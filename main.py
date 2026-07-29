import asyncio

from aiogram import Bot, Dispatcher
from src.bot.middlewares.throttling import ThrottlingMiddleware

from src.bot.config import BOT_TOKEN, logger
from src.bot.db import init_db
from src.bot.handlers import booking


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.update.outer_middleware(ThrottlingMiddleware())

    # Register routers
    dp.include_router(booking.router)

    logger.info("Bot starting...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
