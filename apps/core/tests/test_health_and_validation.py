import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.core.validators import digits_only, is_valid_cnpj, validate_cnpj


def test_cnpj_validation() -> None:
    assert digits_only("11.444.777/0001-61") == "11444777000161"
    assert is_valid_cnpj("11.444.777/0001-61")
    assert not is_valid_cnpj("11.111.111/1111-11")
    with pytest.raises(ValidationError):
        validate_cnpj("12.345.678/0001-00")


@pytest.mark.django_db
def test_health_endpoints(client) -> None:
    assert client.get(reverse("health-live")).json() == {"status": "ok"}
    ready = client.get(reverse("health-ready"))
    assert ready.status_code == 200
    assert ready.json()["checks"] == {"database": "ok", "cache": "ok"}


@pytest.mark.django_db
def test_home_page_and_authenticated_redirect(client, user) -> None:
    assert client.get(reverse("home")).status_code == 200
    client.force_login(user)
    assert client.get(reverse("home")).status_code == 302
