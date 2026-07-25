import asyncio
import logging
import os
import re
import gspread_asyncio
from google.oauth2.service_account import Credentials
from aiogram import F, Bot, Dispatcher
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from dotenv import load_dotenv
from aiogram.client.session.aiohttp import AiohttpSession

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")


if not BOT_TOKEN or not GOOGLE_SHEET_ID:
    print("Error: BOT_TOKEN or GOOGLE_SHEET_ID couldn't load.")
    exit()


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# session = AiohttpSession(proxy="http://proxy.server:3128")
bot = Bot(token=BOT_TOKEN)  # , session=session)
dp = Dispatcher()


def get_creds():
    return Credentials.from_service_account_file(
        "credentials.json",
        scopes=[
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ],
    )


agcm = gspread_asyncio.AsyncioGspreadClientManager(get_creds)


SERVICES = ["Стрижка (5000 ₸)", "Маникюр (4000 ₸)", "Массаж (8000 ₸)"]
TIME_SLOTS = ["10:00", "12:00", "14:00", "16:00", "18:00"]


class BookingState(StatesGroup):
    choosing_service = State()
    choosing_date = State()
    choosing_time = State()
    entering_phone = State()


async def get_booked_slots(date: str) -> list:
    try:
        agc = await agcm.authorize()
        spreadsheet = await agc.open_by_key(GOOGLE_SHEET_ID)
        worksheet = await spreadsheet.get_worksheet(0)

        # Get all records from sheet (each row is a list of cells)
        records = await worksheet.get_all_records()

        # Filter slots that are booked on the requested date
        booked_slots = [row["Time"] for row in records if str(row["Date"]) == date]
        return booked_slots
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

        # Format of the row to append
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


# Dispatcher
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Записаться на услугу", callback_data="start_booking"
                )
            ]
        ]
    )

    await message.answer(
        "Добро пожаловать в наш салон!\n\nНажмите кнопку ниже, чтобы выбрать удобное время для записи",
        reply_markup=keyboard,
    )


@dp.callback_query(F.data == "start_booking")
async def process_start_booking(cb: CallbackQuery, state: FSMContext):

    buttons = [
        [InlineKeyboardButton(text=service, callback_data=f"service:{service}")]
        for service in SERVICES
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await cb.message.edit_text(
        "шаг 1/4: Выберите интересующую вас услугу:", reply_markup=keyboard
    )
    await state.set_state(BookingState.choosing_service)


@dp.callback_query(BookingState.choosing_service, F.data.startswith("service:"))
async def process_service(cb: CallbackQuery, state: FSMContext):
    selected_service = cb.data.split(":")[1]
    await state.update_data(service=selected_service)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Сегодня (25.06)", callback_data="date:25.06")],
            [InlineKeyboardButton(text="Завтра (26.06)", callback_data="date:26.06")],
        ]
    )

    await cb.message.edit_text(
        f"Вы выбрали: {selected_service}\n\nшаг 2/4: Выберите дату записи:",
        reply_markup=keyboard,
    )
    await state.set_state(BookingState.choosing_date)


@dp.callback_query(BookingState.choosing_date, F.data.startswith("date:"))
async def process_date(cb: CallbackQuery, state: FSMContext):
    selected_date = cb.data.split(":")[1]
    await state.update_data(date=selected_date)

    await cb.message.edit_text("Проверяем свободные слоты в расписании...")

    # Fetch booked slots from google sheets
    booked_slots = await get_booked_slots(selected_date)

    # Build time slot keyboard, hiding or disabling already booked slots
    buttons = []
    for slot in TIME_SLOTS:
        if slot in booked_slots:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{slot} (Занято)", callback_data="slot_taken"
                    )
                ]
            )
        else:
            buttons.append(
                [InlineKeyboardButton(text=f"{slot}", callback_data=f"time:{slot}")]
            )

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    data = await state.get_data()
    await cb.message.edit_text(
        f"Услуга: {data['service']}\n"
        f"Дата: {selected_date}\n\n"
        f"шаг 3/4: Выберите свободное время:",
        reply_markup=keyboard,
    )
    await state.set_state(BookingState.choosing_time)


@dp.callback_query(F.data == "slot_taken")
async def process_slot_taken(callback: CallbackQuery):
    await callback.answer(
        "Это время уже забронировано кем-то другим. Выберите свободный слот!",
        show_alert=True,
    )


@dp.callback_query(BookingState.choosing_time, F.data.startswith("time:"))
async def process_time(callback: CallbackQuery, state: FSMContext):
    selected_time = ":".join(callback.data.split(":")[1:])
    await state.update_data(time=selected_time)

    await callback.message.edit_text(
        "шаг 4/4: Пожалуйста, введите ваш номер телефона в чат:\n"
    )
    await state.set_state(BookingState.entering_phone)


@dp.message(BookingState.entering_phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()

    if not re.match(r"^\+?[78]\d{10}$", re.sub(r"\D", "", phone)):
        await message.answer(
            "Неверный формат номера. Пожалуйста, введите корректный номер телефона"
        )
        return

    data = await state.get_data()

    # preventing race condition
    booked_slots = await get_booked_slots(data["date"])
    if data["time"] in booked_slots:
        await message.answer(
            "К сожалению, пока вы заполняли форму, это время уже успели занять. Давайте выберем другое время заново с помощью команды /start"
        )
        await state.clear()
        return

    await message.answer("Записываем вас в систему расписания, подождите...")

    # Save to Google Sheets
    try:
        await save_booking_to_sheets(
            user_id=message.from_user.id,
            username=message.from_user.username,
            phone=phone,
            service=data["service"],
            date=data["date"],
            time=data["time"],
        )

        await message.answer(
            f"<b>Вы успешно записаны!</b>\n\n"
            f"<b>Ваши детали бронирования:</b>\n"
            f"- Услуга: <code>{data['service']}</code>\n"
            f"- Дата: <code>{data['date']}</code>\n"
            f"- Время: <code>{data['time']}</code>\n"
            f"- Телефон: <code>{phone}</code>\n\n"
            f"Ждем вас в назначенное время!",
            parse_mode="HTML",
        )
    except Exception:
        await message.answer(
            "Произошла ошибка при сохранении записи. Пожалуйста, попробуйте позже."
        )

    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
