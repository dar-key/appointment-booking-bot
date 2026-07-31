import asyncio

from aiogram import Bot, Dispatcher

from src.bot.config import BOT_TOKEN, logger
from src.bot.db import init_db, init_redis
from src.bot.handlers import booking
from src.bot.middlewares.throttling import ThrottlingMiddleware
from src.bot.tasks.sheets_sync import setup_sheets_sync_task


async def main():
    await init_db()
    storage = await init_redis()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    # Register middlewares
    dp.message.outer_middleware(ThrottlingMiddleware())

    # Register routers
    dp.include_router(booking.router)

    # Register background tasks
    setup_sheets_sync_task(dp, bot)

    try:
        await dp.start_polling(bot)
    finally:
        logger.info("CLOSING BOT SESSION...")
        await bot.session.close()
        await storage.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
