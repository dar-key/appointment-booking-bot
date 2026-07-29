import datetime
from zoneinfo import ZoneInfo

from src.bot.config import TIMEZONE


def now() -> datetime.datetime:
    return datetime.datetime.now(ZoneInfo(TIMEZONE))


def is_slot_in_past(date: str, time: str) -> bool:
    """date: 'YYYY-MM-DD', time: 'HH:MM', both interpreted in TIMEZONE."""
    slot_dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %I:%M %p").replace(
        tzinfo=ZoneInfo(TIMEZONE)
    )
    return slot_dt <= now()


def format_date_for_display(date: str) -> str:
    """'YYYY-MM-DD' -> '29 Jul 2026', for showing to the user."""

    return datetime.date.fromisoformat(date).strftime("%d %b %Y")
