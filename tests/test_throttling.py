from types import SimpleNamespace

import pytest
from aiogram.types import Update

from src.bot.middlewares.throttling import ThrottlingMiddleware


def make_user(user_id: int):
    return SimpleNamespace(id=user_id)


@pytest.mark.asyncio
async def test_second_rapid_call_from_same_user_is_throttled():
    middleware = ThrottlingMiddleware(rate=100)  # never expires in a test
    calls = []

    async def handler(event, data):
        calls.append(event)
        return "ok"

    user = make_user(1)
    event = Update(update_id=1)
    data = {"event_from_user": user}

    first_result = await middleware(handler, event, data)
    second_result = await middleware(handler, event, data)

    assert first_result == "ok"
    assert second_result is None
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_different_users_are_not_throttled_by_each_other():
    middleware = ThrottlingMiddleware(rate=100)
    calls = []

    async def handler(event, data):
        calls.append(event)
        return "ok"

    event = Update(update_id=1)

    result_a = await middleware(handler, event, {"event_from_user": make_user(1)})
    result_b = await middleware(handler, event, {"event_from_user": make_user(2)})

    assert result_a == "ok"
    assert result_b == "ok"
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_call_after_rate_window_passes_through():
    middleware = ThrottlingMiddleware(rate=0)  # window elapses immediately
    calls = []

    async def handler(event, data):
        calls.append(event)
        return "ok"

    user = make_user(1)
    event = Update(update_id=1)
    data = {"event_from_user": user}

    first_result = await middleware(handler, event, data)
    second_result = await middleware(handler, event, data)

    assert first_result == "ok"
    assert second_result == "ok"
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_missing_user_skips_throttling_and_calls_handler():
    middleware = ThrottlingMiddleware(rate=100)
    calls = []

    async def handler(event, data):
        calls.append(event)
        return "ok"

    event = Update(update_id=1)

    result = await middleware(handler, event, {"event_from_user": None})

    assert result == "ok"
    assert len(calls) == 1
