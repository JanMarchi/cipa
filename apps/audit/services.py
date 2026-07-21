import hashlib
import json
from contextlib import suppress
from typing import Any

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.audit.models import AuditChainHead, AuditEvent
from apps.establishments.models import Establishment
from apps.organizations.models import Company, Organization
from apps.tenants.models import Tenant

FORBIDDEN_METADATA_KEYS = {
    "password",
    "token",
    "credential",
    "choice",
    "candidate",
    "ballot",
    "vote",
}


def _safe_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    cleaned = metadata or {}
    for key in cleaned:
        lowered = key.lower()
        if any(forbidden in lowered for forbidden in FORBIDDEN_METADATA_KEYS):
            raise ValueError(f"Campo proibido em metadata de auditoria: {key}")
    json.dumps(cleaned)
    return cleaned


def _event_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


@transaction.atomic
def record_event(
    *,
    event_type: str,
    tenant: Tenant | None = None,
    actor: User | None = None,
    organization: Organization | None = None,
    company: Company | None = None,
    establishment: Establishment | None = None,
    metadata: dict[str, Any] | None = None,
    justification: str = "",
    ip_address: str | None = None,
    user_agent: str = "",
) -> AuditEvent:
    safe_metadata = _safe_metadata(metadata)
    scope_key = str(getattr(tenant, "id", "platform"))
    with suppress(IntegrityError):
        AuditChainHead.objects.get_or_create(scope_key=scope_key, defaults={"tenant": tenant})
    head = AuditChainHead.objects.select_for_update().get(scope_key=scope_key)
    event = AuditEvent(
        tenant=tenant,
        organization=organization,
        company=company,
        establishment=establishment,
        actor=actor,
        event_type=event_type,
        sequence=head.sequence + 1,
        occurred_at=timezone.now(),
        ip_address=ip_address,
        user_agent=user_agent[:255],
        metadata=safe_metadata,
        justification=justification,
        previous_hash=head.current_hash,
    )
    payload = {
        "id": str(event.id),
        "scope": scope_key,
        "event_type": event.event_type,
        "sequence": event.sequence,
        "occurred_at": event.occurred_at.isoformat(),
        "actor_id": str(getattr(actor, "id", "")),
        "organization_id": str(getattr(organization, "id", "")),
        "company_id": str(getattr(company, "id", "")),
        "establishment_id": str(getattr(establishment, "id", "")),
        "metadata": safe_metadata,
        "justification": justification,
        "previous_hash": head.current_hash,
    }
    event.current_hash = _event_hash(payload)
    event.save(force_insert=True)
    head.current_hash = event.current_hash
    head.sequence = event.sequence
    head.save(update_fields=("current_hash", "sequence", "updated_at"))
    return event


def verify_chain(*, tenant: Tenant | None = None) -> list[str]:
    scope_key = str(getattr(tenant, "id", "platform"))
    previous_hash = ""
    errors: list[str] = []
    events = AuditEvent.objects.filter(tenant=tenant).order_by("sequence")
    for event in events:
        payload = {
            "id": str(event.id),
            "scope": scope_key,
            "event_type": event.event_type,
            "sequence": event.sequence,
            "occurred_at": event.occurred_at.isoformat(),
            "actor_id": str(event.actor_id or ""),
            "organization_id": str(event.organization_id or ""),
            "company_id": str(event.company_id or ""),
            "establishment_id": str(event.establishment_id or ""),
            "metadata": event.metadata,
            "justification": event.justification,
            "previous_hash": previous_hash,
        }
        expected = _event_hash(payload)
        if event.previous_hash != previous_hash or event.current_hash != expected:
            errors.append(str(event.id))
        previous_hash = event.current_hash
    return errors
