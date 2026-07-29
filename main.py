import asyncio

from aiogram import Bot, Dispatcher

from src.bot.config import BOT_TOKEN, logger
from src.bot.db import init_db, init_redis
from src.bot.handlers import booking
from src.bot.middlewares.throttling import ThrottlingMiddleware


async def main():
    await init_db()
    storage = await init_redis()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    dp.message.outer_middleware(ThrottlingMiddleware())
    dp.callback_query.outer_middleware(ThrottlingMiddleware())

    # Register routers
    dp.include_router(booking.router)

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
