"""Idempotent local start; never reset databases or seed demo data."""

import json
import os
import secrets
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)


def run(args, *, env=None, capture=False):
    # Windows npm installs .cmd shims; CreateProcess does not perform PATHEXT lookup.
    executable = shutil.which(args[0])
    if not executable:
        raise SystemExit(f"Missing executable: {args[0]}")
    result = subprocess.run(
        [executable, *args[1:]], env=env, text=True, capture_output=capture, check=False
    )
    if result.returncode:
        # Captured Supabase output may contain local keys; never echo it into reports.
        raise SystemExit(f"Local setup failed at {args[0]}; exit={result.returncode}")
    return result.stdout


def main():
    for command in ["docker", "pnpm", "uv"]:
        if not shutil.which(command):
            raise SystemExit(f"Missing prerequisite: {command}. See docs/SETUP.md")
    run(["docker", "info"], capture=True)
    # Phase 01 needs DB/Auth/Storage and local mail, not editors, telemetry or functions.
    # Keep all required services and their health checks; CLI's documented exclusions
    # avoid downloading unrelated services on a slow first Windows setup.
    run(
        [
            "pnpm",
            "exec",
            "supabase",
            "start",
            "--exclude",
            "realtime,studio,postgres-meta,edge-runtime,logflare,vector,imgproxy,supavisor",
        ],
        capture=True,
    )
    status = json.loads(run(["pnpm", "exec", "supabase", "status", "-o", "json"], capture=True))
    admin = status.get("DB_URL")
    if not admin:
        raise SystemExit("Supabase status did not return DB_URL; no changes made")
    saved = ROOT / ".env.dev"
    current = (
        dict(line.split("=", 1) for line in saved.read_text().splitlines() if "=" in line)
        if saved.exists()
        else {}
    )
    password = current.get("RUNTIME_DB_PASSWORD") or secrets.token_urlsafe(32)
    parts = urlsplit(admin)
    runtime = urlunsplit(
        parts._replace(netloc=f"app_runtime:{password}@{parts.hostname}:{parts.port}")
    )
    runtime = runtime.replace("postgresql://", "postgresql+psycopg://")
    migration = admin.replace("postgresql://", "postgresql+psycopg://")
    values = {
        "APP_ENV": "dev",
        "DATABASE_URL": runtime,
        "MIGRATION_DATABASE_URL": migration,
        "RUNTIME_DB_PASSWORD": password,
        "DATABASE_URL_CONTAINER": runtime.replace("127.0.0.1", "host.docker.internal").replace(
            "localhost", "host.docker.internal"
        ),
        "REDIS_URL": "redis://127.0.0.1:6379/0",
        "API_ORIGIN": "http://127.0.0.1:8000",
    }
    env = {**os.environ, **values}
    run(
        [
            "uv",
            "run",
            "--project",
            "apps/api",
            "alembic",
            "-c",
            "apps/api/alembic.ini",
            "upgrade",
            "head",
        ],
        env=env,
    )
    run(
        [
            "uv",
            "run",
            "--project",
            "apps/api",
            "python",
            "scripts/provision_runtime.py",
        ],
        env=env,
    )
    saved.write_text("\n".join(f"{key}={value}" for key, value in values.items()) + "\n")
    if os.name != "nt":
        saved.chmod(0o600)
    run(
        [
            "docker",
            "compose",
            "--env-file",
            ".env.dev",
            "-f",
            "infra/compose.yaml",
            "up",
            "--build",
            "-d",
        ],
        env=env,
    )
    print("Local services started. Open http://127.0.0.1:3000. No demo data was seeded.")


if __name__ == "__main__":
    main()
