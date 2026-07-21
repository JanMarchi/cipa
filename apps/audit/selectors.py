from django.db.models import Q, QuerySet

from apps.accounts.models import PrivilegedAccessGrant, Role, User, UserMembership
from apps.audit.models import AuditEvent
from apps.tenants.models import Tenant


def audit_events_for_user(*, actor: User, tenant: Tenant) -> QuerySet[AuditEvent]:
    events = AuditEvent.objects.filter(tenant=tenant)
    if PrivilegedAccessGrant.objects.active().filter(user=actor, tenant=tenant).exists():
        return events
    memberships = UserMembership.objects.filter(user=actor, tenant=tenant, is_active=True)
    if memberships.filter(role__code=Role.Code.READONLY_AUDITOR).exists():
        return events
    organization_ids = memberships.filter(role__code=Role.Code.CONSULTANCY_ADMIN).values_list(
        "organization_id", flat=True
    )
    company_ids = memberships.filter(role__code=Role.Code.COMPANY_ADMIN).values_list(
        "company_id", flat=True
    )
    establishment_ids = memberships.filter(role__code=Role.Code.SST_RESPONSIBLE).values_list(
        "establishment_id", flat=True
    )
    return events.filter(
        Q(organization_id__in=organization_ids)
        | Q(company__organization_id__in=organization_ids)
        | Q(company_id__in=company_ids)
        | Q(establishment__company_id__in=company_ids)
        | Q(establishment_id__in=establishment_ids)
        | Q(actor=actor)
    ).distinct()
