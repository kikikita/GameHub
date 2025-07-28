"""Telegram bot entry point."""

import asyncio
import logging

from aiogram import Bot, Dispatcher

from handlers import admin, basic, echo, game
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

    bot = Bot(token=settings.bots.bot_token)
    dp = Dispatcher()

    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    dp.message.middleware.register(TypingMiddleware())

    dp.include_routers(
        admin.router,
        basic.router,
        game.router,
        echo.router,
    )

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    if settings.bots.debug:
        import debugpy
        debugpy.listen(("0.0.0.0", 5678))
        logger.info("Debugger enabled!")
    asyncio.run(start())
