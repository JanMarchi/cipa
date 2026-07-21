from uuid import UUID

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.audit.services import record_event
from apps.tenants.context import set_database_context
from apps.tenants.models import Tenant
from apps.tenants.services import accessible_tenants, user_can_access_tenant


@login_required
@require_http_methods(["GET", "POST"])
def select_tenant(request: HttpRequest) -> HttpResponse:
    tenants = accessible_tenants(request.user)
    if request.method == "POST":
        try:
            tenant_id = UUID(request.POST.get("tenant_id", ""))
        except ValueError:
            messages.error(request, "Selecione um contexto válido.")
        else:
            if user_can_access_tenant(user=request.user, tenant_id=tenant_id):
                tenant = get_object_or_404(Tenant, id=tenant_id, status=Tenant.Status.ACTIVE)
                set_database_context(tenant_id=tenant.id, user_id=request.user.id)
                request.session["active_tenant_id"] = str(tenant.id)
                record_event(
                    event_type="TENANT_CONTEXT_SELECTED", tenant=tenant, actor=request.user
                )
                return redirect("dashboard", tenant_slug=tenant.slug)
            messages.error(request, "Você não possui acesso a esse contexto.")
    return render(request, "tenants/select.html", {"tenants": tenants})
