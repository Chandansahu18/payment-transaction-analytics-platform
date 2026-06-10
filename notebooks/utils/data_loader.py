import logging

import pandas as pd

logger = logging.getLogger(__name__)

MARTS_SOURCE_LABEL = "marts.fct_transactions (+ dim_users, dim_merchants)"

WAREHOUSE_MERGED_SQL = """
SELECT
    f.transaction_id,
    u.user_id,
    m.merchant_id,
    f.merchant_category,
    f.payment_method,
    f.amount,
    f.currency,
    f.status,
    f.is_fraud,
    f.device_type,
    f.city,
    f.state,
    f.transaction_ts
FROM marts.fct_transactions f
LEFT JOIN marts.dim_users u ON f.user_sk = u.user_sk
LEFT JOIN marts.dim_merchants m ON f.merchant_sk = m.merchant_sk
"""


def _prepare_merged_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["transaction_ts"] = pd.to_datetime(df["transaction_ts"])
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["is_fraud"] = df["is_fraud"].astype(bool)
    df["month"] = df["transaction_ts"].dt.to_period("M").astype(str)
    df["is_success"] = df["status"].eq("success")
    return df


def warehouse_available() -> bool:
    from notebooks.utils.db_connector import get_db_connection

    try:
        with get_db_connection():
            return True
    except Exception:
        return False


def query_warehouse(sql: str) -> pd.DataFrame:
    """Query Postgres warehouse via psycopg2 (no SQLAlchemy)."""
    from notebooks.utils.db_connector import get_db_connection

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            description = cur.description
            if description is None:
                return pd.DataFrame()
            cols = [d[0] for d in description]
            rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)


def _warehouse_numeric(sql: str, column: str | None = None) -> float:
    """First cell of a one-row warehouse query as a plain Python float."""
    frame = query_warehouse(sql)
    col = column or str(frame.columns[0])
    values = pd.to_numeric(frame[col], errors="coerce").to_numpy(dtype=float, na_value=float("nan"))
    return float(values[0])


def warehouse_scalar(sql: str, column: str | None = None) -> float:
    """Return a single numeric value from a one-row warehouse query."""
    return _warehouse_numeric(sql, column)


def warehouse_count(sql: str) -> int:
    """Return a single integer count from a one-row warehouse query."""
    return int(_warehouse_numeric(sql))


def get_merged_data() -> tuple[pd.DataFrame, str]:
    """Load domain EDA data from marts only. Requires Docker + dbt build."""
    if not warehouse_available():
        raise ConnectionError("Warehouse unavailable — run: make docker-up && make build")

    df = query_warehouse(WAREHOUSE_MERGED_SQL)
    df = _prepare_merged_df(df)
    logger.info("Loaded %s transactions from %s", f"{len(df):,}", MARTS_SOURCE_LABEL)
    return df, MARTS_SOURCE_LABEL


def print_data_sanity(df: pd.DataFrame, source: str) -> None:
    """Light pre-EDA sanity check — row count, date range, core rates."""
    print(f"Source       : {source}")
    print(f"Rows         : {len(df):,}")
    print(f"Date range   : {df['transaction_ts'].min()} → {df['transaction_ts'].max()}")
    print(f"Success rate : {df['is_success'].mean():.1%}")
    if "is_fraud" in df.columns:
        print(f"Fraud rate   : {df['is_fraud'].mean():.2%}")
        fraud_loss = df.loc[df["is_fraud"], "amount"].sum()
        print(f"Fraud loss   : ₹{fraud_loss:,.0f}")