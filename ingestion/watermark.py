from dotenv import load_dotenv
import logging
from datetime import datetime
from typing import Optional
from .db_utils import get_db_connection

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_watermark(table_name: str) -> Optional[datetime]:
    """Get the last loaded timestamp for incremental loading"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT last_loaded_ts 
                FROM raw._watermark 
                WHERE table_name = %s
            """, (table_name,))
            result = cur.fetchone()
            return result[0] if result else None

def update_watermark(
    table_name: str, 
    last_ts: datetime, 
    rows_loaded: int, 
    cur=None
):
    if cur:
        # Use existing cursor
        cur.execute("""
            INSERT INTO raw._watermark (table_name, last_loaded_ts, rows_loaded, updated_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (table_name) 
            DO UPDATE SET 
                last_loaded_ts = EXCLUDED.last_loaded_ts,
                rows_loaded = EXCLUDED.rows_loaded,
                updated_at = EXCLUDED.updated_at;
        """, (table_name, last_ts, rows_loaded, datetime.now()))
    else:
        # Create new connection
        with get_db_connection() as conn:
            with conn.cursor() as new_cur:
                new_cur.execute("""
                    INSERT INTO raw._watermark (table_name, last_loaded_ts, rows_loaded, updated_at)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (table_name) 
                    DO UPDATE SET 
                        last_loaded_ts = EXCLUDED.last_loaded_ts,
                        rows_loaded = EXCLUDED.rows_loaded,
                        updated_at = EXCLUDED.updated_at;
                """, (table_name, last_ts, rows_loaded, datetime.now()))

    logger.info(f"Watermark updated → {table_name} | Rows: {rows_loaded}")