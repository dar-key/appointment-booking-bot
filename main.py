import asyncio

from aiogram import Bot, Dispatcher

from src.bot.config import BOT_TOKEN, logger
from src.bot.handlers import booking


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Register routers
    dp.include_router(booking.router)

    logger.info("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
