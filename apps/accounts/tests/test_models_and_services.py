from datetime import timedelta

import pytest
from allauth.account.models import EmailAddress
from django.core import mail
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from apps.accounts.adapters import EncryptedMFAAdapter, InviteOnlyAccountAdapter
from apps.accounts.models import (
    AccountInvitation,
    PrivilegedAccessGrant,
    Role,
    User,
    UserMembership,
)
from apps.accounts.services import (
    accept_invitation,
    grant_privileged_access,
    invite_user,
    revoke_sessions,
)
from apps.audit.models import AuditEvent


@pytest.mark.django_db
def test_email_is_normalized_and_case_insensitive(user: User) -> None:
    assert user.email == "admin@example.invalid"
    with pytest.raises(IntegrityError):
        User.objects.create_user(
            email="ADMIN@example.invalid", password="Outra senha forte 123!", full_name="Duplicado"
        )


@pytest.mark.django_db
def test_invitation_stores_only_digest_and_accepts_once(
    user, tenant, organization, admin_role, django_capture_on_commit_callbacks
) -> None:
    with django_capture_on_commit_callbacks(execute=True):
        invitation = invite_user(
            email="novo@example.invalid",
            full_name="Novo Usuário",
            role=admin_role,
            invited_by=user,
            tenant=tenant,
            organization=organization,
            base_url="https://example.invalid",
        )
    assert len(invitation.token_digest) == 64
    assert "novo@example.invalid" in mail.outbox[0].to
    token = mail.outbox[0].body.split("/convites/")[1].split("/")[0]
    assert token not in invitation.token_digest
    invited = accept_invitation(token=token, password="Convite com senha muito forte 123!")
    assert invited.check_password("Convite com senha muito forte 123!")
    assert EmailAddress.objects.get(user=invited).verified
    assert UserMembership.objects.filter(user=invited, tenant=tenant, role=admin_role).exists()
    with pytest.raises(ValueError):
        accept_invitation(token=token, password="Convite com senha muito forte 123!")


@pytest.mark.django_db
def test_expired_invitation_is_not_usable(user, tenant, organization, admin_role) -> None:
    token, digest = AccountInvitation.new_token()
    invitation = AccountInvitation.objects.create(
        email="expired@example.invalid",
        full_name="Expirado",
        role=admin_role,
        tenant=tenant,
        organization=organization,
        invited_by=user,
        token_digest=digest,
        expires_at=timezone.now() - timedelta(seconds=1),
    )
    assert not invitation.is_usable()
    with pytest.raises(ValueError):
        accept_invitation(token=token, password="Senha forte que não será usada 123!")


@pytest.mark.django_db
def test_privileged_grant_validates_duration(user, tenant) -> None:
    grant = PrivilegedAccessGrant(
        user=user,
        tenant=tenant,
        granted_by=user,
        starts_at=timezone.now(),
        expires_at=timezone.now() + timedelta(hours=9),
        justification="Diagnóstico autorizado",
    )
    with pytest.raises(ValidationError):
        grant.full_clean()


def test_mfa_adapter_encrypts_without_plaintext(settings) -> None:
    adapter = EncryptedMFAAdapter()
    encrypted = adapter.encrypt("segredo-totp")
    assert encrypted != "segredo-totp"
    assert adapter.decrypt(encrypted) == "segredo-totp"


def test_public_signup_is_closed() -> None:
    assert InviteOnlyAccountAdapter().is_open_for_signup(object()) is False


@pytest.mark.django_db
def test_revoke_sessions_without_active_sessions(user) -> None:
    assert revoke_sessions(user=user) == 0


@pytest.mark.django_db
def test_invitation_rejects_sensitive_audit_metadata(
    user, tenant, organization, admin_role
) -> None:
    invite_user(
        email="seguro@example.invalid",
        full_name="Seguro",
        role=admin_role,
        invited_by=user,
        tenant=tenant,
        organization=organization,
    )
    assert not AuditEvent.objects.filter(metadata__has_key="token").exists()  # noqa: S105


@pytest.mark.django_db
def test_platform_admin_can_issue_audited_temporary_grant(user, tenant) -> None:
    platform_role = Role.objects.get(code=Role.Code.PLATFORM_ADMIN)
    support_role = Role.objects.get(code=Role.Code.RESTRICTED_SUPPORT)
    UserMembership.objects.create(user=user, role=platform_role)
    support = User.objects.create_user(
        email="support@example.invalid", full_name="Suporte", password=None
    )
    UserMembership.objects.create(user=support, role=support_role)
    grant = grant_privileged_access(
        user=support,
        tenant=tenant,
        granted_by=user,
        justification="Diagnóstico autorizado pelo cliente",
        expires_at=timezone.now() + timedelta(hours=1),
    )
    assert grant.is_active
    assert AuditEvent.objects.filter(event_type="PRIVILEGED_ACCESS_GRANTED").exists()
