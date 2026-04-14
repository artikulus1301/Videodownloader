import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from health_server import start_health_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    # Start health server FIRST before anything else
    logger.info("Starting health server...")
    try:
        health_runner = await start_health_server()
        logger.info("Health server started successfully on port 8000")
    except Exception as e:
        logger.error(f"Failed to start health server: {e}")
        raise
    
    # Now load config (may fail if BOT_TOKEN not set)
    try:
        from config import config
        logger.info("Config loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        await health_runner.cleanup()
        raise
    
    # Initialize bot
    try:
        bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher(storage=MemoryStorage())
        from handlers import router
        dp.include_router(router)
        logger.info("Bot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        await health_runner.cleanup()
        raise

    logger.info("Starting bot polling...")
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
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise
