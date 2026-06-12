import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ingestion.db_utils import get_db_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SQL_DIR = Path(__file__).resolve().parent
REPORTING_SCHEMA = "reporting"

VIEW_FILES = [
    "hourly_fraud_trends.sql",
    "merchant_risk_profiling.sql",
    "fraud_customer_segments.sql",
    "cohort_analysis.sql",
    "velocity_anomaly_detection.sql",
]

EXPECTED_VIEWS = [
    f"{REPORTING_SCHEMA}.hourly_fraud_trends",
    f"{REPORTING_SCHEMA}.merchant_risk_profiling",
    f"{REPORTING_SCHEMA}.fraud_customer_segments",
    f"{REPORTING_SCHEMA}.cohort_analysis",
    f"{REPORTING_SCHEMA}.velocity_anomaly_detection",
]


def deploy_views() -> None:
    missing = [name for name in VIEW_FILES if not (SQL_DIR / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing SQL view files: {', '.join(missing)}")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {REPORTING_SCHEMA}")
            logger.info("Ensured %s schema exists", REPORTING_SCHEMA)

            for filename in VIEW_FILES:
                sql = (SQL_DIR / filename).read_text(encoding="utf-8")
                logger.info("Deploying %s", filename)
                cur.execute(sql)

            logger.info("Verifying deployed views in %s schema...", REPORTING_SCHEMA)
            for qualified_name in EXPECTED_VIEWS:
                schema, view_name = qualified_name.split(".")
                cur.execute(
                    """
                    SELECT 1
                    FROM information_schema.views
                    WHERE table_schema = %s AND table_name = %s
                    """,
                    (schema, view_name),
                )
                if cur.fetchone() is None:
                    raise RuntimeError(f"View not found after deploy: {qualified_name}")

    logger.info(
        "Successfully deployed %d reporting views to %s schema.",
        len(EXPECTED_VIEWS),
        REPORTING_SCHEMA,
    )


if __name__ == "__main__":
    deploy_views()