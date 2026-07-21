from django.db.models import Q, QuerySet

from apps.accounts.models import PrivilegedAccessGrant, Role, User, UserMembership
from apps.tenants.models import Tenant


def memberships_for_user(*, actor: User, tenant: Tenant) -> QuerySet[UserMembership]:
    memberships = UserMembership.objects.filter(tenant=tenant).select_related(
        "user", "role", "organization", "company", "establishment"
    )
    if PrivilegedAccessGrant.objects.active().filter(user=actor, tenant=tenant).exists():
        return memberships
    actor_memberships = UserMembership.objects.filter(user=actor, tenant=tenant, is_active=True)
    if actor_memberships.filter(
        role__code__in=(Role.Code.CONSULTANCY_ADMIN, Role.Code.READONLY_AUDITOR)
    ).exists():
        return memberships
    company_ids = actor_memberships.filter(role__code=Role.Code.COMPANY_ADMIN).values_list(
        "company_id", flat=True
    )
    establishment_ids = actor_memberships.filter(role__code=Role.Code.SST_RESPONSIBLE).values_list(
        "establishment_id", flat=True
    )
    return memberships.filter(
        Q(company_id__in=company_ids)
        | Q(establishment__company_id__in=company_ids)
        | Q(establishment_id__in=establishment_ids)
        | Q(user=actor)
    ).distinct()
