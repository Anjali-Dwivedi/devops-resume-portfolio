from __future__ import annotations

import json
import os
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


ALLOWED_ENVIRONMENTS = {"dev", "sit", "uat", "prod"}


class Settings(BaseModel):
    environment: str = Field(default="dev")
    ready: bool = True
    database_url: str = Field(default="sqlite:///./demo.db")
    feature_flags: dict[str, bool] = Field(default_factory=dict)

    @field_validator("environment")
    @classmethod
    def _env_ok(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in ALLOWED_ENVIRONMENTS:
            raise ValueError(
                f"environment must be one of {sorted(ALLOWED_ENVIRONMENTS)}, got {value!r}"
            )
        return normalized


def load_settings(config_path: str | None = None) -> Settings:
    """Load settings from env and optional JSON config file.

    Used both at runtime and by the config-validation quality gate.
    """
    path = config_path or os.getenv("APP_CONFIG_PATH")
    data: dict = {}
    if path:
        raw = Path(path).read_text(encoding="utf-8")
        data = json.loads(raw)
    # Environment variables override file values (12-factor style).
    if os.getenv("APP_ENVIRONMENT"):
        data["environment"] = os.environ["APP_ENVIRONMENT"]
    if os.getenv("APP_READY") is not None:
        data["ready"] = os.environ["APP_READY"].lower() in {"1", "true", "yes"}
    if os.getenv("DATABASE_URL"):
        data["database_url"] = os.environ["DATABASE_URL"]
    return Settings(**data)


def validate_config_file(path: str) -> Settings:
    """Strict validation entrypoint for CI gates."""
    settings = load_settings(path)
    if settings.environment == "prod" and settings.database_url.startswith("sqlite:"):
        raise ValueError("prod environment cannot use sqlite database_url")
    return settings
