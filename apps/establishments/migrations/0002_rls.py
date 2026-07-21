from django.db import migrations


FORWARD_SQL = r"""
ALTER TABLE establishments_establishment ENABLE ROW LEVEL SECURITY;
ALTER TABLE establishments_establishment FORCE ROW LEVEL SECURITY;
CREATE POLICY establishment_tenant_policy ON establishments_establishment
USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
"""
REVERSE_SQL = r"""
DROP POLICY IF EXISTS establishment_tenant_policy ON establishments_establishment;
ALTER TABLE establishments_establishment DISABLE ROW LEVEL SECURITY;
"""


class Migration(migrations.Migration):
    dependencies = [("establishments", "0001_initial")]
    operations = [migrations.RunSQL(FORWARD_SQL, REVERSE_SQL, hints={"target_db": "postgresql"})]
