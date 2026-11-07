"""Validate configuration without echoing secret input in startup errors."""

from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


class ConfigurationError(RuntimeError):
    pass


def validate_postgres_url(value: str) -> str:
    """Shared by runtime and Alembic; parser exceptions must not echo a DSN fragment."""
    try:
        url = make_url(value)
        if url.drivername != "postgresql+psycopg" or not url.host or not url.database:
            raise ValueError()
        if url.port is not None and not 1 <= url.port <= 65535:
            raise ValueError()
    except (ValueError, TypeError, ArgumentError):
        raise ValueError("requires a valid PostgreSQL psycopg URL") from None
    return value


class Settings(BaseSettings):
    # Explicit environment injection; no implicit reading of an arbitrary working-directory .env.
    model_config = SettingsConfigDict(extra="ignore", hide_input_in_errors=True)
    app_env: Literal["dev", "test", "staging", "prod"] = "dev"
    app_profile: Literal["research", "production"] = "production"
    database_url: SecretStr
    redis_url: SecretStr
    max_body_bytes: int = Field(default=1_048_576, ge=1, le=20_971_520)

    @field_validator("database_url")
    @classmethod
    def postgres_only(cls, value: SecretStr) -> SecretStr:
        validate_postgres_url(value.get_secret_value())
        return value

    @field_validator("redis_url")
    @classmethod
    def redis_only(cls, value: SecretStr) -> SecretStr:
        try:
            url = urlsplit(value.get_secret_value())
            if url.scheme not in {"redis", "rediss"} or not url.hostname:
                raise ValueError()
            if url.port is not None and not 1 <= url.port <= 65535:
                raise ValueError()
            if url.path.strip("/") and not url.path.strip("/").isdigit():
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError("requires a valid Redis URL") from None
        return value


def load_settings() -> Settings:
    # Source: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
    try:
        return Settings()
    except ValidationError as error:
        fields = sorted({str(part).upper() for item in error.errors() for part in item["loc"]})
        raise ConfigurationError("Invalid or missing configuration: " + ", ".join(fields)) from None
