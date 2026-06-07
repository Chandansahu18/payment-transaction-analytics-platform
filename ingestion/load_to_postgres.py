import pandas as pd
import psycopg2
import psycopg2.extras
import psycopg2.sql
from dotenv import load_dotenv
import logging
from typing import Optional
from .db_utils import get_db_connection
from . import watermark

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
            if 'transaction_ts' not in df.columns:
                raise ValueError(
                    f"'transaction_ts' column is required when incremental=True for table {table_name}"
                )

            # Normalize timestamp early
            df['transaction_ts'] = pd.to_datetime(df['transaction_ts'])

            last_ts = watermark.get_watermark(table_name)
            if last_ts:
                # Use >= for safe inclusive boundary
                df = df[df['transaction_ts'] >= last_ts]
                logger.info(f"Filtered to {len(df)} new records since last load")

            if df.empty:
                logger.info(f"No new data to load for {table_name}")
                return

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                columns = [psycopg2.sql.Identifier(col) for col in df.columns]
                cols_sql = psycopg2.sql.SQL(', ').join(columns)

                if conflict_column:
                    conflict_sql = psycopg2.sql.SQL("ON CONFLICT ({}) DO NOTHING").format(
                        psycopg2.sql.Identifier(conflict_column)
                    )
                else:
                    conflict_sql = psycopg2.sql.SQL("")

                query = psycopg2.sql.SQL(
                    "INSERT INTO {} ({}) VALUES %s {}"
                ).format(
                    psycopg2.sql.Identifier(table_name),
                    cols_sql,
                    conflict_sql
                )

                tuples = [tuple(x) for x in df.to_numpy()]
                psycopg2.extras.execute_values(cur, query, tuples)

                # Update watermark in the SAME transaction
                if incremental and not df.empty:
                    max_ts = df['transaction_ts'].max()
                    watermark.update_watermark(
                        table_name=table_name,
                        last_ts=max_ts,
                        rows_loaded=len(df),
                        cur=cur
                    )

                logger.info(f"Successfully loaded {len(df)} rows into {table_name}")

    except Exception as e:
        logger.error(f"Failed to load data into {table_name}: {e}")
        raise

if __name__ == "__main__":
    logger.info("Starting data ingestion into PostgreSQL...")

    load_data_to_postgres('data/raw/users.csv', 'raw.users', conflict_column='user_id')
    load_data_to_postgres('data/raw/merchants.csv', 'raw.merchants', conflict_column='merchant_id')

    load_data_to_postgres(
        csv_path='data/raw/transactions.csv',
        table_name='raw.transactions',
        incremental=True,
        conflict_column='transaction_id'
    )

    logger.info("Data ingestion completed successfully!")