from collections.abc import Callable
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils import timezone

from apps.accounts.models import Role, UserSession


class SessionSecurityMiddleware:
    MFA_EXEMPT_PREFIXES = ("/contas/2fa/", "/contas/logout/", "/contas/email/", "/convites/")

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return self.get_response(request)

        now = timezone.now()
        session = request.session
        created_raw = session.get("security_created_at")
        last_seen_raw = session.get("security_last_seen_at")
        if created_raw and now.timestamp() - float(created_raw) > settings.SESSION_ABSOLUTE_TIMEOUT:
            logout(request)
            return redirect("account_login")
        if last_seen_raw and now.timestamp() - float(last_seen_raw) > settings.SESSION_IDLE_TIMEOUT:
            logout(request)
            return redirect("account_login")
        session.setdefault("security_created_at", now.timestamp())
        session["security_last_seen_at"] = now.timestamp()
        if not session.session_key:
            session.save()
        tracked, _ = UserSession.objects.update_or_create(
            session_key=session.session_key,
            defaults={
                "user": request.user,
                "last_seen_at": now,
                "absolute_expires_at": now + timedelta(seconds=settings.SESSION_ABSOLUTE_TIMEOUT),
                "user_agent": request.headers.get("User-Agent", "")[:255],
            },
        )
        if tracked.revoked_at:
            logout(request)
            return redirect("account_login")

        needs_mfa = (
            request.user.is_superuser
            or request.user.memberships.filter(is_active=True, role__is_administrative=True)
            .exclude(role__code__in=[Role.Code.VOTER, Role.Code.CANDIDATE])
            .exists()
        )
        if needs_mfa and not request.path.startswith(self.MFA_EXEMPT_PREFIXES):
            from allauth.mfa.models import Authenticator

            has_totp = Authenticator.objects.filter(
                user=request.user, type=Authenticator.Type.TOTP
            ).exists()
            if not has_totp:
                return redirect("mfa_activate_totp")
            authentication_methods = request.session.get("account_authentication_methods", [])
            if not any(item.get("method") == "mfa" for item in authentication_methods):
                logout(request)
                return redirect("account_login")
        return self.get_response(request)
