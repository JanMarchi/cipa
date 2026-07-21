from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.accounts.policies import authorize
from apps.audit.selectors import audit_events_for_user


@login_required
def event_list(request: HttpRequest) -> HttpResponse:
    tenant = getattr(request, "tenant", None)
    if tenant is None:
        return redirect("tenant-select")
    authorize(actor=request.user, action="audit.view", tenant=tenant)
    events = audit_events_for_user(actor=request.user, tenant=tenant).select_related("actor")[:200]
    return render(request, "audit/event_list.html", {"events": events})
