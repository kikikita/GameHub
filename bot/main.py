"""Telegram bot entry point."""

import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from bot.bot import bot_instance, dp_instance
from aiogram import Bot

from handlers import admin, basic, echo, game, payments
from api.stories.router import router as stories_router
from api.cache.routes import router as cache_router
from middlewares.typing import TypingMiddleware
from settings import settings
from utils.commands import set_commands

logger = logging.getLogger(__name__)


async def start_bot(bot: Bot):
    """Notify admin that the bot has started."""

    await set_commands(bot)
    for admin_id in settings.bots.admin_id:
        try:
            await bot.send_message(admin_id, text="Bot started!")
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id}: {e}")


async def stop_bot(bot: Bot):
    """Notify admin that the bot has stopped."""
    for admin_id in settings.bots.admin_id:
        try:
            await bot.send_message(admin_id, text="Bot is stopping...")
        except Exception as e:
            logger.error(f"Failed to notify admin {admin_id} about shutdown: {e}")



async def start():
    """Initialize and start polling."""

    dp_instance.startup.register(start_bot)
    dp_instance.shutdown.register(stop_bot)

    dp_instance.message.middleware.register(TypingMiddleware())

    dp_instance.include_routers(
        admin.router,
        basic.router,
        game.router,
        echo.router,
        payments.router,
    )

    try:
        await bot_instance.delete_webhook(drop_pending_updates=True)
        await dp_instance.start_polling(bot_instance)
    finally:
        await bot_instance.session.close()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://app.immersia.fun"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stories_router)
app.include_router(cache_router)

if settings.bots.debug:
    import debugpy
    debugpy.listen(("0.0.0.0", 5678))
    logger.info("Debugger enabled!")

asyncio.create_task(start())