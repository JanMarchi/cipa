import os

import psycopg
import pytest
from django.db import connection
from django.urls import reverse

from apps.organizations.models import Company, Organization
from apps.tenants.services import accessible_tenants, user_can_access_tenant


@pytest.mark.django_db
def test_accessible_tenants_only_returns_membership(tenant_admin, tenant, other_tenant) -> None:
    assert accessible_tenants(tenant_admin) == [tenant]
    assert user_can_access_tenant(user=tenant_admin, tenant_id=tenant.id)
    assert not user_can_access_tenant(user=tenant_admin, tenant_id=other_tenant.id)


@pytest.mark.django_db
def test_manual_url_change_returns_not_found(authenticated_client, other_tenant) -> None:
    response = authenticated_client.get(
        reverse("dashboard", kwargs={"tenant_slug": other_tenant.slug})
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_tenant_switch_rejects_unrelated_tenant(client, tenant_admin, other_tenant) -> None:
    client.force_login(tenant_admin)
    session = client.session
    session["account_authentication_methods"] = [{"method": "mfa"}]
    session.save()
    response = client.post(reverse("tenant-select"), {"tenant_id": str(other_tenant.id)})
    assert response.status_code == 200
    assert "não possui acesso" in response.content.decode()


@pytest.mark.django_db
def test_stale_session_is_closed_after_membership_revocation(
    authenticated_client, tenant, tenant_admin
) -> None:
    tenant_admin.memberships.update(is_active=False)
    response = authenticated_client.get(reverse("dashboard", kwargs={"tenant_slug": tenant.slug}))
    assert response.status_code == 404
    assert "active_tenant_id" not in authenticated_client.session


@pytest.mark.postgres
@pytest.mark.django_db(transaction=True)
def test_postgres_rls_is_enabled() -> None:
    if connection.vendor != "postgresql":
        pytest.skip("Requer PostgreSQL")
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT relrowsecurity, relforcerowsecurity "
            "FROM pg_class WHERE relname = 'organizations_company'"
        )
        assert cursor.fetchone() == (True, True)
        cursor.execute("SELECT rolbypassrls FROM pg_roles WHERE rolname = 'cipa_app'")
        role = cursor.fetchone()
        assert role is not None and role[0] is False


@pytest.mark.postgres
@pytest.mark.django_db(transaction=True)
def test_postgres_rls_fails_closed_and_isolates_tenants(
    tenant, other_tenant, organization, company
) -> None:
    if connection.vendor != "postgresql":
        pytest.skip("Requer PostgreSQL")
    app_password = os.environ.get("CIPA_APP_PASSWORD")
    if not app_password:
        pytest.skip("CIPA_APP_PASSWORD não configurada")

    other_organization = Organization.objects.create(
        tenant=other_tenant,
        name="Consultoria B",
        kind=Organization.Kind.CONSULTANCY,
    )
    Company.objects.create(
        tenant=other_tenant,
        organization=other_organization,
        corporate_name="Empresa B Ltda.",
    )
    with connection.cursor() as cursor:
        cursor.execute("GRANT USAGE ON SCHEMA public TO cipa_app")
        cursor.execute("GRANT SELECT ON organizations_company TO cipa_app")

    database = connection.settings_dict
    with (
        psycopg.connect(
            dbname=database["NAME"],
            user="cipa_app",
            password=app_password,
            host=database["HOST"] or "localhost",
            port=database["PORT"] or 5432,
        ) as app_connection,
        app_connection.cursor() as cursor,
    ):
        cursor.execute("SELECT corporate_name FROM organizations_company")
        assert cursor.fetchall() == []
        cursor.execute("SELECT set_config('app.tenant_id', %s, false)", [str(tenant.id)])
        cursor.execute("SELECT corporate_name FROM organizations_company")
        assert cursor.fetchall() == [(company.corporate_name,)]
