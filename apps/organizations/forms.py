from django import forms

from apps.accounts.models import User
from apps.organizations.models import Company, Organization
from apps.organizations.selectors import organizations_for_user
from apps.tenants.models import Tenant


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ("organization", "corporate_name", "trade_name", "cnpj", "status")

    def __init__(self, *args: object, tenant: Tenant, actor: User, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.instance.tenant = tenant
        self.fields["organization"].queryset = organizations_for_user(
            actor=actor, tenant=tenant
        ).filter(status=Organization.Status.ACTIVE)
