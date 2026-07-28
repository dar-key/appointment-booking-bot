from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.callback_data.booking import (
    DateCb,
    ServiceCb,
    TimeCb,
)
from src.bot.constants import SERVICES, TIME_SLOTS


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
        [
            InlineKeyboardButton(
                text=service, callback_data=ServiceCb(name=service).pack()
            )
        ]
        for service in SERVICES
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_dates_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Today (25.06)", callback_data=DateCb(date="25.06").pack()
                )
            ],
            [
                InlineKeyboardButton(
                    text="Tomorrow (26.06)", callback_data=DateCb(date="26.06").pack()
                )
            ],
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
                [
                    InlineKeyboardButton(
                        text=slot,
                        callback_data=TimeCb(time=slot.replace(":", "-")).pack(),
                    )
                ]
            )
    return InlineKeyboardMarkup(inline_keyboard=buttons)
