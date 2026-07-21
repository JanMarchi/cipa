from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.accounts.forms import AcceptInvitationForm, InvitationForm
from apps.accounts.policies import authorize
from apps.accounts.selectors import memberships_for_user
from apps.accounts.services import accept_invitation, invite_user


@require_http_methods(["GET", "POST"])
def accept_invitation_view(request: HttpRequest, token: str) -> HttpResponse:
    form = AcceptInvitationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            user = accept_invitation(token=token, password=form.cleaned_data["password1"])
        except ValueError:
            messages.error(request, "O convite é inválido, expirou ou já foi utilizado.")
        else:
            login(request, user, backend="allauth.account.auth_backends.AuthenticationBackend")
            messages.success(
                request, "Conta ativada. Configure agora o segundo fator de autenticação."
            )
            return redirect("mfa_activate_totp")
    return render(request, "accounts/invitation_accept.html", {"form": form})


@require_http_methods(["GET", "POST"])
def user_list(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("account_login")
    tenant = getattr(request, "tenant", None)
    if tenant is None:
        return redirect("tenant-select")
    authorize(actor=request.user, action="list", tenant=tenant)
    form = InvitationForm(request.POST or None, tenant=tenant, actor=request.user)
    if request.method == "POST" and form.is_valid():
        authorize(actor=request.user, action="user.invite", tenant=tenant)
        invite_user(
            tenant=tenant,
            invited_by=request.user,
            base_url=request.build_absolute_uri("/").rstrip("/"),
            **form.cleaned_data,
        )
        messages.success(request, "Convite enviado com validade de 48 horas.")
        return redirect("user-list")
    memberships = memberships_for_user(actor=request.user, tenant=tenant)
    return render(
        request,
        "accounts/user_list.html",
        {"memberships": memberships, "form": form},
    )
