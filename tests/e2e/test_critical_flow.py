import os

import pytest


@pytest.mark.e2e
def test_login_page_is_keyboard_accessible(page) -> None:
    base_url = os.getenv("E2E_BASE_URL")
    if not base_url:
        pytest.skip("Defina E2E_BASE_URL para executar contra o ambiente Docker")
    page.goto(f"{base_url}/contas/login/")
    page.get_by_label("E-mail").focus()
    assert page.get_by_label("E-mail").is_focused()
    assert page.get_by_role("button", name="Entrar").is_visible()
