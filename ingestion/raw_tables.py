import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def create_raw_tables():
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    cur = conn.cursor()

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
            user_id VARCHAR(20) NOT NULL,
            merchant_id VARCHAR(20) NOT NULL,
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

    # Watermark Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw._watermark (
            table_name VARCHAR(50) PRIMARY KEY,
            last_loaded_ts TIMESTAMP,
            rows_loaded INT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Raw tables and watermark table created successfully!")

if __name__ == "__main__":
    create_raw_tables()