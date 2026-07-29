import sqlite3
from datetime import timedelta

import aiosqlite
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from src.bot.config import DB_PATH, REDIS_DB, REDIS_HOST, REDIS_PORT, logger


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                phone TEXT NOT NULL,
                service TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                synced_to_sheets BOOLEAN DEFAULT FALSE,
                UNIQUE(date, time)
            )
            """
        )
        await db.commit()
    logger.info("Database ready at %s", DB_PATH)


async def init_redis() -> RedisStorage:

    redis_client = Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
    )

    # Set states to automatically expire if abandoned after 24 hours
    storage = RedisStorage(
        redis=redis_client,
        state_ttl=timedelta(hours=24),
        data_ttl=timedelta(hours=24),
    )

    logger.info("RedisStorage has been loaded")

    return storage


async def get_booked_slots(date: str) -> list[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT time FROM bookings WHERE date = ?", (date,))
        rows = await cursor.fetchall()
    return [row[0] for row in rows]


async def create_booking(
    user_id: int, username: str | None, phone: str, service: str, date: str, time: str
) -> int | None:
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            cursor = await db.execute(
                """
                INSERT INTO bookings (user_id, username, phone, service, date, time)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, username, phone, service, date, time),
            )
            await db.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None


async def mark_booking_synced(booking_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE bookings SET synced_to_sheets = TRUE WHERE id = ?",
            (booking_id,),
        )
        await db.commit()


async def get_unsynced_bookings() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row  # Access columns by name
        cursor = await db.execute(
            "SELECT * FROM bookings WHERE synced_to_sheets = FALSE"
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
