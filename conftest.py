import pytest
from allauth.mfa.models import Authenticator

from apps.accounts.models import Role, User, UserMembership
from apps.organizations.models import Company, Organization
from apps.tenants.models import Tenant


@pytest.fixture
def tenant(db) -> Tenant:
    return Tenant.objects.create(name="Tenant A", slug="tenant-a")


@pytest.fixture
def other_tenant(db) -> Tenant:
    return Tenant.objects.create(name="Tenant B", slug="tenant-b")


@pytest.fixture
def organization(tenant: Tenant) -> Organization:
    return Organization.objects.create(
        tenant=tenant, name="Consultoria A", kind=Organization.Kind.CONSULTANCY
    )


@pytest.fixture
def company(tenant: Tenant, organization: Organization) -> Company:
    return Company.objects.create(
        tenant=tenant,
        organization=organization,
        corporate_name="Empresa A Ltda.",
        cnpj="11444777000161",
    )


@pytest.fixture
def admin_role(db) -> Role:
    return Role.objects.get(code=Role.Code.CONSULTANCY_ADMIN)


@pytest.fixture
def auditor_role(db) -> Role:
    return Role.objects.get(code=Role.Code.READONLY_AUDITOR)


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(
        email="admin@example.invalid",
        password="Senha de teste muito forte 123!",  # noqa: S106
        full_name="Admin Teste",
    )


@pytest.fixture
def tenant_admin(user: User, tenant: Tenant, organization: Organization, admin_role: Role) -> User:
    UserMembership.objects.create(
        user=user, tenant=tenant, organization=organization, role=admin_role
    )
    Authenticator.objects.create(
        user=user, type=Authenticator.Type.TOTP, data={"secret": "encrypted-for-query-only"}
    )
    return user


@pytest.fixture
def authenticated_client(client, tenant_admin: User, tenant: Tenant):
    client.force_login(tenant_admin)
    session = client.session
    session["active_tenant_id"] = str(tenant.id)
    session["account_authentication_methods"] = [{"method": "mfa"}]
    session.save()
    return client
