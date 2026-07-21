from allauth.account.signals import user_logged_in
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver

from apps.audit.services import record_event


@receiver(user_logged_in)
def audit_login(sender: object, request: object, user: object, **kwargs: object) -> None:
    tenant = getattr(request, "tenant", None)
    record_event(event_type="ADMIN_LOGIN", tenant=tenant, actor=user)


@receiver(user_login_failed)
def audit_login_failed(sender: object, request: object | None, **kwargs: object) -> None:
    record_event(event_type="ADMIN_LOGIN_FAILED", metadata={"reason": "invalid_credentials"})
