from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import UUIDTimeStampedModel


class AuditChainHead(UUIDTimeStampedModel):
    scope_key = models.CharField(max_length=64, unique=True)
    tenant = models.OneToOneField(
        "tenants.Tenant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="audit_chain_head",
    )
    current_hash = models.CharField(max_length=64, blank=True)
    sequence = models.PositiveBigIntegerField(default=0)


class AuditEvent(UUIDTimeStampedModel):
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.PROTECT, null=True, blank=True
    )
    company = models.ForeignKey(
        "organizations.Company", on_delete=models.PROTECT, null=True, blank=True
    )
    establishment = models.ForeignKey(
        "establishments.Establishment", on_delete=models.PROTECT, null=True, blank=True
    )
    actor = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_events",
    )
    event_type = models.CharField(max_length=64)
    sequence = models.PositiveBigIntegerField()
    occurred_at = models.DateTimeField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    justification = models.TextField(blank=True, max_length=2000)
    previous_hash = models.CharField(max_length=64, blank=True)
    current_hash = models.CharField(max_length=64, unique=True)

    class Meta:
        ordering = ("-occurred_at", "-sequence")
        constraints = [
            models.UniqueConstraint(
                fields=("tenant", "sequence"), name="audit_tenant_sequence_unique"
            )
        ]
        indexes = [
            models.Index(
                fields=("tenant", "event_type", "occurred_at"), name="audit_event_lookup_idx"
            ),
            models.Index(fields=("actor", "occurred_at"), name="audit_actor_time_idx"),
        ]

    def save(self, *args: object, **kwargs: object) -> None:
        if not self._state.adding:
            raise ValidationError("Eventos de auditoria são imutáveis.")
        super().save(*args, **kwargs)

    def delete(self, *args: object, **kwargs: object) -> tuple[int, dict[str, int]]:
        raise ValidationError("Eventos de auditoria não podem ser excluídos.")
