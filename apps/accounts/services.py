from datetime import datetime, timedelta

from allauth.account.models import EmailAddress
from django.contrib.sessions.models import Session
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.mail import send_mail
from django.db import connection, transaction
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import (
    AccountInvitation,
    PrivilegedAccessGrant,
    Role,
    User,
    UserMembership,
    UserSession,
)
from apps.audit.services import record_event
from apps.establishments.models import Establishment
from apps.organizations.models import Company, Organization
from apps.tenants.context import set_database_context
from apps.tenants.models import Tenant


@transaction.atomic
def invite_user(
    *,
    email: str,
    full_name: str,
    role: Role,
    invited_by: User,
    tenant: Tenant | None = None,
    organization: Organization | None = None,
    company: Company | None = None,
    establishment: Establishment | None = None,
    base_url: str = "",
) -> AccountInvitation:
    token, digest = AccountInvitation.new_token()
    invitation = AccountInvitation.objects.create(
        email=email,
        full_name=full_name,
        role=role,
        invited_by=invited_by,
        tenant=tenant,
        organization=organization,
        company=company,
        establishment=establishment,
        token_digest=digest,
        expires_at=timezone.now() + timedelta(hours=48),
    )
    path = reverse("invitation-accept", kwargs={"token": token})
    transaction.on_commit(
        lambda: send_mail(
            "Convite para CIPA Eleitoral",
            "Você recebeu um convite administrativo. "
            f"Acesse {base_url}{path}. O link expira em 48 horas.",
            None,
            [invitation.email],
        )
    )
    record_event(
        event_type="ACCOUNT_INVITATION_ISSUED",
        tenant=tenant,
        actor=invited_by,
        metadata={"role": role.code},
    )
    return invitation


@transaction.atomic
def accept_invitation(*, token: str, password: str) -> User:
    digest = AccountInvitation.digest_token(token)
    if connection.vendor == "postgresql":
        with connection.cursor() as cursor:
            cursor.execute("SELECT cipa_invitation_tenant(%s)", [digest])
            row = cursor.fetchone()
        if row and row[0]:
            set_database_context(tenant_id=row[0], user_id=None)
    invitation = (
        AccountInvitation.objects.select_for_update(of=("self",))
        .select_related("role", "tenant")
        .filter(token_digest=digest)
        .first()
    )
    if invitation is None or not invitation.is_usable():
        raise ValueError("Convite inválido ou expirado.")
    user, created = User.objects.get_or_create(
        email=invitation.email, defaults={"full_name": invitation.full_name, "is_active": True}
    )
    if not created and user.has_usable_password():
        raise ValueError("Este convite não pode mais ser utilizado.")
    user.full_name = invitation.full_name
    user.set_password(password)
    user.save(update_fields=("full_name", "password"))
    EmailAddress.objects.update_or_create(
        user=user, email=user.email, defaults={"verified": True, "primary": True}
    )
    UserMembership.objects.create(
        user=user,
        role=invitation.role,
        tenant=invitation.tenant,
        organization=invitation.organization,
        company=invitation.company,
        establishment=invitation.establishment,
    )
    invitation.accepted_at = timezone.now()
    invitation.save(update_fields=("accepted_at", "updated_at"))
    record_event(
        event_type="ACCOUNT_INVITATION_ACCEPTED",
        tenant=invitation.tenant,
        actor=user,
        metadata={"role": invitation.role.code},
    )
    return user


@transaction.atomic
def revoke_sessions(*, user: User, except_session_key: str | None = None) -> int:
    sessions = UserSession.objects.filter(user=user, revoked_at__isnull=True)
    if except_session_key:
        sessions = sessions.exclude(session_key=except_session_key)
    keys = list(sessions.values_list("session_key", flat=True))
    count = sessions.update(revoked_at=timezone.now())
    Session.objects.filter(session_key__in=keys).delete()
    return count


@transaction.atomic
def grant_privileged_access(
    *,
    user: User,
    tenant: Tenant,
    granted_by: User,
    justification: str,
    expires_at: datetime,
) -> PrivilegedAccessGrant:
    if not UserMembership.objects.filter(
        user=granted_by,
        role__code=Role.Code.PLATFORM_ADMIN,
        is_active=True,
    ).exists():
        raise PermissionDenied
    if not UserMembership.objects.filter(
        user=user,
        role__code__in=(Role.Code.PLATFORM_ADMIN, Role.Code.RESTRICTED_SUPPORT),
        is_active=True,
    ).exists():
        raise ValidationError("O acesso privilegiado é exclusivo de plataforma ou suporte.")
    grant = PrivilegedAccessGrant(
        user=user,
        tenant=tenant,
        granted_by=granted_by,
        starts_at=timezone.now(),
        expires_at=expires_at,
        justification=justification,
    )
    grant.full_clean()
    grant.save()
    record_event(
        event_type="PRIVILEGED_ACCESS_GRANTED",
        tenant=None,
        actor=granted_by,
        metadata={
            "target_tenant_id": str(tenant.id),
            "grantee_id": str(user.id),
            "expires_at": expires_at.isoformat(),
        },
        justification=justification,
    )
    return grant
