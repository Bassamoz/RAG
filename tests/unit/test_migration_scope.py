import os
import subprocess
import sys
from pathlib import Path

import pytest
from store_advisor.migration_scope import include_app_name


@pytest.mark.parametrize("schema", [None, "public", "auth", "storage", "extensions"])
def test_provider_and_default_schemas_are_excluded_from_autogeneration(schema):
    assert not include_app_name(schema, "schema", {})
    assert not include_app_name("provider_table", "table", {"schema_name": schema})


def test_app_schema_and_its_tables_remain_manageable():
    assert include_app_name("app", "schema", {})
    assert include_app_name("users", "table", {"schema_name": "app"})


def test_migration_startup_hides_malformed_admin_dsn():
    env = {**os.environ, "MIGRATION_DATABASE_URL": "postgresql+psycopg://user:private-sentinel"}
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head", "--sql"],
        cwd=Path(__file__).resolve().parents[2],
        env=env,
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    output = result.stdout + result.stderr
    assert b"MIGRATION_DATABASE_URL" in output
    assert b"private-sentinel" not in output
