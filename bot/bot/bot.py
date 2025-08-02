from aiogram import Bot, Dispatcher
from settings import settings

bot_instance = Bot(token=settings.bots.bot_token.get_secret_value())
dp_instance = Dispatcher()