import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from handlers import router
from health_server import start_health_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    # Start health server
    health_runner = await start_health_server()
    
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    logger.info("Bot started!")
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Run bot polling without blocking health server
    polling_task = asyncio.create_task(dp.start_polling(bot))
    
    try:
        await polling_task
    except asyncio.CancelledError:
        logger.info("Bot polling cancelled")
    finally:
        await health_runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
