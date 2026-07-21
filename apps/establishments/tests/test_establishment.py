import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.establishments.models import Establishment


@pytest.mark.django_db
def test_establishment_normalizes_fields(tenant, company) -> None:
    establishment = Establishment(
        tenant=tenant,
        company=company,
        name="Matriz",
        registration_id="UNIDADE-01",
        state="sp",
        postal_code="01000-000",
    )
    establishment.full_clean()
    establishment.save()
    assert establishment.state == "SP"
    assert establishment.postal_code == "01000000"


@pytest.mark.django_db
def test_establishment_rejects_other_tenant(tenant, other_tenant, company) -> None:
    establishment = Establishment(tenant=other_tenant, company=company, name="Inválido")
    with pytest.raises(ValidationError):
        establishment.full_clean()


@pytest.mark.django_db
def test_establishment_create_view(authenticated_client, tenant, company) -> None:
    response = authenticated_client.post(
        reverse("establishment-create"),
        {
            "company": str(company.id),
            "name": "Filial",
            "registration_id": "FILIAL-01",
            "cnae": "",
            "risk_degree": "2",
            "employee_count": "10",
            "address_line": "Rua Exemplo, 1",
            "city": "São Paulo",
            "state": "SP",
            "postal_code": "01000-000",
            "predominant_union": "",
            "responsible_email": "sst@example.invalid",
            "status": Establishment.Status.ACTIVE,
        },
    )
    assert response.status_code == 302
    assert Establishment.objects.filter(
        tenant=tenant, name="Filial", postal_code="01000000"
    ).exists()
