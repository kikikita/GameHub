from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Register user"),
        BotCommand(command="play", description="Create and play game"),
        BotCommand(command="my_games", description="List my games"),
        BotCommand(command="end_game", description="Finish current game"),
        BotCommand(command="help", description="Show help"),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
