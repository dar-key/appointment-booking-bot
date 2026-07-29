import sqlite3

import aiosqlite

from src.bot.config import DB_PATH, logger


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
                UNIQUE(date, time)
            )
            """
        )
        await db.commit()
    logger.info("Database ready at %s", DB_PATH)


async def get_booked_slots(date: str) -> list[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT time FROM bookings WHERE date = ?", (date,))
        rows = await cursor.fetchall()
    return [row[0] for row in rows]


async def create_booking(
    user_id: int, username: str | None, phone: str, service: str, date: str, time: str
) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                """
                INSERT INTO bookings (user_id, username, phone, service, date, time)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, username, phone, service, date, time),
            )
            await db.commit()
            return True
        except sqlite3.IntegrityError:
            return False
