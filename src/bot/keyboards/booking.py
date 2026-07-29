from datetime import timedelta

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.callback_data.booking import (
    DateCb,
    ServiceCb,
    TimeCb,
)
from src.bot.constants import BOOKING_DAYS_AHEAD, SERVICES, TIME_SLOTS
from src.bot.utils.time import is_slot_in_past, now

_RELATIVE_LABELS = ["Today", "Tomorrow"]


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
    today = now()
    buttons = []
    for i in range(BOOKING_DAYS_AHEAD):
        day = today + timedelta(days=i)
        label = _RELATIVE_LABELS[i] if i < len(_RELATIVE_LABELS) else day.strftime("%A")
        display = day.strftime("%d.%m")
        iso_date = day.strftime("%Y-%m-%d")
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{label} ({display})",
                    callback_data=DateCb(date=iso_date).pack(),
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_time_slots_keyboard(booked_slots: list[str], date: str) -> InlineKeyboardMarkup:
    buttons = []
    for slot in TIME_SLOTS:
        if slot in booked_slots:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{slot} (Booked)", callback_data="slot_unavailable"
                    )
                ]
            )
        elif is_slot_in_past(date, slot):
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{slot} (Past)", callback_data="slot_unavailable"
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
