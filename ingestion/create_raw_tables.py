from dotenv import load_dotenv
from .db_utils import get_db_connection
import logging

load_dotenv()  

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_raw_tables():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Create schema
                cur.execute("CREATE SCHEMA IF NOT EXISTS raw;")

                # Users Table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS raw.users (
                        user_id VARCHAR(20) PRIMARY KEY,
                        age_group VARCHAR(10) NOT NULL,
                        account_type VARCHAR(10) NOT NULL,
                        registration_date DATE,
                        city VARCHAR(50),
                        state VARCHAR(50)
                    );
                """)

                # Merchants Table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS raw.merchants (
                        merchant_id VARCHAR(20) PRIMARY KEY,
                        merchant_name VARCHAR(100) NOT NULL,
                        merchant_category VARCHAR(30) NOT NULL,
                        city VARCHAR(50),
                        state VARCHAR(50),
                        onboarding_date DATE
                    );
                """)

                # Transactions Table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS raw.transactions (
                        transaction_id UUID PRIMARY KEY,
                        user_id VARCHAR(20) NOT NULL REFERENCES raw.users(user_id),
                        merchant_id VARCHAR(20) NOT NULL REFERENCES raw.merchants(merchant_id),
                        merchant_category VARCHAR(30),
                        payment_method VARCHAR(20),
                        amount NUMERIC(12,2),
                        currency VARCHAR(5) DEFAULT 'INR',
                        status VARCHAR(20),
                        is_fraud_flag BOOLEAN,
                        device_type VARCHAR(20),
                        city VARCHAR(50),
                        state VARCHAR(50),
                        transaction_ts TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

                # Indexes for performance
                cur.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON raw.transactions(user_id);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_transactions_merchant_id ON raw.transactions(merchant_id);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_transactions_ts ON raw.transactions(transaction_ts);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_transactions_status ON raw.transactions(status);")

                # Watermark Table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS raw._watermark (
                        table_name VARCHAR(50) PRIMARY KEY,
                        last_loaded_ts TIMESTAMP,
                        rows_loaded INT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

        logger.info("Raw tables, indexes, and watermark table created successfully!")

    except Exception as e:
        logger.error(f"Failed to create raw tables: {e}")
        raise

if __name__ == "__main__":
    create_raw_tables()