import pytest
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import AccountInvitation, Role


@pytest.mark.django_db
def test_invalid_invitation_shows_uniform_message(client) -> None:
    response = client.post(
        reverse("invitation-accept", kwargs={"token": "invalido"}),
        {
            "password1": "Uma senha suficientemente longa 123!",
            "password2": "Uma senha suficientemente longa 123!",
        },
        follow=True,
    )
    assert response.status_code == 200
    assert "inválido, expirou ou já foi utilizado" in response.content.decode()


@pytest.mark.django_db
def test_idle_session_is_terminated(client, user, settings) -> None:
    client.force_login(user)
    session = client.session
    session["security_created_at"] = timezone.now().timestamp()
    session["security_last_seen_at"] = (
        timezone.now().timestamp() - settings.SESSION_IDLE_TIMEOUT - 1
    )
    session.save()
    response = client.get(reverse("tenant-select"))
    assert response.status_code == 302
    assert reverse("account_login") in response.url


@pytest.mark.django_db
def test_session_without_completed_mfa_is_rejected(client, tenant_admin, tenant) -> None:
    client.force_login(tenant_admin)
    session = client.session
    session["active_tenant_id"] = str(tenant.id)
    session.save()
    response = client.get(reverse("dashboard", kwargs={"tenant_slug": tenant.slug}))
    assert response.status_code == 302
    assert reverse("account_login") in response.url


@pytest.mark.django_db
def test_consultancy_admin_can_invite_tenant_auditor(authenticated_client) -> None:
    role = Role.objects.get(code=Role.Code.READONLY_AUDITOR)
    response = authenticated_client.post(
        reverse("user-list"),
        {
            "email": "invited-auditor@example.invalid",
            "full_name": "Auditor Convidado",
            "role": str(role.id),
        },
    )
    assert response.status_code == 302
    invitation = AccountInvitation.objects.get(email="invited-auditor@example.invalid")
    assert invitation.role == role
    assert invitation.token_digest
