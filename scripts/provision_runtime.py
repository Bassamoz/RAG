"""Set a local runtime password out of band; never put passwords in Alembic history."""

import os

import psycopg
from psycopg import sql

if os.environ.get("APP_ENV") not in {"dev", "test"}:
    raise SystemExit("Local provisioning requires APP_ENV=dev or test")
url = os.environ.get("MIGRATION_DATABASE_URL", "")
password = os.environ.get("RUNTIME_DB_PASSWORD", "")
if not url or len(password) < 24:
    raise SystemExit("MIGRATION_DATABASE_URL and strong RUNTIME_DB_PASSWORD are required")
try:
    with psycopg.connect(url.replace("postgresql+psycopg://", "postgresql://")) as connection:
        connection.execute(
            sql.SQL("ALTER ROLE app_runtime LOGIN PASSWORD {} ").format(sql.Literal(password))
        )
except Exception:
    raise SystemExit("Runtime provisioning failed; check local DB and migration status") from None
print("Local runtime login configured")
