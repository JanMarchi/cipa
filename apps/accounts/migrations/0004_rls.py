from django.db import migrations


FORWARD_SQL = r"""
ALTER TABLE accounts_usermembership ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts_usermembership FORCE ROW LEVEL SECURITY;
CREATE POLICY membership_tenant_policy ON accounts_usermembership
USING (
  tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  OR (user_id = NULLIF(current_setting('app.user_id', true), '')::uuid)
  OR cipa_is_platform_admin(NULLIF(current_setting('app.user_id', true), '')::uuid)
)
WITH CHECK (
  tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  OR cipa_is_platform_admin(NULLIF(current_setting('app.user_id', true), '')::uuid)
);

ALTER TABLE accounts_privilegedaccessgrant ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts_privilegedaccessgrant FORCE ROW LEVEL SECURITY;
CREATE POLICY privileged_grant_policy ON accounts_privilegedaccessgrant
USING (
  tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  OR user_id = NULLIF(current_setting('app.user_id', true), '')::uuid
  OR cipa_is_platform_admin(NULLIF(current_setting('app.user_id', true), '')::uuid)
)
WITH CHECK (
  tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  OR cipa_is_platform_admin(NULLIF(current_setting('app.user_id', true), '')::uuid)
);

ALTER TABLE accounts_accountinvitation ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts_accountinvitation FORCE ROW LEVEL SECURITY;
CREATE POLICY invitation_tenant_policy ON accounts_accountinvitation
USING (
  tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  OR cipa_is_platform_admin(NULLIF(current_setting('app.user_id', true), '')::uuid)
)
WITH CHECK (
  tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  OR cipa_is_platform_admin(NULLIF(current_setting('app.user_id', true), '')::uuid)
);
"""

REVERSE_SQL = r"""
DROP POLICY IF EXISTS invitation_tenant_policy ON accounts_accountinvitation;
ALTER TABLE accounts_accountinvitation DISABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS privileged_grant_policy ON accounts_privilegedaccessgrant;
ALTER TABLE accounts_privilegedaccessgrant DISABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS membership_tenant_policy ON accounts_usermembership;
ALTER TABLE accounts_usermembership DISABLE ROW LEVEL SECURITY;
"""


class Migration(migrations.Migration):
    dependencies = [("accounts", "0003_security_functions")]
    operations = [migrations.RunSQL(FORWARD_SQL, REVERSE_SQL, hints={"target_db": "postgresql"})]
