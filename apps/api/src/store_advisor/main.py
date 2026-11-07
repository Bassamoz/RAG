from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from redis import Redis
from sqlalchemy import text
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from store_advisor.config import Settings, load_settings
from store_advisor.db import make_engine
from store_advisor.http import RequestBoundary, error_response
from store_advisor.worker import make_worker


class Health(BaseModel):
    status: Literal["ok"] = "ok"


class ErrorDetail(BaseModel):
    code: str
    message: str
    trace_id: str


class ErrorEnvelope(BaseModel):
    error: ErrorDetail


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    engine = make_engine(settings)
    redis = Redis.from_url(
        settings.redis_url.get_secret_value(), socket_connect_timeout=1, socket_timeout=1
    )
    worker = make_worker(settings)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # https://fastapi.tiangolo.com/advanced/events/ — shared resources have bounded lifetime.
        yield
        engine.dispose()
        redis.close()
        worker.close()

    app = FastAPI(
        title="Store Advisor API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None if settings.app_env in {"staging", "prod"} else "/docs",
        redoc_url=None,
        openapi_url="/api/v1/openapi.json",
        responses={
            413: {"model": ErrorEnvelope},
            422: {"model": ErrorEnvelope},
            500: {"model": ErrorEnvelope},
        },
    )
    app.add_middleware(RequestBoundary, max_body_bytes=settings.max_body_bytes)

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, error: HTTPException) -> JSONResponse:
        code = "NOT_FOUND" if error.status_code == 404 else "REQUEST_REJECTED"
        return error_response(error.status_code, code, "Request rejected", request.state.request_id)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, error: RequestValidationError) -> JSONResponse:
        return error_response(422, "VALIDATION_ERROR", "Invalid request", request.state.request_id)

    @app.get("/api/v1/health", response_model=Health, operation_id="health")
    def health() -> Health:
        return Health()

    @app.get(
        "/api/v1/ready",
        response_model=Health,
        operation_id="readiness",
        responses={503: {"model": ErrorEnvelope}},
    )
    def readiness(request: Request) -> Health | JSONResponse:
        try:
            with engine.connect() as connection:
                role = connection.execute(
                    text(
                        "SELECT rolsuper OR rolbypassrls OR rolcreatedb OR rolcreaterole "
                        "OR rolname <> 'app_runtime' FROM pg_roles WHERE rolname=current_user"
                    )
                ).scalar_one()
                if (
                    role
                    or connection.execute(
                        text("SELECT version_num FROM app.alembic_version")
                    ).scalar_one()
                    != "0001"
                ):
                    raise RuntimeError("unsafe role or migration not ready")
            if not redis.ping():
                raise RuntimeError("dependency unavailable")
            # A worker on this broker may consume a different environment's queue.
            # active_queues verifies that a responding consumer can accept our tasks.
            # https://docs.celeryq.dev/en/stable/userguide/monitoring.html
            queues = worker.control.inspect(timeout=1).active_queues() or {}
            if not any(
                queue.get("name") == worker.conf.task_default_queue
                for worker_queues in queues.values()
                for queue in worker_queues
            ):
                raise RuntimeError("worker queue unavailable")
        except Exception:
            return error_response(
                503, "DEPENDENCY_UNAVAILABLE", "Service is not ready", request.state.request_id
            )
        return Health()

    return app
