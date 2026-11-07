FROM ghcr.io/astral-sh/uv:0.13.7 AS uv
FROM python:3.13-slim
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
COPY apps/api/pyproject.toml apps/api/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY apps/api/src ./src
COPY apps/api/migrations ./migrations
COPY apps/api/alembic.ini ./
RUN uv sync --frozen --no-dev && useradd --uid 10001 --create-home app
USER app
EXPOSE 8000
CMD [".venv/bin/uvicorn", "store_advisor.main:create_app", "--factory", "--host", "0.0.0.0", "--no-access-log"]
