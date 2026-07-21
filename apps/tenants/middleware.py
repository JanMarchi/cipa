from collections.abc import Callable
from uuid import UUID

from django.db import transaction
from django.http import HttpRequest, HttpResponse

from apps.core.context import tenant_id_var, user_id_var
from apps.tenants.context import set_database_context
from apps.tenants.models import Tenant


class TenantContextMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        user_id = request.user.id if request.user.is_authenticated else None
        raw_tenant_id = (
            request.session.get("active_tenant_id") if request.user.is_authenticated else None
        )
        tenant_id: UUID | None = None
        if raw_tenant_id:
            try:
                tenant_id = UUID(raw_tenant_id)
            except (TypeError, ValueError):
                request.session.pop("active_tenant_id", None)

        tenant_token = tenant_id_var.set(str(tenant_id or ""))
        user_token = user_id_var.set(str(user_id or ""))
        try:
            with transaction.atomic():
                set_database_context(tenant_id=tenant_id, user_id=user_id)
                request.tenant = None
                if tenant_id:
                    from apps.tenants.services import user_can_access_tenant

                    if request.user.is_authenticated and user_can_access_tenant(
                        user=request.user, tenant_id=tenant_id
                    ):
                        request.tenant = Tenant.objects.filter(
                            id=tenant_id, status=Tenant.Status.ACTIVE
                        ).first()
                    if request.tenant is None:
                        request.session.pop("active_tenant_id", None)
                        set_database_context(tenant_id=None, user_id=user_id)
                return self.get_response(request)
        finally:
            tenant_id_var.reset(tenant_token)
            user_id_var.reset(user_token)
