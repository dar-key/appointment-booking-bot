import logging
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

if not BOT_TOKEN or not GOOGLE_SHEET_ID:
    raise ValueError("Missing BOT_TOKEN or GOOGLE_SHEET_ID in environment variables.")

# App Constants
SERVICES = ["Haircut ($20)", "Manicure ($15)", "Massage ($35)"]
TIME_SLOTS = ["10:00", "12:00", "14:00", "16:00", "18:00"]

# Logging Setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
