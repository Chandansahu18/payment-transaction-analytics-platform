from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

_ENV_KEYS = (
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "DBT_SCHEMA",
)


def bootstrap_env() -> None:
    # Load .env and export variables required by Makefile subprocesses.
    load_dotenv(PROJECT_ROOT / ".env")
    for key in _ENV_KEYS:
        if value := os.getenv(key):
            os.environ[key] = value
    if password := os.getenv("POSTGRES_PASSWORD"):
        os.environ["PGPASSWORD"] = password