"""Boot the documented local stack twice and prove that existing foundation rows survive.

Only a uniquely identified sentinel in the local development database is created and removed.
No reset, truncate, global cleanup, or demo seed is performed.
"""

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from store_advisor.config import load_settings
from store_advisor.worker import make_worker

ROOT = Path(__file__).resolve().parents[1]


def start() -> None:
    subprocess.run([sys.executable, "scripts/dev.py"], cwd=ROOT, check=True)


def check_services() -> None:
    with httpx.Client(timeout=8) as client:
        for _ in range(30):
            try:
                response = client.get("http://127.0.0.1:8000/api/v1/ready")
                if response.status_code == 200:
                    break
            except httpx.TransportError:
                pass
            time.sleep(0.5)
        else:
            raise AssertionError("Development API did not become ready")
        assert response.json() == {"status": "ok"}
        assert client.get("http://127.0.0.1:8000/api/v1/health").json() == {"status": "ok"}
        page = client.get("http://127.0.0.1:3000")
        assert page.status_code == 200
        assert '<html lang="ar" dir="rtl"' in page.text
        assert "الاتصال متاح" in page.text
    worker = make_worker(load_settings())
    try:
        assert worker.send_task("store_advisor.worker_probe").get(timeout=15) == {"status": "ok"}
    finally:
        worker.close()


def snapshot(engine) -> dict[str, dict[str, object]]:
    tables = {"users": "id", "tenants": "id", "memberships": "tenant_id,user_id", "stores": "id"}
    result = {}
    with engine.connect() as connection:
        for table, order in tables.items():
            rows = connection.execute(text(f"SELECT * FROM app.{table} ORDER BY {order}")).all()
            digest = hashlib.sha256(json.dumps([list(row) for row in rows], default=str).encode())
            result[table] = {"rows": len(rows), "sha256": digest.hexdigest()}
    return result


def local_values() -> dict[str, str]:
    values = dict(
        line.split("=", 1)
        for line in (ROOT / ".env.dev").read_text(encoding="utf-8").splitlines()
        if "=" in line and not line.startswith("#")
    )
    admin_url = make_url(values["MIGRATION_DATABASE_URL"])
    if values.get("APP_ENV") != "dev" or admin_url.host not in {"127.0.0.1", "localhost"}:
        raise RuntimeError("Restart verification only permits a local development database")
    return values


def main() -> None:
    original = None
    if (ROOT / ".env.dev").exists():
        # A future rerun may already contain user rows. Refuse to start without a baseline;
        # otherwise a destructive first startup could be hidden by the second-start check.
        baseline_engine = create_engine(
            local_values()["MIGRATION_DATABASE_URL"], hide_parameters=True
        )
        try:
            original = snapshot(baseline_engine)
        except Exception:
            raise RuntimeError(
                "Existing local database must be reachable for a pre-start snapshot; "
                "start Supabase without resetting data, then rerun verification"
            ) from None
        finally:
            baseline_engine.dispose()
    start()
    values = local_values()
    os.environ.update(values)
    check_services()
    engine = create_engine(values["MIGRATION_DATABASE_URL"], hide_parameters=True)
    sentinel = uuid4()
    try:
        if original is not None:
            assert snapshot(engine) == original, "Foundation rows changed during first startup"
        with engine.begin() as connection:
            connection.execute(
                text("INSERT INTO app.tenants(id,name) VALUES(:id,:name)"),
                {"id": sentinel, "name": "Foundation restart acceptance sentinel"},
            )
        before = snapshot(engine)
        start()
        check_services()
        after = snapshot(engine)
        assert before == after, "Foundation rows changed during second startup"
        print(
            json.dumps(
                {
                    "event": "development_restart_verified",
                    "starts": 2,
                    "health": 200,
                    "readiness": 200,
                    "web": 200,
                    "celery_roundtrip": "passed",
                    "foundation_rows_preserved": True,
                    "pre_first_start_snapshot": (
                        "verified" if original is not None else "no_existing_env_file"
                    ),
                    "preservation_scope": (
                        "both_starts" if original is not None else "populated_second_start"
                    ),
                    "snapshot": after,
                }
            )
        )
    finally:
        with engine.begin() as connection:
            connection.execute(text("DELETE FROM app.tenants WHERE id=:id"), {"id": sentinel})
        engine.dispose()


if __name__ == "__main__":
    main()
