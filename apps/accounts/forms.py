from django import forms
from django.contrib.auth import password_validation

from apps.accounts.models import Role, User
from apps.establishments.models import Establishment
from apps.establishments.selectors import establishments_for_user
from apps.organizations.models import Company, Organization
from apps.organizations.selectors import companies_for_user, organizations_for_user
from apps.tenants.models import Tenant


class AcceptInvitationForm(forms.Form):
    password1 = forms.CharField(
        label="Senha", widget=forms.PasswordInput(attrs={"autocomplete": "new-password"})
    )
    password2 = forms.CharField(
        label="Confirme a senha", widget=forms.PasswordInput(attrs={"autocomplete": "new-password"})
    )

    def clean_password1(self) -> str:
        password = self.cleaned_data["password1"]
        password_validation.validate_password(password)
        return password

    def clean(self) -> dict[str, object]:
        cleaned = super().clean()
        if cleaned.get("password1") and cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "As senhas não coincidem.")
        return cleaned


class InvitationForm(forms.Form):
    email = forms.EmailField(label="E-mail")
    full_name = forms.CharField(label="Nome completo", max_length=180)
    role = forms.ModelChoiceField(label="Papel", queryset=Role.objects.none())
    organization = forms.ModelChoiceField(
        label="Organização", queryset=Organization.objects.none(), required=False
    )
    company = forms.ModelChoiceField(
        label="Empresa", queryset=Company.objects.none(), required=False
    )
    establishment = forms.ModelChoiceField(
        label="Estabelecimento", queryset=Establishment.objects.none(), required=False
    )

    def __init__(self, *args: object, tenant: Tenant, actor: User, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        actor_codes = set(
            actor.memberships.filter(tenant=tenant, is_active=True).values_list(
                "role__code", flat=True
            )
        )
        allowed: set[Role.Code] = set()
        if Role.Code.COMPANY_ADMIN in actor_codes:
            allowed |= {Role.Code.COMPANY_ADMIN, Role.Code.SST_RESPONSIBLE}
        if Role.Code.CONSULTANCY_ADMIN in actor_codes:
            allowed |= {
                Role.Code.CONSULTANCY_ADMIN,
                Role.Code.COMPANY_ADMIN,
                Role.Code.SST_RESPONSIBLE,
                Role.Code.READONLY_AUDITOR,
            }
        self.fields["role"].queryset = Role.objects.filter(code__in=allowed).order_by("name")
        self.fields["organization"].queryset = organizations_for_user(actor=actor, tenant=tenant)
        self.fields["company"].queryset = companies_for_user(actor=actor, tenant=tenant)
        self.fields["establishment"].queryset = establishments_for_user(actor=actor, tenant=tenant)

    def clean(self) -> dict[str, object]:
        cleaned = super().clean() or {}
        role = cleaned.get("role")
        if not isinstance(role, Role):
            return cleaned
        required_fields: dict[str, str] = {
            Role.Scope.ORGANIZATION: "organization",
            Role.Scope.COMPANY: "company",
            Role.Scope.ESTABLISHMENT: "establishment",
        }
        required_field = required_fields.get(role.scope_type)
        if required_field and not cleaned.get(required_field):
            self.add_error(required_field, "Informe o escopo exigido pelo papel.")
        for field in ("organization", "company", "establishment"):
            if field != required_field:
                cleaned[field] = None
        return cleaned
