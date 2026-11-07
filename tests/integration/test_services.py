from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import text
from store_advisor.config import load_settings
from store_advisor.db import scoped_session
from store_advisor.main import create_app
from store_advisor.worker import make_worker


def test_schema_migration_rerun_and_runtime_rls(databases):
    admin, runtime = databases
    user_a, user_b, tenant_a, tenant_b = [uuid4() for _ in range(4)]
    stores = [uuid4() for _ in range(3)]
    with admin.begin() as connection:
        for user in [user_a, user_b]:
            connection.execute(
                text("INSERT INTO app.users (id, auth_subject) VALUES (:id,:id)"),
                {"id": user},
            )
        for tenant in [tenant_a, tenant_b]:
            connection.execute(
                text("INSERT INTO app.tenants (id,name) VALUES (:id,'Synthetic test')"),
                {"id": tenant},
            )
        for store, tenant in zip(stores, [tenant_a, tenant_a, tenant_b], strict=True):
            connection.execute(
                text(
                    "INSERT INTO app.stores (id,tenant_id,name) "
                    "VALUES (:id,:tenant,'Synthetic store')"
                ),
                {"id": store, "tenant": tenant},
            )
    try:
        with runtime.connect() as connection:
            assert connection.execute(text("SELECT id FROM app.stores")).all() == []
            assert (
                connection.execute(
                    text(
                        "SELECT rolsuper OR rolbypassrls OR rolcreatedb "
                        "OR rolcreaterole FROM pg_roles "
                        "WHERE rolname=current_user"
                    )
                ).scalar_one()
                is False
            )
            assert (
                connection.execute(text("SELECT version_num FROM app.alembic_version")).scalar_one()
                == "0001"
            )
        with scoped_session(runtime, user_id=user_a, tenant_id=tenant_a) as session:
            assert set(session.execute(text("SELECT id FROM app.stores")).scalars()) == set(
                stores[:2]
            )
            assert session.execute(text("SELECT id FROM app.users")).scalar_one() == user_a
        with runtime.connect() as connection:
            assert connection.execute(text("SELECT id FROM app.stores")).all() == []
        with scoped_session(
            runtime, user_id=user_b, tenant_id=tenant_b, store_id=stores[0]
        ) as session:
            assert session.execute(text("SELECT id FROM app.stores")).all() == []
        with scoped_session(
            runtime, user_id=user_b, tenant_id=tenant_b, store_id=stores[2]
        ) as session:
            assert session.execute(text("SELECT id FROM app.stores")).scalar_one() == stores[2]
        with admin.connect() as connection:
            assert connection.execute(
                text("SELECT extversion FROM pg_extension WHERE extname='vector'")
            ).scalar_one()
    finally:
        with admin.begin() as connection:
            connection.execute(
                text("DELETE FROM app.stores WHERE tenant_id IN (:a,:b)"),
                {"a": tenant_a, "b": tenant_b},
            )
            connection.execute(
                text("DELETE FROM app.tenants WHERE id IN (:a,:b)"),
                {"a": tenant_a, "b": tenant_b},
            )
            connection.execute(
                text("DELETE FROM app.users WHERE id IN (:a,:b)"),
                {"a": user_a, "b": user_b},
            )


def test_actual_worker_roundtrip_and_readiness(databases):
    settings = load_settings()
    app = make_worker(settings)
    try:
        result = app.send_task("store_advisor.worker_probe")
        assert result.get(timeout=10) == {"status": "ok"}
        with TestClient(create_app(settings)) as client:
            health = client.get("/api/v1/health")
            assert health.status_code == 200
            assert health.json() == {"status": "ok"}
            assert client.get("/api/v1/ready").status_code == 200
        down = settings.model_copy(
            update={"redis_url": type(settings.redis_url)("redis://127.0.0.1:1/0")}
        )
        with TestClient(create_app(down)) as client:
            assert client.get("/api/v1/ready").status_code == 503
    finally:
        app.close()


def test_database_failure_keeps_health_alive_but_not_ready(databases):
    settings = load_settings()
    down = settings.model_copy(
        update={
            "database_url": type(settings.database_url)(
                "postgresql+psycopg://app_runtime:test-only@127.0.0.1:1/app_test"
            )
        }
    )
    with TestClient(create_app(down)) as client:
        assert client.get("/api/v1/health").status_code == 200
        assert client.get("/api/v1/ready").status_code == 503


def test_worker_on_another_environment_queue_does_not_make_api_ready(databases):
    settings = load_settings()
    assert settings.app_env == "test"
    # The real worker consumes store_advisor.test; staging has no consumer on this broker.
    wrong_queue = settings.model_copy(update={"app_env": "staging"})
    with TestClient(create_app(wrong_queue)) as client:
        assert client.get("/api/v1/health").status_code == 200
        assert client.get("/api/v1/ready").status_code == 503
