from django.db import models

from apps.core.models import UUIDTimeStampedModel


class Tenant(UUIDTimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Ativo"
        SUSPENDED = "SUSPENDED", "Suspenso"
        CLOSED = "CLOSED", "Encerrado"

    name = models.CharField("nome", max_length=180)
    slug = models.SlugField("identificador", max_length=80, unique=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ("name",)
        verbose_name = "tenant"
        verbose_name_plural = "tenants"

    def __str__(self) -> str:
        return self.name


class TenantOwnedModel(UUIDTimeStampedModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)

    class Meta:
        abstract = True
