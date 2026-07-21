from django.db import transaction

from apps.accounts.models import User
from apps.audit.services import record_event
from apps.establishments.models import Establishment
from apps.tenants.models import Tenant


@transaction.atomic
def create_establishment(*, tenant: Tenant, actor: User, **data: object) -> Establishment:
    establishment = Establishment(tenant=tenant, **data)
    establishment.full_clean()
    establishment.save()
    record_event(
        event_type="ESTABLISHMENT_CREATED",
        tenant=tenant,
        actor=actor,
        organization=establishment.company.organization,
        company=establishment.company,
        establishment=establishment,
    )
    return establishment
