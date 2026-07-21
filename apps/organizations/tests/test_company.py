import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.accounts.models import Role, User, UserMembership
from apps.audit.models import AuditEvent
from apps.organizations.models import Company, Organization
from apps.organizations.selectors import companies_for_user


@pytest.mark.django_db
def test_company_rejects_organization_from_other_tenant(tenant, other_tenant) -> None:
    organization = Organization.objects.create(
        tenant=other_tenant, name="Outra", kind=Organization.Kind.CONSULTANCY
    )
    company = Company(tenant=tenant, organization=organization, corporate_name="Inválida")
    with pytest.raises(ValidationError):
        company.full_clean()


@pytest.mark.django_db
def test_company_list_filters_current_tenant(authenticated_client, company, other_tenant) -> None:
    other_org = Organization.objects.create(
        tenant=other_tenant, name="Outra", kind=Organization.Kind.CONSULTANCY
    )
    Company.objects.create(
        tenant=other_tenant, organization=other_org, corporate_name="Empresa Secreta"
    )
    response = authenticated_client.get(reverse("company-list"))
    content = response.content.decode()
    assert response.status_code == 200
    assert "Empresa A Ltda." in content
    assert "Empresa Secreta" not in content


@pytest.mark.django_db
def test_company_create_uses_service_and_audits(authenticated_client, tenant, organization) -> None:
    response = authenticated_client.post(
        reverse("company-create"),
        {
            "organization": str(organization.id),
            "corporate_name": "Nova Empresa Ltda.",
            "trade_name": "Nova",
            "cnpj": "12345678000195",
            "status": Company.Status.ACTIVE,
        },
    )
    assert response.status_code == 302
    company = Company.objects.get(corporate_name="Nova Empresa Ltda.")
    assert company.tenant == tenant
    assert AuditEvent.objects.filter(
        tenant=tenant, company=company, event_type="COMPANY_CREATED"
    ).exists()


@pytest.mark.django_db
def test_company_selector_respects_company_scope(tenant, organization, company) -> None:
    other_company = Company.objects.create(
        tenant=tenant,
        organization=organization,
        corporate_name="Empresa do Mesmo Tenant Ltda.",
    )
    scoped_user = User.objects.create_user(
        email="company-scope@example.invalid", full_name="Escopo Empresa", password=None
    )
    role = Role.objects.get(code=Role.Code.COMPANY_ADMIN)
    UserMembership.objects.create(user=scoped_user, tenant=tenant, company=company, role=role)
    assert list(companies_for_user(actor=scoped_user, tenant=tenant)) == [company]
    assert other_company not in companies_for_user(actor=scoped_user, tenant=tenant)
