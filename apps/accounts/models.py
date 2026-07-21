import hashlib
import secrets
import uuid
from datetime import timedelta

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone

from apps.core.models import UUIDTimeStampedModel


class UserManager(BaseUserManager["User"]):
    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields: object) -> "User":
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        normalized = self.normalize_email(email).strip().lower()
        user = self.model(email=normalized, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self, email: str, password: str | None = None, **extra_fields: object
    ) -> "User":
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields: object
    ) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True or extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusuário deve possuir is_staff e is_superuser.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None  # type: ignore[assignment]
    email = models.EmailField("e-mail", max_length=254, unique=True)
    full_name = models.CharField("nome completo", max_length=180)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = ["full_name"]
    objects = UserManager()  # type: ignore[assignment]

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("email"), name="accounts_user_email_ci_unique")
        ]

    def save(self, *args: object, **kwargs: object) -> None:
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    def get_full_name(self) -> str:
        return self.full_name

    def __str__(self) -> str:
        return self.email


class Role(UUIDTimeStampedModel):
    class Code(models.TextChoices):
        PLATFORM_ADMIN = "PLATFORM_ADMIN", "Administrador da plataforma"
        CONSULTANCY_ADMIN = "CONSULTANCY_ADMIN", "Administrador da consultoria"
        COMPANY_ADMIN = "COMPANY_ADMIN", "Administrador da empresa"
        SST_RESPONSIBLE = "SST_RESPONSIBLE", "Responsável de SST"
        ELECTION_COMMITTEE = "ELECTION_COMMITTEE", "Comissão eleitoral"
        READONLY_AUDITOR = "READONLY_AUDITOR", "Auditor somente leitura"
        RESTRICTED_SUPPORT = "RESTRICTED_SUPPORT", "Suporte técnico restrito"
        VOTER = "VOTER", "Eleitor"
        CANDIDATE = "CANDIDATE", "Candidato"

    class Scope(models.TextChoices):
        PLATFORM = "PLATFORM", "Plataforma"
        TENANT = "TENANT", "Tenant"
        ORGANIZATION = "ORGANIZATION", "Organização"
        COMPANY = "COMPANY", "Empresa"
        ESTABLISHMENT = "ESTABLISHMENT", "Estabelecimento"
        ELECTION = "ELECTION", "Eleição"
        SELF = "SELF", "Próprio usuário"

    code = models.CharField(max_length=32, choices=Code.choices, unique=True)
    name = models.CharField(max_length=100)
    scope_type = models.CharField(max_length=20, choices=Scope.choices)
    is_administrative = models.BooleanField(default=True)
    permissions = models.ManyToManyField("auth.Permission", blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class UserMembership(UUIDTimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="memberships")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="memberships")
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.PROTECT, null=True, blank=True)
    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.PROTECT, null=True, blank=True
    )
    company = models.ForeignKey(
        "organizations.Company", on_delete=models.PROTECT, null=True, blank=True
    )
    establishment = models.ForeignKey(
        "establishments.Establishment", on_delete=models.PROTECT, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    starts_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=("user", "tenant", "is_active"), name="membership_access_idx")
        ]

    def clean(self) -> None:
        errors: dict[str, str] = {}
        scope = self.role.scope_type if self.role_id else None
        if scope in {Role.Scope.PLATFORM, Role.Scope.SELF}:
            if any((self.tenant_id, self.organization_id, self.company_id, self.establishment_id)):
                errors["tenant"] = "Papéis globais ou próprios não aceitam escopo de tenant."
        else:
            if not self.tenant_id:
                errors["tenant"] = "Este papel exige tenant."
        required: dict[str, tuple[str, uuid.UUID | None]] = {
            Role.Scope.ORGANIZATION: ("organization", self.organization_id),
            Role.Scope.COMPANY: ("company", self.company_id),
            Role.Scope.ESTABLISHMENT: ("establishment", self.establishment_id),
        }
        if scope in required:
            field, value = required[scope]
            if not value:
                errors[field] = "Informe o escopo exigido pelo papel."
        organization = self.organization if self.organization_id else None
        company = self.company if self.company_id else None
        establishment = self.establishment if self.establishment_id else None
        if organization is not None and organization.tenant_id != self.tenant_id:
            errors["organization"] = "A organização pertence a outro tenant."
        if company is not None and company.tenant_id != self.tenant_id:
            errors["company"] = "A empresa pertence a outro tenant."
        if establishment is not None and establishment.tenant_id != self.tenant_id:
            errors["establishment"] = "O estabelecimento pertence a outro tenant."
        if self.ends_at and self.ends_at <= self.starts_at:
            errors["ends_at"] = "O término deve ser posterior ao início."
        if errors:
            raise ValidationError(errors)

    def is_current(self) -> bool:
        now = timezone.now()
        return (
            self.is_active
            and self.starts_at <= now
            and (self.ends_at is None or self.ends_at > now)
        )


class AccountInvitation(UUIDTimeStampedModel):
    email = models.EmailField()
    full_name = models.CharField(max_length=180)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.PROTECT, null=True, blank=True)
    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.PROTECT, null=True, blank=True
    )
    company = models.ForeignKey(
        "organizations.Company", on_delete=models.PROTECT, null=True, blank=True
    )
    establishment = models.ForeignKey(
        "establishments.Establishment", on_delete=models.PROTECT, null=True, blank=True
    )
    invited_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="sent_invitations")
    token_digest = models.CharField(max_length=64, unique=True, editable=False)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=("email", "expires_at"), name="invitation_lookup_idx")]

    @staticmethod
    def digest_token(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @classmethod
    def new_token(cls) -> tuple[str, str]:
        token = secrets.token_urlsafe(32)
        return token, cls.digest_token(token)

    def is_usable(self) -> bool:
        return not self.accepted_at and not self.revoked_at and self.expires_at > timezone.now()

    def save(self, *args: object, **kwargs: object) -> None:
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)


class PrivilegedAccessGrantQuerySet(models.QuerySet["PrivilegedAccessGrant"]):
    def active(self) -> "PrivilegedAccessGrantQuerySet":
        now = timezone.now()
        return self.filter(
            is_active=True, starts_at__lte=now, expires_at__gt=now, revoked_at__isnull=True
        )


class PrivilegedAccessGrant(UUIDTimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="privileged_grants")
    tenant = models.ForeignKey(
        "tenants.Tenant", on_delete=models.PROTECT, related_name="privileged_grants"
    )
    granted_by = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="issued_privileged_grants"
    )
    starts_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    justification = models.TextField(max_length=1000)
    is_active = models.BooleanField(default=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    objects = PrivilegedAccessGrantQuerySet.as_manager()

    class Meta:
        indexes = [
            models.Index(fields=("user", "tenant", "expires_at"), name="privileged_access_idx")
        ]

    def clean(self) -> None:
        if self.expires_at <= self.starts_at:
            raise ValidationError({"expires_at": "O término deve ser posterior ao início."})
        if not self.justification.strip():
            raise ValidationError({"justification": "A justificativa é obrigatória."})
        if self.expires_at > self.starts_at + timedelta(hours=8):
            raise ValidationError(
                {"expires_at": "O acesso privilegiado pode durar no máximo 8 horas."}
            )


class UserSession(UUIDTimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tracked_sessions")
    session_key = models.CharField(max_length=40, unique=True)
    last_seen_at = models.DateTimeField(default=timezone.now)
    absolute_expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    class Meta:
        indexes = [models.Index(fields=("user", "revoked_at"), name="active_user_session_idx")]
