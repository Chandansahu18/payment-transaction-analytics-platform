import pandas as pd
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os
import logging
from typing import Optional
from watermark import get_watermark, update_watermark

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


def load_data_to_postgres(
    csv_path: str, 
    table_name: str, 
    incremental: bool = False,
    conflict_column: Optional[str] = None
):
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} rows from {csv_path}")

        if incremental:
            last_ts = get_watermark(table_name)
            if last_ts:
                df['transaction_ts'] = pd.to_datetime(df['transaction_ts'])
                df = df[df['transaction_ts'] > last_ts]
                logger.info(f"Filtered to {len(df)} new records")

            if df.empty:
                logger.info(f"No new data for {table_name}")
                return

        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                tuples = [tuple(x) for x in df.to_numpy()]
                cols = ','.join(df.columns)
                conflict_clause = f"ON CONFLICT ({conflict_column}) DO NOTHING" if conflict_column else ""

                query = f"INSERT INTO {table_name} ({cols}) VALUES %s {conflict_clause}"
                psycopg2.extras.execute_values(cur, query, tuples)

                if incremental and 'transaction_ts' in df.columns:
                    max_ts = df['transaction_ts'].max()
                    update_watermark(table_name, max_ts, len(df))

                logger.info(f"Loaded {len(df)} rows into {table_name}")

    except Exception as e:
        logger.error(f"Failed to load {table_name}: {e}")
        raise


if __name__ == "__main__":
    logger.info("Starting data ingestion...")

    load_data_to_postgres('data/raw/users.csv', 'raw.users')
    load_data_to_postgres('data/raw/merchants.csv', 'raw.merchants')

    load_data_to_postgres(
        csv_path='data/raw/transactions.csv',
        table_name='raw.transactions',
        incremental=True,
        conflict_column='transaction_id'
    )

    logger.info("Data ingestion completed successfully!")