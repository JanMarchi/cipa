from uuid import UUID

from django.db import connection

from apps.accounts.models import PrivilegedAccessGrant, User, UserMembership
from apps.tenants.models import Tenant


def user_can_access_tenant(*, user: User, tenant_id: UUID) -> bool:
    if not user.is_active:
        return False
    if connection.vendor == "postgresql":
        with connection.cursor() as cursor:
            cursor.execute("SELECT cipa_has_tenant_access(%s, %s)", [str(user.id), str(tenant_id)])
            row = cursor.fetchone()
            return bool(row and row[0])
    return (
        UserMembership.objects.filter(user=user, tenant_id=tenant_id, is_active=True).exists()
        or PrivilegedAccessGrant.objects.active().filter(user=user, tenant_id=tenant_id).exists()
    )


def accessible_tenants(user: User) -> list[Tenant]:
    tenant_ids = set(
        UserMembership.objects.filter(
            user=user, is_active=True, tenant__status=Tenant.Status.ACTIVE
        ).values_list("tenant_id", flat=True)
    )
    tenant_ids.update(
        PrivilegedAccessGrant.objects.active().filter(user=user).values_list("tenant_id", flat=True)
    )
    return list(Tenant.objects.filter(id__in=tenant_ids).order_by("name"))
