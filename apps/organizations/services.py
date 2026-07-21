from django.db import transaction

from apps.accounts.models import User
from apps.audit.services import record_event
from apps.organizations.models import Company
from apps.tenants.models import Tenant


@transaction.atomic
def create_company(*, tenant: Tenant, actor: User, **data: object) -> Company:
    company = Company(tenant=tenant, **data)
    company.full_clean()
    company.save()
    record_event(
        event_type="COMPANY_CREATED",
        tenant=tenant,
        actor=actor,
        organization=company.organization,
        company=company,
    )
    return company
