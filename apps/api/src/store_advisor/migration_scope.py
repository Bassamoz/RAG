"""Keep Alembic autogeneration out of provider-owned Supabase schemas."""

from collections.abc import Mapping


def include_app_name(name: str | None, type_: str, parent_names: Mapping[str, str | None]) -> bool:
    if type_ == "schema":
        return name == "app"
    return parent_names.get("schema_name") == "app"
