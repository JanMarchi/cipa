from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.accounts.policies import authorize
from apps.organizations.forms import CompanyForm
from apps.organizations.selectors import companies_for_user
from apps.organizations.services import create_company


@login_required
def company_list(request: HttpRequest) -> HttpResponse:
    tenant = getattr(request, "tenant", None)
    if tenant is None:
        return redirect("tenant-select")
    authorize(actor=request.user, action="list", tenant=tenant)
    companies = companies_for_user(actor=request.user, tenant=tenant).select_related("organization")
    return render(request, "organizations/company_list.html", {"companies": companies})


@login_required
@require_http_methods(["GET", "POST"])
def company_create(request: HttpRequest) -> HttpResponse:
    tenant = getattr(request, "tenant", None)
    if tenant is None:
        return redirect("tenant-select")
    authorize(actor=request.user, action="company.create", tenant=tenant)
    form = CompanyForm(request.POST or None, tenant=tenant, actor=request.user)
    if request.method == "POST" and form.is_valid():
        create_company(tenant=tenant, actor=request.user, **form.cleaned_data)
        messages.success(request, "Empresa cadastrada.")
        return redirect("company-list")
    return render(request, "organizations/company_form.html", {"form": form})
