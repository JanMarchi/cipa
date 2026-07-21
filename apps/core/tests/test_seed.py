import pytest
from django.core.management import call_command

from apps.accounts.models import User
from apps.audit.models import AuditEvent
from apps.establishments.models import Establishment
from apps.organizations.models import Company
from apps.tenants.models import Tenant


@pytest.mark.django_db
def test_seed_demo_is_idempotent() -> None:
    call_command("seed_demo")
    call_command("seed_demo")
    assert Tenant.objects.filter(slug="consultoria-demo").count() == 1
    assert Company.objects.count() == 2
    assert Establishment.objects.count() == 3
    assert User.objects.filter(email__endswith="@example.invalid").count() == 3
    assert AuditEvent.objects.filter(event_type="TENANT_CREATED").count() == 1
