"""Utility for configuring default bot commands."""

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot) -> None:
    """Register default commands for the bot."""

    commands = [
        BotCommand(command="start", description="Регистрация"),
        BotCommand(command="new_game", description="Создать игру"),
        BotCommand(command="my_games", description="Мои игры"),
        BotCommand(command="end_game", description="Завершить игру"),
        BotCommand(command="help", description="Помощь"),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
