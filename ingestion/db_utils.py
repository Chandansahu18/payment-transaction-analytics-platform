import psycopg2
from dotenv import load_dotenv
import os
import logging
from contextlib import contextmanager

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@contextmanager
def get_db_connection():
    """
    Context manager for PostgreSQL database connections.
    Ensures proper commit, rollback, and connection closing.
    """
    required_vars = [
        "POSTGRES_HOST", 
        "POSTGRES_PORT", 
        "POSTGRES_DB", 
        "POSTGRES_USER", 
        "POSTGRES_PASSWORD"
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Missing required environment variable: {var}")
        
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            connect_timeout=10
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