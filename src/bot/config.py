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

# App Constants
SERVICES = ["Haircut ($20)", "Manicure ($15)", "Massage ($35)"]
TIME_SLOTS = ["10:00", "12:00", "14:00", "16:00", "18:00"]

# Logging Setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
