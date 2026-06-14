from __future__ import annotations
from prefect import flow, get_run_logger
from orchestration.config import bootstrap_env
from orchestration.postgres import wait_for_postgres
from orchestration.shell import run_make


@flow(name="payment-analytics-pipeline", log_prints=True)
def payment_analytics_pipeline(
    ensure_postgres_up: bool = True,
    run_setup_db: bool = True,
    skip_ingest: bool = False,
    skip_pytest: bool = False,
    skip_dbt_tests: bool = False,
) -> None:
    bootstrap_env()
    logger = get_run_logger()

    if ensure_postgres_up:
        run_make("up", description="Start PostgreSQL")
        wait_for_postgres()

    if run_setup_db:
        run_make("setup-db", description="Configure database")

    if skip_ingest:
        logger.info("Skipping ingest")
    else:
        run_make("ingest", description="Load raw data")

    if skip_pytest:
        logger.info("Skipping pytest")
    else:
        run_make("pytest", description="Run ingestion tests")

    run_make("pipeline", description="Run dbt pipeline")

    if skip_dbt_tests:
        logger.info("Skipping dbt tests")
    else:
        run_make("test", description="Run dbt tests")


if __name__ == "__main__":
    payment_analytics_pipeline()