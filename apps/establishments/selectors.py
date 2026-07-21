from django.db.models import Q, QuerySet

from apps.accounts.models import PrivilegedAccessGrant, Role, User, UserMembership
from apps.establishments.models import Establishment
from apps.tenants.models import Tenant


def establishments_for_user(*, actor: User, tenant: Tenant) -> QuerySet[Establishment]:
    if PrivilegedAccessGrant.objects.active().filter(user=actor, tenant=tenant).exists():
        return Establishment.objects.filter(tenant=tenant)
    memberships = UserMembership.objects.filter(user=actor, tenant=tenant, is_active=True)
    if memberships.filter(role__code=Role.Code.READONLY_AUDITOR).exists():
        return Establishment.objects.filter(tenant=tenant)
    organization_ids = memberships.filter(role__code=Role.Code.CONSULTANCY_ADMIN).values_list(
        "organization_id", flat=True
    )
    company_ids = memberships.filter(role__code=Role.Code.COMPANY_ADMIN).values_list(
        "company_id", flat=True
    )
    establishment_ids = memberships.filter(role__code=Role.Code.SST_RESPONSIBLE).values_list(
        "establishment_id", flat=True
    )
    return (
        Establishment.objects.filter(tenant=tenant)
        .filter(
            Q(company__organization_id__in=organization_ids)
            | Q(company_id__in=company_ids)
            | Q(id__in=establishment_ids)
        )
        .distinct()
    )
