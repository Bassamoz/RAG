"""Read-only final check; log counts/versions only, never environment values or rows."""

import json
from pathlib import Path

from sqlalchemy import create_engine, text

values = dict(
    line.split("=", 1)
    for line in Path(".env.dev").read_text().splitlines()
    if "=" in line and not line.startswith("#")
)
engine = create_engine(values["MIGRATION_DATABASE_URL"], hide_parameters=True)
try:
    with engine.connect() as connection:
        counts = {
            name: connection.execute(text("SELECT count(*) FROM app." + name)).scalar_one()
            for name in ["users", "tenants", "memberships", "stores"]
        }
        result = {
            "foundation_rows_after_cleanup": counts,
            "alembic_revision": connection.execute(
                text("SELECT version_num FROM app.alembic_version")
            ).scalar_one(),
            "pgvector_version": connection.execute(
                text("SELECT extversion FROM pg_extension WHERE extname='vector'")
            ).scalar_one(),
            "provider_schemas": list(
                connection.execute(
                    text(
                        "SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name IN ('auth','storage') ORDER BY schema_name"
                    )
                ).scalars()
            ),
        }
        assert result["alembic_revision"] == "0001"
        # This check belongs to this fresh bootstrap, whose initial rows were all zero.
        # It never deletes or repairs data if another run has since populated the app.
        assert all(value == 0 for value in counts.values())
        assert result["provider_schemas"] == ["auth", "storage"]
    print(json.dumps(result))
finally:
    engine.dispose()
