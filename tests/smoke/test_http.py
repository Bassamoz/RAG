"""Real Uvicorn process and TCP requests; dependencies intentionally unavailable."""

import os
import socket
import subprocess
import sys
import time

import httpx


def test_live_api_liveness_and_dependency_failure():
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    env = {
        **os.environ,
        "APP_ENV": "test",
        "DATABASE_URL": "postgresql+psycopg://app_runtime:test-only@127.0.0.1:1/app_test",
        "REDIS_URL": "redis://127.0.0.1:1/0",
    }
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "store_advisor.main:create_app",
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--no-access-log",
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=5) as client:
            for _ in range(50):
                try:
                    health = client.get("/api/v1/health")
                    break
                except httpx.ConnectError:
                    assert process.poll() is None, "API process failed during startup"
                    time.sleep(0.1)
            else:
                raise AssertionError("API did not listen")
            assert health.status_code == 200
            assert health.json() == {"status": "ok"}
            ready = client.get("/api/v1/ready")
            assert ready.status_code == 503
            assert ready.json()["error"]["code"] == "DEPENDENCY_UNAVAILABLE"
            assert "test-only" not in ready.text
            assert ready.headers["x-request-id"] == ready.json()["error"]["trace_id"]
    finally:
        process.terminate()
        process.wait(timeout=10)
