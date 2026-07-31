from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import CallbackQuery, Message

from src.bot.config import ADMIN_ID, logger


def require_message(cb: CallbackQuery) -> Message:
    message = cb.message

    if not isinstance(message, Message):
        raise TypeError("CallbackQuery has no accessible Message")

    return message


async def notify_admin(bot: Bot, text: str) -> None:
    if ADMIN_ID is None:
        return
    try:
        await bot.send_message(ADMIN_ID, text)
    except TelegramAPIError as e:
        logger.error("Failed to send admin alert: %s", e)
