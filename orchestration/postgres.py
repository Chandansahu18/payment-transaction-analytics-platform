from __future__ import annotations
import logging
import os
import time
import psycopg2
from psycopg2 import OperationalError
from prefect import task

logger = logging.getLogger(__name__)

_REQUIRED_ENV = (
    "POSTGRES_HOST",
    "POSTGRES_PORT",
    "POSTGRES_DB",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
)


@task(name="wait-for-postgres", retries=2, retry_delay_seconds=15, log_prints=True)
def wait_for_postgres(max_attempts: int = 30, delay_seconds: int = 2) -> None:
    missing = [name for name in _REQUIRED_ENV if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            f"Missing environment variables: {', '.join(missing)}. "
            "Copy .env.example to .env before running the flow."
        )

    last_error: OperationalError | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            with psycopg2.connect(
                host=os.environ["POSTGRES_HOST"],
                port=os.environ["POSTGRES_PORT"],
                dbname=os.environ["POSTGRES_DB"],
                user=os.environ["POSTGRES_USER"],
                password=os.environ["POSTGRES_PASSWORD"],
                connect_timeout=5,
            ):
                logger.info("PostgreSQL ready (attempt %s/%s)", attempt, max_attempts)
                return
        except OperationalError as exc:
            last_error = exc
            logger.warning(
                "PostgreSQL unavailable (attempt %s/%s): %s",
                attempt,
                max_attempts,
                exc,
            )
            time.sleep(delay_seconds)

    raise RuntimeError(
        f"PostgreSQL not available after {max_attempts} attempts"
    ) from last_error