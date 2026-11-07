"""Integration gate fails when infrastructure is absent; it never silently skips."""

import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from sqlalchemy import create_engine


@pytest.fixture(scope="session")
def databases():
    if os.environ.get("APP_ENV") != "test":
        pytest.fail("Integration requires APP_ENV=test and an isolated *_test database")
    for name in ["DATABASE_URL", "MIGRATION_DATABASE_URL", "REDIS_URL"]:
        if not os.environ.get(name):
            pytest.fail(f"Missing integration configuration: {name}")
    runtime = os.environ["DATABASE_URL"]
    admin = os.environ["MIGRATION_DATABASE_URL"]
    for url in [runtime, admin]:
        if not urlsplit(url).path.endswith("_test"):
            pytest.fail("Integration databases must end in _test; never target dev/prod")
    if urlsplit(runtime).path != urlsplit(admin).path:
        pytest.fail("Runtime and migration must use the same test database")
    root = Path(__file__).resolve().parents[2]
    for _ in range(2):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "alembic",
                "-c",
                "apps/api/alembic.ini",
                "upgrade",
                "head",
            ],
            cwd=root,
            capture_output=True,
        )
        if result.returncode:
            pytest.fail("Migration failed against real PostgreSQL; output withheld to protect DSN")
    admin_engine = create_engine(admin, hide_parameters=True)
    runtime_engine = create_engine(runtime, pool_size=1, max_overflow=0, hide_parameters=True)
    yield admin_engine, runtime_engine
    admin_engine.dispose()
    runtime_engine.dispose()
