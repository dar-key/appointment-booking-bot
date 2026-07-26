import gspread_asyncio
from google.oauth2.service_account import Credentials
from src.bot.config import GOOGLE_SHEET_ID, logger


def get_creds():
    return Credentials.from_service_account_file(
        "credentials.json",
        scopes=[
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ],
    )


agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)


async def get_booked_slots(date: str) -> list[str]:
    try:
        agc = await agcm.authorize()
        spreadsheet = await agc.open_by_key(GOOGLE_SHEET_ID)
        worksheet = await spreadsheet.get_worksheet(0)
        records = await worksheet.get_all_records()
        return [str(row["Time"]) for row in records if str(row["Date"]) == date]
    except Exception as e:
        logger.error(f"Failed to read from Google Sheets: {e}")
        return []


async def save_booking_to_sheets(
    user_id: int, username: str, phone: str, service: str, date: str, time: str
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
    except Exception as e:
        logger.error(f"Failed to write to Google Sheets: {e}")
        raise e
