"""Shared fixtures for ingestion and pipeline quality tests."""

from __future__ import annotations

import os
from pathlib import Path

import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from constants import REQUIRED_CSV_FILES  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"


def _postgres_env_ready() -> bool:
    required = (
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    )
    return all(os.getenv(var) for var in required)


@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def data_raw_dir() -> Path:
    return DATA_RAW_DIR


@pytest.fixture(scope="session")
def require_csv_files(data_raw_dir: Path) -> Path:
    missing = [name for name in REQUIRED_CSV_FILES if not (data_raw_dir / name).exists()]
    if missing:
        pytest.skip(f"Missing CSV files in data/raw/: {', '.join(missing)}. Run: make ingest")
    return data_raw_dir


@pytest.fixture
def db_cursor():
    """Read-only database cursor; skips when PostgreSQL is unreachable."""
    if not _postgres_env_ready():
        pytest.skip("PostgreSQL env vars not set — copy .env.example to .env")

    from ingestion.db_utils import get_db_connection

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                yield cur
    except Exception as exc:
        pytest.skip(f"PostgreSQL not available: {exc}")