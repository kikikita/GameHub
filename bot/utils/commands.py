"""Utility for configuring default bot commands."""

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot) -> None:
    """Register default commands for the bot in all supported languages."""

    commands_en = [
        BotCommand(command="start", description="Start"),
        BotCommand(command="my_game", description="Create game"),
        BotCommand(command="my_games", description="My games"),
        BotCommand(command="end_game", description="End game"),
        BotCommand(command="help", description="Help"),
    ]

    commands_ru = [
        BotCommand(command="start", description="Регистрация"),
        BotCommand(command="my_game", description="Создать игру"),
        BotCommand(command="my_games", description="Мои игры"),
        BotCommand(command="end_game", description="Завершить игру"),
        BotCommand(command="help", description="Помощь"),
    ]

    await bot.set_my_commands(commands_en, BotCommandScopeDefault(), language_code="en")
    await bot.set_my_commands(commands_ru, BotCommandScopeDefault(), language_code="ru")
