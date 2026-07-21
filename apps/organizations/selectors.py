from django.db.models import Q, QuerySet

from apps.accounts.models import PrivilegedAccessGrant, Role, User, UserMembership
from apps.organizations.models import Company, Organization
from apps.tenants.models import Tenant


def organizations_for_user(*, actor: User, tenant: Tenant) -> QuerySet[Organization]:
    if PrivilegedAccessGrant.objects.active().filter(user=actor, tenant=tenant).exists():
        return Organization.objects.filter(tenant=tenant)
    memberships = UserMembership.objects.filter(user=actor, tenant=tenant, is_active=True)
    if memberships.filter(role__code=Role.Code.READONLY_AUDITOR).exists():
        return Organization.objects.filter(tenant=tenant)
    organization_ids = memberships.values_list("organization_id", flat=True)
    return Organization.objects.filter(tenant=tenant, id__in=organization_ids)


def companies_for_user(*, actor: User, tenant: Tenant) -> QuerySet[Company]:
    if PrivilegedAccessGrant.objects.active().filter(user=actor, tenant=tenant).exists():
        return Company.objects.filter(tenant=tenant)
    memberships = UserMembership.objects.filter(user=actor, tenant=tenant, is_active=True)
    if memberships.filter(role__code=Role.Code.READONLY_AUDITOR).exists():
        return Company.objects.filter(tenant=tenant)
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
        Company.objects.filter(tenant=tenant)
        .filter(
            Q(organization_id__in=organization_ids)
            | Q(id__in=company_ids)
            | Q(establishments__id__in=establishment_ids)
        )
        .distinct()
    )
