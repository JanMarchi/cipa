from django.db import migrations


TABLES = ("organizations_organization", "organizations_company")
SETTING = "NULLIF(current_setting('app.tenant_id', true), '')::uuid"
FORWARD_SQL = "\n".join(
    f"""ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;
ALTER TABLE {table} FORCE ROW LEVEL SECURITY;
CREATE POLICY {table}_tenant_policy ON {table}
USING (tenant_id = {SETTING}) WITH CHECK (tenant_id = {SETTING});"""
    for table in TABLES
)
REVERSE_SQL = "\n".join(
    f"DROP POLICY IF EXISTS {table}_tenant_policy ON {table}; ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;"
    for table in reversed(TABLES)
)


class Migration(migrations.Migration):
    dependencies = [("organizations", "0001_initial")]
    operations = [migrations.RunSQL(FORWARD_SQL, REVERSE_SQL, hints={"target_db": "postgresql"})]
