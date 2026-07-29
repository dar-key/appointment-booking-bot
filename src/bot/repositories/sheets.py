import gspread_asyncio
from google.oauth2.service_account import Credentials
from gspread.exceptions import APIError, GSpreadException

from src.bot.config import GOOGLE_CREDENTIALS_FILE, GOOGLE_SHEET_ID, logger


def get_creds():
    return Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_FILE,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
        ],
    )


agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)


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
            phone,
            service,
            date,
            time,
        ]
        await worksheet.append_row(row_data)
        logger.info(f"Successfully saved booking for {user_id} in Google Sheets.")
    except (APIError, GSpreadException) as e:
        logger.error(f"Failed to write to Google Sheets: {e}")
        raise
