from aiogram.types import CallbackQuery, Message


def require_message(cb: CallbackQuery) -> Message:
    message = cb.message

    if not isinstance(message, Message):
        raise TypeError("CallbackQuery has no accessible Message")

    return message
