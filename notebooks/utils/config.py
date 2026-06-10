from pathlib import Path
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]

load_dotenv(ROOT / '.env')

DATA_RAW        = ROOT / 'data' / 'raw'
SCREENSHOTS_DIR = ROOT / 'dashboard' / 'screenshots'
CHARTS_DIR      = ROOT / 'notebooks' / 'charts'

for _dir in [DATA_RAW, SCREENSHOTS_DIR, CHARTS_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)


def _get_port() -> int:
    port_str = os.getenv('POSTGRES_PORT') or os.getenv('DB_PORT') or '5432'
    try:
        return int(port_str)
    except ValueError:
        logger.warning("Invalid port '%s', using default 5432", port_str)
        return 5432


DB_CONFIG = {
    'host'    : os.getenv('POSTGRES_HOST',     os.getenv('DB_HOST',     'localhost')),
    'port'    : _get_port(),
    'dbname'  : os.getenv('POSTGRES_DB',       os.getenv('DB_NAME',     'payment_transaction_warehouse')),
    'user'    : os.getenv('POSTGRES_USER',     os.getenv('DB_USER',     'postgres')),
    'password': os.getenv('POSTGRES_PASSWORD', os.getenv('DB_PASSWORD', '')),
}