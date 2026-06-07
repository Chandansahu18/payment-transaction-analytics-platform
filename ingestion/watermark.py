import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

def get_watermark(table_name):
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT last_loaded_ts 
        FROM raw._watermark 
        WHERE table_name = %s
    """, (table_name,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else None


def update_watermark(table_name, last_ts, rows_loaded):
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO raw._watermark (table_name, last_loaded_ts, rows_loaded, updated_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (table_name) 
        DO UPDATE SET 
            last_loaded_ts = EXCLUDED.last_loaded_ts,
            rows_loaded = EXCLUDED.rows_loaded,
            updated_at = EXCLUDED.updated_at;
    """, (table_name, last_ts, rows_loaded, datetime.now()))
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Watermark updated → {table_name} | Rows loaded: {rows_loaded}")