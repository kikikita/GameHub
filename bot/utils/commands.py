from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='start', description='Register user'),
        BotCommand(command='help', description='Show help'),
        BotCommand(command='create_template', description='Create template'),
        BotCommand(command='list_templates', description='List templates'),
        BotCommand(command='start_session', description='Start game session'),
        BotCommand(command='make_choice', description='Send choice'),
        BotCommand(command='history', description='Session history'),
        BotCommand(command='plans', description='Show plans'),
        BotCommand(command='subscribe', description='Subscribe plan'),
        BotCommand(command='status', description='Subscription status'),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())
