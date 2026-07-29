import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(
        self,
        rate: float = 0.7,
        maxsize: int = 10_000,
        ttl: float = 60.0,
    ) -> None:
        self.rate = rate
        self._last_seen: TTLCache[int, float] = TTLCache[int, float](
            maxsize=maxsize, ttl=ttl
        )

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        now = time.monotonic()
        last = self._last_seen.get(user.id)
        self._last_seen[user.id] = now

        if last is not None and (now - last) < self.rate:
            if isinstance(event, Update) and event.callback_query:
                await event.callback_query.answer()
            return None

        return await handler(event, data)
