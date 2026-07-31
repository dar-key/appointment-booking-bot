import logging
import os

from dotenv import load_dotenv

load_dotenv()


def require_env(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"{name} is not set")
    return value


BOT_TOKEN = require_env("BOT_TOKEN")
GOOGLE_SHEET_ID = require_env("GOOGLE_SHEET_ID")
GOOGLE_CREDENTIALS_FILE = require_env("GOOGLE_CREDENTIALS_FILE")
DB_PATH = require_env("DB_PATH")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
TIMEZONE = os.getenv("TIMEZONE", "UTC")

_admin_id_raw = os.getenv("ADMIN_ID")
ADMIN_ID = int(_admin_id_raw) if _admin_id_raw and _admin_id_raw.isdigit() else None

# Logging Setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
