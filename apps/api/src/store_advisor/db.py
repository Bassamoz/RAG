"""Transaction-scoped tenant context; only authenticated services may call scoped_session."""

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import UUID

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session

from store_advisor.config import Settings


def make_engine(settings: Settings) -> Engine:
    return create_engine(
        settings.database_url.get_secret_value(),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        connect_args={"connect_timeout": 2, "options": "-c statement_timeout=3000"},
        hide_parameters=True,
    )


@contextmanager
def scoped_session(
    engine: Engine, *, user_id: UUID, tenant_id: UUID, store_id: UUID | None = None
) -> Iterator[Session]:
    """Set transaction-local context after membership validation, never from raw HTTP input.

    RLS is a second boundary. This helper cannot authenticate a user; phase 02 owns that gate.
    See https://docs.sqlalchemy.org/en/20/orm/session_transaction.html.
    """
    with Session(engine) as session, session.begin():
        session.execute(
            text(
                "SELECT set_config('app.user_id', :user_id, true), "
                "set_config('app.tenant_id', :tenant_id, true), "
                "set_config('app.store_id', :store_id, true)"
            ),
            {
                "user_id": str(user_id),
                "tenant_id": str(tenant_id),
                "store_id": str(store_id) if store_id else "",
            },
        )
        yield session
