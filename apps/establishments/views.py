from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.accounts.policies import authorize
from apps.establishments.forms import EstablishmentForm
from apps.establishments.selectors import establishments_for_user
from apps.establishments.services import create_establishment


@login_required
def establishment_list(request: HttpRequest) -> HttpResponse:
    tenant = getattr(request, "tenant", None)
    if tenant is None:
        return redirect("tenant-select")
    authorize(actor=request.user, action="list", tenant=tenant)
    establishments = establishments_for_user(actor=request.user, tenant=tenant).select_related(
        "company"
    )
    return render(
        request, "establishments/establishment_list.html", {"establishments": establishments}
    )


@login_required
@require_http_methods(["GET", "POST"])
def establishment_create(request: HttpRequest) -> HttpResponse:
    tenant = getattr(request, "tenant", None)
    if tenant is None:
        return redirect("tenant-select")
    authorize(actor=request.user, action="establishment.create", tenant=tenant)
    form = EstablishmentForm(request.POST or None, tenant=tenant, actor=request.user)
    if request.method == "POST" and form.is_valid():
        authorize(
            actor=request.user,
            action="establishment.create",
            tenant=tenant,
            company_id=form.cleaned_data["company"].id,
        )
        create_establishment(tenant=tenant, actor=request.user, **form.cleaned_data)
        messages.success(request, "Estabelecimento cadastrado.")
        return redirect("establishment-list")
    return render(request, "establishments/establishment_form.html", {"form": form})
