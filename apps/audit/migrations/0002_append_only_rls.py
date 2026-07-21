from django.db import migrations


FORWARD_SQL = r"""
CREATE OR REPLACE FUNCTION cipa_reject_audit_mutation()
RETURNS trigger LANGUAGE plpgsql SET search_path = public, pg_temp AS $$
BEGIN
  RAISE EXCEPTION 'audit events are append-only';
END;
$$;

CREATE TRIGGER audit_event_no_update_delete
BEFORE UPDATE OR DELETE ON audit_auditevent
FOR EACH ROW EXECUTE FUNCTION cipa_reject_audit_mutation();

ALTER TABLE audit_auditevent ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_auditevent FORCE ROW LEVEL SECURITY;
CREATE POLICY audit_event_tenant_policy ON audit_auditevent
USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
WITH CHECK (
  tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  OR tenant_id IS NULL
);

ALTER TABLE audit_auditchainhead ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_auditchainhead FORCE ROW LEVEL SECURITY;
CREATE POLICY audit_head_tenant_policy ON audit_auditchainhead
USING (
  tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  OR tenant_id IS NULL
)
WITH CHECK (
  tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  OR tenant_id IS NULL
);
"""

REVERSE_SQL = r"""
DROP POLICY IF EXISTS audit_head_tenant_policy ON audit_auditchainhead;
ALTER TABLE audit_auditchainhead DISABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS audit_event_tenant_policy ON audit_auditevent;
ALTER TABLE audit_auditevent DISABLE ROW LEVEL SECURITY;
DROP TRIGGER IF EXISTS audit_event_no_update_delete ON audit_auditevent;
DROP FUNCTION IF EXISTS cipa_reject_audit_mutation();
"""


class Migration(migrations.Migration):
    dependencies = [("audit", "0001_initial")]
    operations = [migrations.RunSQL(FORWARD_SQL, REVERSE_SQL, hints={"target_db": "postgresql"})]
