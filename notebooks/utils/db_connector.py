import psycopg2
from contextlib import contextmanager
import logging
from notebooks.utils.config import DB_CONFIG

logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            connect_timeout=10,
        )
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()
