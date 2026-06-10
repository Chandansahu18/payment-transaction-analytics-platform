from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]

load_dotenv(ROOT / '.env')

DATA_RAW        = ROOT / 'data' / 'raw'
SCREENSHOTS_DIR = ROOT / 'dashboard' / 'screenshots'
CHARTS_DIR      = ROOT / 'notebooks' / 'charts'

for _dir in [DATA_RAW, SCREENSHOTS_DIR, CHARTS_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)

DB_CONFIG = {
    'host'    : os.getenv('POSTGRES_HOST',     os.getenv('DB_HOST',     'localhost')),
    'port'    : int(os.getenv('POSTGRES_PORT', os.getenv('DB_PORT', '5432'))),
    'dbname'  : os.getenv('POSTGRES_DB',       os.getenv('DB_NAME',     'payment_transaction_warehouse')),
    'user'    : os.getenv('POSTGRES_USER',     os.getenv('DB_USER',     'postgres')),
    'password': os.getenv('POSTGRES_PASSWORD', os.getenv('DB_PASSWORD', '')),
}