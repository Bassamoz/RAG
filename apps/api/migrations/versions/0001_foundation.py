"""Initial app-only schema, pgvector and deny-by-default runtime role.

No mutation of Supabase auth/storage schemas. Runtime is deliberately read-only until
phase 02 supplies authenticated write paths. RLS context is transaction-local.
Source: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS extensions")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions")
    op.execute("""DO $$ BEGIN
      IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='app_runtime') THEN
        CREATE ROLE app_runtime NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE
          NOINHERIT NOBYPASSRLS NOREPLICATION;
      ELSIF EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname='app_runtime' AND
          (rolsuper OR rolcreatedb OR rolcreaterole OR rolinherit OR rolbypassrls OR rolreplication)
      ) OR EXISTS (
        SELECT 1 FROM pg_auth_members m JOIN pg_roles r ON r.oid=m.member
        WHERE r.rolname='app_runtime'
      ) THEN
        RAISE EXCEPTION 'Existing app_runtime role is not restricted; manual review required';
      END IF;
    END $$""")
    op.execute("REVOKE ALL ON SCHEMA app FROM PUBLIC")
    op.execute("GRANT USAGE ON SCHEMA app TO app_runtime")
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("auth_subject", sa.Uuid(), nullable=False, unique=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        schema="app",
    )
    op.create_table(
        "tenants",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        schema="app",
    )
    op.create_table(
        "memberships",
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("app.tenants.id"), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("app.users.id"), primary_key=True),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="active"),
        sa.CheckConstraint("role IN ('tenant_owner','tenant_admin','support_agent','analyst')"),
        sa.CheckConstraint("status IN ('active','suspended')"),
        schema="app",
    )
    op.create_table(
        "stores",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("tenant_id", sa.Uuid(), sa.ForeignKey("app.tenants.id"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("tenant_id", "id"),
        schema="app",
    )
    policies = {
        "users": "id = NULLIF(current_setting('app.user_id', true), '')::uuid",
        "tenants": "id = NULLIF(current_setting('app.tenant_id', true), '')::uuid",
        "memberships": "tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid "
        "AND user_id = NULLIF(current_setting('app.user_id', true), '')::uuid",
        "stores": "tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid "
        "AND (NULLIF(current_setting('app.store_id', true), '') IS NULL "
        "OR id = NULLIF(current_setting('app.store_id', true), '')::uuid)",
    }
    for table, condition in policies.items():
        op.execute(f"ALTER TABLE app.{table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE app.{table} FORCE ROW LEVEL SECURITY")
        # Identifiers/conditions above are fixed migration text, never request input.
        op.execute(
            f"CREATE POLICY runtime_read ON app.{table} FOR SELECT "
            f"TO app_runtime USING ({condition})"
        )
        op.execute(f"GRANT SELECT ON app.{table} TO app_runtime")
    op.execute("GRANT SELECT ON app.alembic_version TO app_runtime")


def downgrade() -> None:
    raise RuntimeError(
        "Destructive downgrade is disabled; use a forward migration or isolated restore"
    )
