import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ingestion.db_utils import get_db_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def reset_raw_tables() -> None:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE raw.transactions, raw.users, raw.merchants CASCADE;")
            cur.execute("TRUNCATE raw.watermark;")
    logger.info("Raw tables and watermark truncated.")


if __name__ == "__main__":
    reset_raw_tables()