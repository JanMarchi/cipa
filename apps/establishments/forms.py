from django import forms

from apps.accounts.models import User
from apps.establishments.models import Establishment
from apps.organizations.models import Company
from apps.organizations.selectors import companies_for_user
from apps.tenants.models import Tenant


class EstablishmentForm(forms.ModelForm):
    class Meta:
        model = Establishment
        fields = (
            "company",
            "name",
            "registration_id",
            "cnae",
            "risk_degree",
            "employee_count",
            "address_line",
            "city",
            "state",
            "postal_code",
            "predominant_union",
            "responsible_email",
            "status",
        )

    def __init__(self, *args: object, tenant: Tenant, actor: User, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.instance.tenant = tenant
        self.fields["company"].queryset = companies_for_user(actor=actor, tenant=tenant).filter(
            status=Company.Status.ACTIVE
        )
