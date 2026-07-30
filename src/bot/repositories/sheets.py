import gspread_asyncio
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError, GSpreadException
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.bot.config import GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEET_ID, logger

# If the sheet is ever exported to CSV and opened elsewhere, a value like
# "+1234567" phone numbers would otherwise be read as a formula.
# Neutralize this at write time so the exported file is safe too.
_FORMULA_TRIGGER_CHARS = ("=", "+", "-", "@")


def _sheet_safe(value: str) -> str:
    if value and value[0] in _FORMULA_TRIGGER_CHARS:
        return f"'{value}"
    return value


def get_creds():
    return Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_FILE,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
        ],
    )


agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)


# Retry up to 3 times with exponential backoff (2s, 4s, 8s) if a GSpread exception occurs
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(GSpreadException),
    reraise=True,  # Reraise exception if all 3 retries fail
)
async def save_booking_to_sheets_with_retry(*args, **kwargs):
    return await save_booking_to_sheets(*args, **kwargs)


async def save_booking_to_sheets(
    user_id: int, username: str | None, phone: str, service: str, date: str, time: str
):
    try:
        agc = await agcm.authorize()
        spreadsheet = await agc.open_by_key(GOOGLE_SHEET_ID)
        worksheet = await spreadsheet.get_worksheet(0)
        row_data = [
            user_id,
            f"@{username}" if username else "N/A",
            _sheet_safe(phone),
            service,
            date,
            time,
        ]
        await worksheet.append_row(row_data)
        logger.info(f"Successfully saved booking for {user_id} in Google Sheets.")
    except (APIError, GSpreadException) as e:
        logger.error(f"Failed to write to Google Sheets: {e}")
        raise
