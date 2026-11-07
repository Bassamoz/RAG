import os

from alembic import context
from sqlalchemy import create_engine, pool, text
from store_advisor.config import validate_postgres_url
from store_advisor.migration_scope import include_app_name
from store_advisor.models import Base

try:
    url = validate_postgres_url(os.environ.get("MIGRATION_DATABASE_URL", ""))
except ValueError:
    raise RuntimeError("Invalid or missing configuration: MIGRATION_DATABASE_URL") from None

if context.is_offline_mode():
    context.configure(
        url=url,
        target_metadata=Base.metadata,
        literal_binds=True,
        include_schemas=True,
        include_name=include_app_name,
        version_table_schema="app",
    )
    with context.begin_transaction():
        context.execute("CREATE SCHEMA IF NOT EXISTS app")
        context.run_migrations()
else:
    engine = create_engine(url, poolclass=pool.NullPool, hide_parameters=True)
    with engine.connect() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS app"))
        connection.commit()
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
            include_schemas=True,
            include_name=include_app_name,
            version_table_schema="app",
        )
        with context.begin_transaction():
            context.run_migrations()
