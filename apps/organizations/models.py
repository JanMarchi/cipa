from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.core.validators import digits_only, validate_cnpj
from apps.tenants.models import TenantOwnedModel


class Organization(TenantOwnedModel):
    class Kind(models.TextChoices):
        DIRECT_COMPANY = "DIRECT_COMPANY", "Empresa direta"
        CONSULTANCY = "CONSULTANCY", "Consultoria"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Ativa"
        INACTIVE = "INACTIVE", "Inativa"

    name = models.CharField("nome", max_length=180)
    kind = models.CharField("tipo", max_length=20, choices=Kind.choices)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("tenant", "name"), name="organization_tenant_name_unique"
            )
        ]
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Company(TenantOwnedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Ativa"
        INACTIVE = "INACTIVE", "Inativa"
        SUSPENDED = "SUSPENDED", "Suspensa"

    organization = models.ForeignKey(
        Organization, on_delete=models.PROTECT, related_name="companies"
    )
    corporate_name = models.CharField("razão social", max_length=200)
    trade_name = models.CharField("nome fantasia", max_length=180, blank=True)
    cnpj = models.CharField("CNPJ", max_length=14, blank=True, validators=[validate_cnpj])
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("tenant", "cnpj"), condition=~Q(cnpj=""), name="company_tenant_cnpj_unique"
            ),
        ]
        indexes = [models.Index(fields=("tenant", "status"), name="company_tenant_status_idx")]
        ordering = ("corporate_name",)

    def clean(self) -> None:
        if self.organization_id and self.organization.tenant_id != self.tenant_id:
            raise ValidationError({"organization": "A organização pertence a outro tenant."})

    def save(self, *args: object, **kwargs: object) -> None:
        self.cnpj = digits_only(self.cnpj)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.trade_name or self.corporate_name
