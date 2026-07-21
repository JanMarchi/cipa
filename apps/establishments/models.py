from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.core.validators import digits_only, validate_cnpj
from apps.organizations.models import Company
from apps.tenants.models import TenantOwnedModel


class Establishment(TenantOwnedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Ativo"
        INACTIVE = "INACTIVE", "Inativo"

    company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name="establishments")
    name = models.CharField("nome", max_length=180)
    registration_id = models.CharField("CNPJ ou identificação", max_length=32, blank=True)
    cnae = models.CharField("CNAE", max_length=16, blank=True)
    risk_degree = models.PositiveSmallIntegerField(
        "grau de risco", choices=((1, "1"), (2, "2"), (3, "3"), (4, "4")), null=True, blank=True
    )
    employee_count = models.PositiveIntegerField("quantidade de empregados", default=0)
    address_line = models.CharField("endereço", max_length=255, blank=True)
    city = models.CharField("cidade", max_length=100, blank=True)
    state = models.CharField("UF", max_length=2, blank=True)
    postal_code = models.CharField("CEP", max_length=9, blank=True)
    predominant_union = models.CharField("sindicato predominante", max_length=180, blank=True)
    responsible_email = models.EmailField("e-mail do responsável", blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("company", "name"), name="establishment_company_name_unique"
            ),
            models.UniqueConstraint(
                fields=("tenant", "registration_id"),
                condition=~Q(registration_id=""),
                name="establishment_tenant_reg_unique",
            ),
        ]
        indexes = [models.Index(fields=("tenant", "status"), name="est_tenant_status_idx")]
        ordering = ("company__corporate_name", "name")

    def clean(self) -> None:
        errors: dict[str, str] = {}
        if self.company_id and self.company.tenant_id != self.tenant_id:
            errors["company"] = "A empresa pertence a outro tenant."
        registration_digits = digits_only(self.registration_id)
        if len(registration_digits) == 14:
            try:
                validate_cnpj(registration_digits)
            except ValidationError as exc:
                errors["registration_id"] = exc.messages[0]
        if self.state and (len(self.state) != 2 or not self.state.isalpha()):
            errors["state"] = "Informe a UF com duas letras."
        if errors:
            raise ValidationError(errors)

    def save(self, *args: object, **kwargs: object) -> None:
        self.state = self.state.upper()
        self.postal_code = digits_only(self.postal_code)
        if len(digits_only(self.registration_id)) == 14:
            self.registration_id = digits_only(self.registration_id)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.company} — {self.name}"
