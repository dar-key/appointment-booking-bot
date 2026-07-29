import pytest

from src.bot import db


@pytest.fixture
async def temp_db(tmp_path, monkeypatch):
    """Point DB_PATH at a throwaway sqlite file for each test."""
    db_path = tmp_path / "test_bookings.db"
    monkeypatch.setattr(db, "DB_PATH", str(db_path))
    await db.init_db()
    return db_path


@pytest.mark.asyncio
async def test_create_booking_succeeds_for_free_slot(temp_db):
    booking_id = await db.create_booking(
        user_id=1,
        username="alice",
        phone="+12025550123",
        service="Haircut ($20)",
        date="2026-08-01",
        time="10:00",
    )
    assert booking_id is not None


@pytest.mark.asyncio
async def test_double_booking_same_slot_is_rejected(temp_db):
    first = await db.create_booking(
        user_id=1,
        username="alice",
        phone="+12025550123",
        service="Haircut ($20)",
        date="2026-08-01",
        time="10:00",
    )
    second = await db.create_booking(
        user_id=2,
        username="bob",
        phone="+12025550999",
        service="Manicure ($15)",
        date="2026-08-01",
        time="10:00",
    )
    assert first is not None
    assert second is None


@pytest.mark.asyncio
async def test_same_time_different_date_is_allowed(temp_db):
    first = await db.create_booking(
        user_id=1,
        username="bob1",
        phone="+12025555123",
        service="Haircut ($20)",
        date="2026-08-01",
        time="10:00 AM",
    )
    second = await db.create_booking(
        user_id=2,
        username="bob2",
        phone="+12025554999",
        service="Manicure ($15)",
        date="2026-08-02",
        time="10:00 AM",
    )
    assert first is not None
    assert second is not None


@pytest.mark.asyncio
async def test_get_booked_slots_reflects_created_bookings(temp_db):
    await db.create_booking(
        user_id=1,
        username="bob1",
        phone="+12025555123",
        service="Haircut ($20)",
        date="2026-08-01",
        time="10:00 AM",
    )
    await db.create_booking(
        user_id=2,
        username="bob2",
        phone="+12025554999",
        service="Manicure ($15)",
        date="2026-08-01",
        time="12:00 PM",
    )

    slots = await db.get_booked_slots("2026-08-01")

    assert sorted(slots) == ["10:00 AM", "12:00 PM"]
    assert await db.get_booked_slots("2026-08-02") == []
