# src/bot/tasks/sheets_sync.py
import asyncio
import logging
import sqlite3

import aiosqlite
from aiogram import Bot, Dispatcher
from gspread.exceptions import GSpreadException

from src.bot import db
from src.bot.repositories.sheets import save_booking_to_sheets
from src.bot.utils.telegram import notify_admin

logger = logging.getLogger(__name__)


_FAILURE_ALERT_THRESHOLD = 3
_consecutive_failures: dict[int, int] = {}


async def _sync_loop(bot: Bot) -> None:
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
                    # clear failure count once it recovers
                    _consecutive_failures.pop(booking["id"], None)

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
                    count = _consecutive_failures.get(booking["id"], 0) + 1
                    _consecutive_failures[booking["id"]] = count
                    if count == _FAILURE_ALERT_THRESHOLD:
                        await notify_admin(
                            bot,
                            f"Booking #{booking['id']} has failed to sync "
                            f"to Google Sheets {count} times in a row. It's "
                            f"saved locally but may need manual attention.",
                        )

        except asyncio.CancelledError:
            logger.info("Background sheets sync task stopped.")
            break

        except Exception:
            logger.exception("Unexpected error in background sync loop")


def setup_sheets_sync_task(dp: Dispatcher, bot: Bot) -> None:
    sync_task: asyncio.Task[None] | None = None

    async def on_startup() -> None:
        nonlocal sync_task
        sync_task = asyncio.create_task(_sync_loop(bot))
        logger.info("Background sheets sync task started.")

    async def on_shutdown() -> None:
        nonlocal sync_task
        if sync_task:
            sync_task.cancel()
            await asyncio.gather(sync_task, return_exceptions=True)
            logger.info("Background sheets sync task shut down.")

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
