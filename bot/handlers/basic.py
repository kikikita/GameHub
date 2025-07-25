import httpx
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.reply import get_main_kb, remove_kb
from settings import settings

router = Router()


@router.message(Command("start"))
async def start_command(message: Message):
    """Регистрирует пользователя в бэкэнде и приветствует его."""
    url = f"{settings.bots.app_url}/api/v1/auth/tg"
    payload = {"tg_id": message.from_user.id}

    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.post(url, json=payload)

    if resp.status_code != 200:
        await message.answer("⚠️ Сервис временно недоступен.")
        return

    welcome = (
        f"👋 Hi, <b>{message.from_user.first_name}</b>!\n\n"
    )
    await message.answer(welcome, parse_mode=ParseMode.HTML,
                         reply_markup=get_main_kb())


@router.message(Command(commands=["help"]))
async def help_command(message: Message):
    help_message = (
        "ℹ️ <b>INFO</b>"
    )
    await message.answer(
            help_message,
            parse_mode=ParseMode.HTML,
            reply_markup=remove_kb
            )
