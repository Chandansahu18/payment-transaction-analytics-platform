from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from constants import (
    EXPECTED_MERCHANTS,
    EXPECTED_TRANSACTIONS,
    EXPECTED_USERS,
    TARGET_FRAUD_RATE_PCT,
    TARGET_FRAUD_TOLERANCE_PCT,
)

from ingestion.load_to_postgres import load_data_to_postgres

RAW_TABLES = ("users", "merchants", "transactions", "watermark")


# Unit - loader contracts (no database required)
def test_incremental_load_requires_transaction_ts(tmp_path):
    csv_path = tmp_path / "invalid.csv"
    csv_path.write_text("user_id,amount\nUSR_00000001,100.00\n", encoding="utf-8")

    with pytest.raises(ValueError, match="transaction_ts"):
        load_data_to_postgres(
            str(csv_path),
            "raw.transactions",
            incremental=True,
            conflict_column="transaction_id",
        )


def test_csv_row_counts_match_generator_targets(require_csv_files):
    users = pd.read_csv(require_csv_files / "users.csv")
    merchants = pd.read_csv(require_csv_files / "merchants.csv")
    transactions = pd.read_csv(require_csv_files / "transactions.csv")

    assert len(users) == EXPECTED_USERS
    assert len(merchants) == EXPECTED_MERCHANTS
    assert len(transactions) == EXPECTED_TRANSACTIONS


def test_csv_transactions_have_required_columns(require_csv_files):
    df = pd.read_csv(require_csv_files / "transactions.csv", nrows=1000)

    required = {
        "transaction_id",
        "user_id",
        "merchant_id",
        "amount",
        "status",
        "is_fraud",
        "transaction_ts",
    }
    assert required.issubset(df.columns)


def test_csv_transaction_ids_are_unique(require_csv_files):
    df = pd.read_csv(require_csv_files / "transactions.csv", usecols=["transaction_id"])
    assert df["transaction_id"].is_unique


def test_csv_fraud_rate_within_generator_tolerance(require_csv_files):
    df = pd.read_csv(require_csv_files / "transactions.csv", usecols=["is_fraud"])
    fraud_rate_pct = df["is_fraud"].mean() * 100
    lower = TARGET_FRAUD_RATE_PCT - TARGET_FRAUD_TOLERANCE_PCT
    upper = TARGET_FRAUD_RATE_PCT + TARGET_FRAUD_TOLERANCE_PCT
    assert lower <= fraud_rate_pct <= upper

# Integration - raw schema in PostgreSQL (requires make up + make ingest)
def test_raw_schema_exists(db_cursor):
    db_cursor.execute(
        "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'raw'"
    )
    assert db_cursor.fetchone() is not None


@pytest.mark.parametrize("table_name", RAW_TABLES)
def test_raw_tables_exist(db_cursor, table_name: str):
    db_cursor.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'raw' AND table_name = %s
        """,
        (table_name,),
    )
    assert db_cursor.fetchone() is not None


def test_raw_users_row_count(db_cursor):
    db_cursor.execute("SELECT COUNT(*) FROM raw.users")
    (count,) = db_cursor.fetchone()
    assert count == EXPECTED_USERS


def test_raw_merchants_row_count(db_cursor):
    db_cursor.execute("SELECT COUNT(*) FROM raw.merchants")
    (count,) = db_cursor.fetchone()
    assert count == EXPECTED_MERCHANTS


def test_raw_transactions_row_count(db_cursor):
    db_cursor.execute("SELECT COUNT(*) FROM raw.transactions")
    (count,) = db_cursor.fetchone()
    assert count == EXPECTED_TRANSACTIONS


def test_raw_transactions_primary_key_unique(db_cursor):
    db_cursor.execute(
        """
        SELECT COUNT(*) - COUNT(DISTINCT transaction_id)
        FROM raw.transactions
        """
    )
    (duplicates,) = db_cursor.fetchone()
    assert duplicates == 0


def test_raw_transactions_no_null_keys(db_cursor):
    db_cursor.execute(
        """
        SELECT COUNT(*)
        FROM raw.transactions
        WHERE transaction_id IS NULL
           OR user_id IS NULL
           OR merchant_id IS NULL
           OR transaction_ts IS NULL
        """
    )
    (null_keys,) = db_cursor.fetchone()
    assert null_keys == 0


def test_raw_transactions_referential_integrity(db_cursor):
    db_cursor.execute(
        """
        SELECT COUNT(*)
        FROM raw.transactions t
        LEFT JOIN raw.users u ON t.user_id = u.user_id
        WHERE u.user_id IS NULL
        """
    )
    (orphan_users,) = db_cursor.fetchone()
    assert orphan_users == 0

    db_cursor.execute(
        """
        SELECT COUNT(*)
        FROM raw.transactions t
        LEFT JOIN raw.merchants m ON t.merchant_id = m.merchant_id
        WHERE m.merchant_id IS NULL
        """
    )
    (orphan_merchants,) = db_cursor.fetchone()
    assert orphan_merchants == 0


def test_raw_transaction_status_values_valid(db_cursor):
    db_cursor.execute(
        """
        SELECT DISTINCT status
        FROM raw.transactions
        WHERE status NOT IN ('success', 'failed', 'declined', 'disputed')
           OR status IS NULL
        """
    )
    invalid = db_cursor.fetchall()
    assert invalid == []


def test_watermark_table_has_transaction_entry(db_cursor):
    db_cursor.execute(
        """
        SELECT last_loaded_ts, rows_loaded
        FROM raw.watermark
        WHERE table_name = 'raw.transactions'
        """
    )
    row = db_cursor.fetchone()
    assert row is not None
    last_loaded_ts, rows_loaded = row
    assert last_loaded_ts is not None
    assert rows_loaded == EXPECTED_TRANSACTIONS


def test_watermark_last_loaded_ts_matches_max_transaction_ts(db_cursor):
    db_cursor.execute("SELECT MAX(transaction_ts) FROM raw.transactions")
    (max_txn_ts,) = db_cursor.fetchone()

    db_cursor.execute(
        """
        SELECT last_loaded_ts
        FROM raw.watermark
        WHERE table_name = 'raw.transactions'
        """
    )
    row = db_cursor.fetchone()
    assert row is not None
    (watermark_ts,) = row
    assert watermark_ts == max_txn_ts