from django.core.management.base import BaseCommand, CommandError

from apps.audit.services import verify_chain
from apps.tenants.models import Tenant


class Command(BaseCommand):
    help = "Verifica todas as cadeias de auditoria."

    def handle(self, *args: object, **options: object) -> None:
        failures: list[str] = []
        for tenant in [None, *Tenant.objects.all()]:
            failures.extend(verify_chain(tenant=tenant))
        if failures:
            raise CommandError(f"Cadeia inválida nos eventos: {', '.join(failures)}")
        self.stdout.write(self.style.SUCCESS("Todas as cadeias estão íntegras."))
