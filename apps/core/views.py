from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db import connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render


def live(_: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"})


def ready(_: HttpRequest) -> JsonResponse:
    checks: dict[str, str] = {}
    status = 200
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "unavailable"
        status = 503
    try:
        cache.set("readiness", "ok", timeout=5)
        checks["cache"] = "ok" if cache.get("readiness") == "ok" else "unavailable"
    except Exception:
        checks["cache"] = "unavailable"
        status = 503
    return JsonResponse(
        {"status": "ok" if status == 200 else "degraded", "checks": checks}, status=status
    )


def home(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("tenant-select")
    return render(request, "core/home.html")


@login_required
def dashboard(request: HttpRequest, tenant_slug: str) -> HttpResponse:
    tenant = getattr(request, "tenant", None)
    if tenant is None or tenant.slug != tenant_slug:
        return HttpResponse(status=404)
    from apps.accounts.policies import authorize
    from apps.establishments.selectors import establishments_for_user
    from apps.organizations.selectors import companies_for_user

    authorize(actor=request.user, action="list", tenant=tenant)

    context = {
        "company_count": companies_for_user(actor=request.user, tenant=tenant)
        .filter(status="ACTIVE")
        .count(),
        "establishment_count": establishments_for_user(actor=request.user, tenant=tenant)
        .filter(status="ACTIVE")
        .count(),
    }
    return render(request, "core/dashboard.html", context)
