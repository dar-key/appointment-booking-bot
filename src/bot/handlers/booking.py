from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from gspread.exceptions import GSpreadException

from src.bot.callback_data.booking import (
    DateCb,
    ServiceCb,
    TimeCb,
)
from src.bot.config import logger
from src.bot.keyboards.booking import (
    get_dates_keyboard,
    get_services_keyboard,
    get_start_keyboard,
    get_time_slots_keyboard,
)
from src.bot.repositories.sheets import get_booked_slots, save_booking_to_sheets
from src.bot.services.messages import booking_confirmation
from src.bot.states import BookingState
from src.bot.utils.telegram import require_message
from src.bot.validators.phone import is_valid_phone

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Welcome to our salon!\n\nClick the button below to book an appointment:",
        reply_markup=get_start_keyboard(),
    )


@router.callback_query(
    F.data == "start_booking",
)
async def process_start_booking(cb: CallbackQuery, state: FSMContext):
    msg = require_message(cb)
    await msg.edit_text(
        "Step 1/4: Select a service:", reply_markup=get_services_keyboard()
    )
    await state.set_state(BookingState.choosing_service)


@router.callback_query(
    BookingState.choosing_service,
    ServiceCb.filter(),
)
async def process_service(
    cb: CallbackQuery, callback_data: ServiceCb, state: FSMContext
):
    selected_service = callback_data.name
    await state.update_data(service=selected_service)

    msg = require_message(cb)
    await msg.edit_text(
        f"Selected service: {selected_service}\n\nStep 2/4: Select a date:",
        reply_markup=get_dates_keyboard(),
    )
    await state.set_state(BookingState.choosing_date)


@router.callback_query(
    BookingState.choosing_date,
    DateCb.filter(),
)
async def process_date(cb: CallbackQuery, callback_data: DateCb, state: FSMContext):
    selected_date = callback_data.date
    await state.update_data(date=selected_date)

    msg = require_message(cb)
    await msg.edit_text("Checking available slots...")

    booked_slots = await get_booked_slots(selected_date)
    keyboard = get_time_slots_keyboard(booked_slots)

    data = await state.get_data()
    await msg.edit_text(
        f"Service: {data['service']}\n"
        f"Date: {selected_date}\n\n"
        f"Step 3/4: Select an available time slot:",
        reply_markup=keyboard,
    )
    await state.set_state(BookingState.choosing_time)


@router.callback_query(F.data == "slot_taken")
async def process_slot_taken(callback: CallbackQuery):
    await callback.answer(
        "This slot is already booked. Please select an available slot!",
        show_alert=True,
    )


@router.callback_query(BookingState.choosing_time, TimeCb.filter())
async def process_time(cb: CallbackQuery, callback_data: TimeCb, state: FSMContext):
    selected_time = callback_data.time.replace("-", ":")
    await state.update_data(time=selected_time)

    msg = require_message(cb)
    await msg.edit_text("Step 4/4: Please enter your phone number in the chat:\n")
    await state.set_state(BookingState.entering_phone)


@router.message(BookingState.entering_phone)
async def process_phone(message: Message, state: FSMContext):
    if message.text is None:
        await message.answer("Please send a text message.")
        return

    phone = message.text.strip()

    if not is_valid_phone:
        await message.answer(
            "Invalid phone number format. Please enter a valid phone number."
        )
        return

    data = await state.get_data()

    # Race condition check
    booked_slots = await get_booked_slots(data["date"])
    if data["time"] in booked_slots:
        await message.answer(
            "Sorry, this slot was just taken by someone else. Please restart with /start to pick another time."
        )
        await state.clear()
        return

    await message.answer("Saving your booking, please wait...")

    try:
        user = message.from_user
        if user is None:
            return

        await save_booking_to_sheets(
            user_id=user.id,
            username=user.username,
            phone=phone,
            service=data["service"],
            date=data["date"],
            time=data["time"],
        )

        await message.answer(
            booking_confirmation(
                data["service"], data["date"], data["time"], str(phone)
            ),
            parse_mode="HTML",
        )
    except (GSpreadException, TelegramAPIError, KeyError) as e:
        logger.exception("Failed to process booking: %s", e)
        await message.answer(
            "An error occurred while saving your booking. Please try again later."
        )

    await state.clear()
