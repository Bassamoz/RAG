"""Export the app's schema without a DB, broker or embedded credentials."""

import json
from pathlib import Path

from store_advisor.config import Settings
from store_advisor.main import create_app

settings = Settings(
    database_url="postgresql+psycopg://localhost/schema_only",
    redis_url="redis://localhost:1/0",
    app_env="test",
)
output = Path(__file__).resolve().parents[1] / "packages/api-client/openapi.json"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(
    json.dumps(create_app(settings).openapi(), ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print("Exported OpenAPI without contacting services")
