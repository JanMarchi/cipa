from allauth.account.models import EmailAddress
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Role, User, UserMembership
from apps.audit.services import record_event
from apps.establishments.models import Establishment
from apps.organizations.models import Company, Organization
from apps.tenants.models import Tenant


class Command(BaseCommand):
    help = "Cria dados fictícios e idempotentes para desenvolvimento."

    @transaction.atomic
    def handle(self, *args: object, **options: object) -> None:
        tenant, tenant_created = Tenant.objects.get_or_create(
            slug="consultoria-demo",
            defaults={"name": "Consultoria Horizonte (Demonstração)"},
        )
        organization, _ = Organization.objects.get_or_create(
            tenant=tenant,
            name="Consultoria Horizonte",
            defaults={"kind": Organization.Kind.CONSULTANCY},
        )
        company_a, company_a_created = Company.objects.get_or_create(
            tenant=tenant,
            cnpj="11444777000161",
            defaults={
                "organization": organization,
                "corporate_name": "Indústria Aurora Demonstração Ltda.",
                "trade_name": "Aurora Demo",
            },
        )
        company_b, company_b_created = Company.objects.get_or_create(
            tenant=tenant,
            cnpj="12345678000195",
            defaults={
                "organization": organization,
                "corporate_name": "Logística Vale Demonstração Ltda.",
                "trade_name": "Vale Demo",
            },
        )
        establishments = [
            (company_a, "Unidade São Paulo", "UNIDADE-SP", "São Paulo", "SP", 120),
            (company_a, "Unidade Campinas", "UNIDADE-CPS", "Campinas", "SP", 65),
            (company_b, "Unidade Curitiba", "UNIDADE-CWB", "Curitiba", "PR", 80),
        ]
        for company, name, registration_id, city, state, employee_count in establishments:
            Establishment.objects.get_or_create(
                tenant=tenant,
                company=company,
                name=name,
                defaults={
                    "registration_id": registration_id,
                    "city": city,
                    "state": state,
                    "employee_count": employee_count,
                    "responsible_email": "sst@example.invalid",
                },
            )

        users = [
            (
                "consultoria.admin@example.invalid",
                "Administrador da Consultoria",
                Role.Code.CONSULTANCY_ADMIN,
                {"tenant": tenant, "organization": organization},
            ),
            (
                "empresa.admin@example.invalid",
                "Administrador da Empresa",
                Role.Code.COMPANY_ADMIN,
                {"tenant": tenant, "company": company_a},
            ),
            (
                "auditor@example.invalid",
                "Auditor de Demonstração",
                Role.Code.READONLY_AUDITOR,
                {"tenant": tenant},
            ),
        ]
        for email, full_name, role_code, scope in users:
            user, _ = User.objects.get_or_create(
                email=email, defaults={"full_name": full_name, "is_active": True}
            )
            if user.has_usable_password():
                user.set_unusable_password()
                user.save(update_fields=("password",))
            EmailAddress.objects.update_or_create(
                user=user, email=email, defaults={"verified": True, "primary": True}
            )
            role = Role.objects.get(code=role_code)
            UserMembership.objects.get_or_create(user=user, role=role, **scope)

        if tenant_created:
            record_event(event_type="TENANT_CREATED", tenant=tenant)
        if company_a_created:
            record_event(
                event_type="COMPANY_CREATED",
                tenant=tenant,
                organization=organization,
                company=company_a,
            )
        if company_b_created:
            record_event(
                event_type="COMPANY_CREATED",
                tenant=tenant,
                organization=organization,
                company=company_b,
            )
        self.stdout.write(
            self.style.SUCCESS("Dados de demonstração disponíveis; nenhuma senha foi criada.")
        )
