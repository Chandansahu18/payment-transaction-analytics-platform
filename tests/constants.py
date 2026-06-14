# thresholds aligned with generator/transaction_generator.py
from generator.transaction_generator import (
    TARGET_FRAUD_RATE_PCT,
    TARGET_FRAUD_TOLERANCE_PCT,
)

EXPECTED_USERS = 12_000
EXPECTED_MERCHANTS = 600
EXPECTED_TRANSACTIONS = 500_000
REQUIRED_CSV_FILES = ("users.csv", "merchants.csv", "transactions.csv")