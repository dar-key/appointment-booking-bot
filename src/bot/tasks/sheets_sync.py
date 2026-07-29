# src/bot/tasks/sheets_sync.py
import asyncio
import logging
import sqlite3

import aiosqlite
from aiogram import Dispatcher
from gspread.exceptions import GSpreadException

from src.bot import db
from src.bot.repositories.sheets import save_booking_to_sheets

logger = logging.getLogger(__name__)


async def _sync_loop() -> None:
    while True:
        try:
            await asyncio.sleep(300)

            unsynced = await db.get_unsynced_bookings()
            if not unsynced:
                continue

            logger.info("Found %d unsynced booking(s). Retrying sync...", len(unsynced))

            for booking in unsynced:
                try:
                    await save_booking_to_sheets(
                        user_id=booking["user_id"],
                        username=booking["username"],
                        phone=booking["phone"],
                        service=booking["service"],
                        date=booking["date"],
                        time=booking["time"],
                    )
                    await db.mark_booking_synced(booking["id"])
                    logger.info(
                        "Background sync succeeded for booking ID %s", booking["id"]
                    )

                except (
                    GSpreadException,
                    sqlite3.Error,
                    aiosqlite.Error,
                    OSError,
                ) as err:
                    logger.error(
                        "Background sync failed for booking ID %s: %s",
                        booking["id"],
                        err,
                    )

        except asyncio.CancelledError:
            logger.info("Background sheets sync task stopped.")
            break

        except Exception:
            logger.exception("Unexpected error in background sync loop")


def setup_sheets_sync_task(dp: Dispatcher) -> None:
    sync_task: asyncio.Task[None] | None = None

    async def on_startup() -> None:
        nonlocal sync_task
        sync_task = asyncio.create_task(_sync_loop())
        logger.info("Background sheets sync task started.")

    async def on_shutdown() -> None:
        nonlocal sync_task
        if sync_task:
            sync_task.cancel()
            await asyncio.gather(sync_task, return_exceptions=True)
            logger.info("Background sheets sync task shut down.")

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
