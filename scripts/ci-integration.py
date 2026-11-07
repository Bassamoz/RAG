"""Run actual migration/DB/Redis/worker tests against disposable Compose services."""

import os
import secrets
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
if not shutil.which("docker"):
    raise SystemExit("Missing prerequisite: docker. Integration gate is blocked, not passed.")
password, runtime_password = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
env = {
    **os.environ,
    "APP_ENV": "test",
    "TEST_DB_PASSWORD": password,
    "RUNTIME_DB_PASSWORD": runtime_password,
    "MIGRATION_DATABASE_URL": f"postgresql+psycopg://postgres:{quote(password)}@127.0.0.1:55432/store_advisor_test",
    "DATABASE_URL": f"postgresql+psycopg://app_runtime:{quote(runtime_password)}@127.0.0.1:55432/store_advisor_test",
    "REDIS_URL": "redis://127.0.0.1:56379/0",
}
compose = ["docker", "compose", "-f", "infra/compose.test.yaml"]
worker = None
try:
    subprocess.run(compose + ["up", "-d", "--wait"], env=env, check=True)
    subprocess.run(
        [
            sys.executable,
            "-m",
            "alembic",
            "-c",
            "apps/api/alembic.ini",
            "upgrade",
            "head",
        ],
        env=env,
        check=True,
    )
    subprocess.run([sys.executable, "scripts/provision_runtime.py"], env=env, check=True)
    # Solo pool also supports local Windows development; Linux deployment uses prefork.
    worker = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "celery",
            "-A",
            "store_advisor.celery_app:app",
            "worker",
            "--pool=solo",
            "--loglevel=WARNING",
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    from store_advisor.config import load_settings
    from store_advisor.worker import make_worker

    saved = os.environ.copy()
    os.environ.update(env)
    app = make_worker(load_settings())
    os.environ.clear()
    os.environ.update(saved)
    for _ in range(30):
        if app.control.ping(timeout=1):
            break
        time.sleep(0.2)
    else:
        raise RuntimeError("Test worker did not become ready")
    app.close()
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            "apps/api/pyproject.toml",
            "tests/integration",
            "-q",
        ],
        env=env,
    )
    raise SystemExit(result.returncode)
finally:
    if worker:
        worker.terminate()
        worker.wait(timeout=15)
    # Removes ONLY disposable test services; never volumes or development infrastructure.
    subprocess.run(compose + ["down"], env=env, check=False)
