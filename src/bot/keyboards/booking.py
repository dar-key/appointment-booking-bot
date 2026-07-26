from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from src.bot.config import SERVICES, TIME_SLOTS


def get_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Book an Appointment", callback_data="start_booking"
                )
            ]
        ]
    )


def get_services_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=service, callback_data=f"service:{service}")]
        for service in SERVICES
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_dates_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Today (25.06)", callback_data="date:25.06")],
            [InlineKeyboardButton(text="Tomorrow (26.06)", callback_data="date:26.06")],
        ]
    )


def get_time_slots_keyboard(booked_slots: list[str]) -> InlineKeyboardMarkup:
    buttons = []
    for slot in TIME_SLOTS:
        if slot in booked_slots:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{slot} (Booked)", callback_data="slot_taken"
                    )
                ]
            )
        else:
            buttons.append(
                [InlineKeyboardButton(text=slot, callback_data=f"time:{slot}")]
            )
    return InlineKeyboardMarkup(inline_keyboard=buttons)
