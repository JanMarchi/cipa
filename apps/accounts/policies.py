from django.core.exceptions import PermissionDenied
from django.db.models import Q

from apps.accounts.models import PrivilegedAccessGrant, Role, User, UserMembership
from apps.tenants.models import Tenant

READ_ACTIONS = {"view", "list", "audit.view"}
WRITE_ROLES = {
    Role.Code.CONSULTANCY_ADMIN,
    Role.Code.COMPANY_ADMIN,
    Role.Code.SST_RESPONSIBLE,
}
READ_ROLES = WRITE_ROLES | {Role.Code.READONLY_AUDITOR}
WRITE_ACTION_ROLES = {
    "company.create": {Role.Code.CONSULTANCY_ADMIN},
    "establishment.create": {Role.Code.CONSULTANCY_ADMIN, Role.Code.COMPANY_ADMIN},
    "user.invite": {Role.Code.CONSULTANCY_ADMIN, Role.Code.COMPANY_ADMIN},
}


def authorize(
    *,
    actor: User,
    action: str,
    tenant: Tenant,
    company_id: object | None = None,
    establishment_id: object | None = None,
) -> None:
    if not actor.is_active:
        raise PermissionDenied
    if PrivilegedAccessGrant.objects.active().filter(user=actor, tenant=tenant).exists():
        return
    memberships = UserMembership.objects.filter(user=actor, tenant=tenant, is_active=True).filter(
        Q(ends_at__isnull=True) | Q(ends_at__gt=timezone.now())
    )
    if company_id is not None:
        memberships = memberships.filter(Q(company_id=company_id) | Q(company__isnull=True))
    if establishment_id is not None:
        memberships = memberships.filter(
            Q(establishment_id=establishment_id) | Q(establishment__isnull=True)
        )
    codes = set(memberships.values_list("role__code", flat=True))
    allowed_roles = READ_ROLES if action in READ_ACTIONS else WRITE_ACTION_ROLES.get(action, set())
    if codes & allowed_roles:
        return
    raise PermissionDenied


from django.utils import timezone  # noqa: E402
