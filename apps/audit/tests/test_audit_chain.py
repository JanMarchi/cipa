import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import DatabaseError, connection, transaction
from django.urls import reverse

from apps.audit.models import AuditEvent
from apps.audit.services import record_event, verify_chain


@pytest.mark.django_db
def test_audit_chain_is_linked_and_valid(tenant, user) -> None:
    first = record_event(event_type="TENANT_CREATED", tenant=tenant, actor=user)
    second = record_event(
        event_type="COMPANY_CREATED", tenant=tenant, actor=user, metadata={"status": "ACTIVE"}
    )
    assert first.sequence == 1
    assert second.previous_hash == first.current_hash
    assert verify_chain(tenant=tenant) == []


@pytest.mark.django_db
def test_audit_event_rejects_update_and_delete(tenant, user) -> None:
    event = record_event(event_type="TENANT_CREATED", tenant=tenant, actor=user)
    event.event_type = "TAMPERED"
    with pytest.raises(ValidationError):
        event.save()
    with pytest.raises(ValidationError):
        event.delete()


@pytest.mark.django_db
def test_audit_detects_manual_tampering(tenant, user) -> None:
    event = record_event(event_type="TENANT_CREATED", tenant=tenant, actor=user)
    if connection.vendor == "postgresql":
        with pytest.raises(DatabaseError), transaction.atomic():
            AuditEvent.objects.filter(id=event.id).update(event_type="TAMPERED")
        return
    AuditEvent.objects.filter(id=event.id).update(event_type="TAMPERED")
    assert verify_chain(tenant=tenant) == [str(event.id)]


@pytest.mark.django_db
def test_sensitive_metadata_is_rejected(tenant) -> None:
    with pytest.raises(ValueError):
        record_event(event_type="TEST", tenant=tenant, metadata={"voting_token": "secret"})


@pytest.mark.django_db
def test_verify_command_and_audit_view(authenticated_client, tenant, user) -> None:
    record_event(event_type="TENANT_CREATED", tenant=tenant, actor=user)
    call_command("verify_audit_chain")
    response = authenticated_client.get(reverse("audit-event-list"))
    assert response.status_code == 200
    assert "TENANT_CREATED" in response.content.decode()
