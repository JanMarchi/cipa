import pytest
from django.core.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import Role, UserMembership
from apps.accounts.policies import authorize


@pytest.mark.django_db
def test_auditor_is_read_only(user, tenant, auditor_role) -> None:
    UserMembership.objects.create(user=user, tenant=tenant, role=auditor_role)
    authorize(actor=user, action="view", tenant=tenant)
    with pytest.raises(PermissionDenied):
        authorize(actor=user, action="create", tenant=tenant)


@pytest.mark.django_db
def test_user_cannot_access_other_tenant(tenant_admin, other_tenant) -> None:
    with pytest.raises(PermissionDenied):
        authorize(actor=tenant_admin, action="view", tenant=other_tenant)


@pytest.mark.django_db
def test_membership_rejects_mismatched_scope(
    user, tenant, other_tenant, organization, admin_role
) -> None:
    organization.tenant = other_tenant
    organization.save(update_fields=("tenant",))
    membership = UserMembership(
        user=user, tenant=tenant, organization=organization, role=admin_role
    )
    with pytest.raises(ValidationError):
        membership.full_clean()


def test_all_nine_roles_are_declared() -> None:
    assert len(Role.Code.values) == 9
