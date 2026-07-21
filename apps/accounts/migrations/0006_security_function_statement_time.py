from django.db import migrations


FORWARD_SQL = r"""
CREATE OR REPLACE FUNCTION cipa_is_platform_admin(p_user uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM accounts_usermembership m
    JOIN accounts_role r ON r.id = m.role_id
    WHERE m.user_id = p_user AND m.is_active AND r.code = 'PLATFORM_ADMIN'
      AND m.starts_at <= statement_timestamp()
      AND (m.ends_at IS NULL OR m.ends_at > statement_timestamp())
  );
$$;

CREATE OR REPLACE FUNCTION cipa_has_tenant_access(p_user uuid, p_tenant uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
  SELECT EXISTS (
    SELECT 1 FROM accounts_usermembership m
    WHERE m.user_id = p_user AND m.tenant_id = p_tenant AND m.is_active
      AND m.starts_at <= statement_timestamp()
      AND (m.ends_at IS NULL OR m.ends_at > statement_timestamp())
  ) OR EXISTS (
    SELECT 1 FROM accounts_privilegedaccessgrant g
    WHERE g.user_id = p_user AND g.tenant_id = p_tenant AND g.is_active
      AND g.revoked_at IS NULL AND g.starts_at <= statement_timestamp()
      AND g.expires_at > statement_timestamp()
  );
$$;

CREATE OR REPLACE FUNCTION cipa_invitation_tenant(p_digest text)
RETURNS uuid
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
  SELECT tenant_id FROM accounts_accountinvitation
  WHERE token_digest = p_digest AND accepted_at IS NULL AND revoked_at IS NULL
    AND expires_at > statement_timestamp()
  LIMIT 1;
$$;
"""

REVERSE_SQL = FORWARD_SQL.replace("statement_timestamp()", "CURRENT_TIMESTAMP")


class Migration(migrations.Migration):
    dependencies = [("accounts", "0005_alter_user_email")]
    operations = [migrations.RunSQL(FORWARD_SQL, REVERSE_SQL, hints={"target_db": "postgresql"})]
