import json
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from store_advisor.config import ConfigurationError, load_settings
from store_advisor.main import create_app


@pytest.fixture
def settings(monkeypatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://app_runtime:private@127.0.0.1:1/app")
    monkeypatch.setenv("REDIS_URL", "redis://127.0.0.1:1/0")
    return load_settings()


def test_missing_configuration_is_safe(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("REDIS_URL", "not-a-url-secret-value")
    with pytest.raises(ConfigurationError) as error:
        load_settings()
    assert "DATABASE_URL" in str(error.value)
    assert "not-a-url-secret-value" not in str(error.value)
    assert "input_value" not in str(error.value)


@pytest.mark.parametrize(
    "field,value",
    [
        ("DATABASE_URL", "postgresql+psycopg://user:sensitive-port"),
        ("REDIS_URL", "redis://localhost:sensitive-port/0"),
    ],
)
def test_malformed_dsn_fails_safely_during_settings_load(settings, monkeypatch, field, value):
    monkeypatch.setenv(field, value)
    with pytest.raises(ConfigurationError) as error:
        create_app(load_settings())
    assert field in str(error.value)
    assert "sensitive-port" not in str(error.value)


def test_liveness_and_unknown_route_contract(settings, capsys):
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/health", headers={"x-request-id": "untrusted\tvalue"})
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        UUID(response.headers["x-request-id"])
        assert response.headers["cache-control"] == "no-store"
        missing = client.get("/api/v1/not-found")
        assert missing.status_code == 404
        assert missing.json()["error"]["code"] == "NOT_FOUND"
        assert missing.json()["error"]["trace_id"] == missing.headers["x-request-id"]
    for line in capsys.readouterr().out.splitlines():
        event = json.loads(line)
        assert event["entryPoint"] == "api"
        assert "private" not in line


def test_readiness_is_not_liveness_when_real_services_are_down(settings):
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/ready")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "DEPENDENCY_UNAVAILABLE"
    assert "127.0.0.1" not in response.text
    assert "private" not in response.text


def test_body_limit_catches_declared_and_chunked_body(settings):
    settings.max_body_bytes = 100
    with TestClient(create_app(settings)) as client:
        for body in [b"x" * 101, iter([b"x" * 60, b"x" * 60])]:
            response = client.post("/api/v1/unknown", content=body)
            assert response.status_code == 413
            assert response.json()["error"]["code"] == "BODY_TOO_LARGE"


def test_unhandled_error_does_not_expose_details(settings):
    app = create_app(settings)

    @app.get("/test-failure")
    def failure():
        raise RuntimeError("database-password-private")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/test-failure")
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_ERROR"
    assert "database-password-private" not in response.text
    assert response.headers["x-request-id"] == response.json()["error"]["trace_id"]
