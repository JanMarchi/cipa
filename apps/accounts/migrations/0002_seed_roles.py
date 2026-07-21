from django.db import migrations


ROLES = (
    ("PLATFORM_ADMIN", "Administrador da plataforma", "PLATFORM", True),
    ("CONSULTANCY_ADMIN", "Administrador da consultoria", "ORGANIZATION", True),
    ("COMPANY_ADMIN", "Administrador da empresa", "COMPANY", True),
    ("SST_RESPONSIBLE", "Responsável de SST", "ESTABLISHMENT", True),
    ("ELECTION_COMMITTEE", "Comissão eleitoral", "ELECTION", True),
    ("READONLY_AUDITOR", "Auditor somente leitura", "TENANT", True),
    ("RESTRICTED_SUPPORT", "Suporte técnico restrito", "PLATFORM", True),
    ("VOTER", "Eleitor", "SELF", False),
    ("CANDIDATE", "Candidato", "SELF", False),
)


def seed_roles(apps, schema_editor):
    role_model = apps.get_model("accounts", "Role")
    for code, name, scope_type, is_administrative in ROLES:
        role_model.objects.update_or_create(
            code=code,
            defaults={"name": name, "scope_type": scope_type, "is_administrative": is_administrative},
        )


class Migration(migrations.Migration):
    dependencies = [("accounts", "0001_initial")]
    operations = [migrations.RunPython(seed_roles, migrations.RunPython.noop)]
