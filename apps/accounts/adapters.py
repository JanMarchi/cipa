import base64
import hashlib

from allauth.account.adapter import DefaultAccountAdapter
from allauth.mfa.adapter import DefaultMFAAdapter
from cryptography.fernet import Fernet, MultiFernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def _fernet() -> MultiFernet:
    configured = (
        [item.strip() for item in settings.MFA_ENCRYPTION_KEYS.split(",") if item.strip()]
        if hasattr(settings, "MFA_ENCRYPTION_KEYS")
        else []
    )
    if not configured:
        if not settings.DEBUG:
            raise ImproperlyConfigured("MFA_ENCRYPTION_KEYS é obrigatório fora de desenvolvimento")
        digest = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
        configured = [base64.urlsafe_b64encode(digest).decode("ascii")]
    return MultiFernet([Fernet(key.encode("ascii")) for key in configured])


class EncryptedMFAAdapter(DefaultMFAAdapter):
    def encrypt(self, text: str) -> str:
        return _fernet().encrypt(text.encode("utf-8")).decode("ascii")

    def decrypt(self, encrypted_text: str) -> str:
        return _fernet().decrypt(encrypted_text.encode("ascii")).decode("utf-8")


class InviteOnlyAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: object) -> bool:
        return False
