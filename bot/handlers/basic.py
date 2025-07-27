"""Basic user commands handlers."""

import hmac
import hashlib
import time
from urllib.parse import urlencode

import httpx
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.reply import remove_kb
from settings import settings

router = Router()

user_headers = {}


@router.message(Command("start"))
async def start_command(message: Message):
    """Register and authenticate the user on the backend."""
    url = f"{settings.bots.app_url}/api/v1/auth/register"
    payload = {
        "tg_id": message.from_user.id,
        "username": message.from_user.username,
    }

    async with httpx.AsyncClient(timeout=5.0) as client:
        await client.post(url, json=payload)

    # Build initData to authenticate further API requests
    data = {
        "user": f"{{\"id\":{message.from_user.id}}}",
        "auth_date": int(time.time()),
    }
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(data.items())
    )
    secret_key = hmac.new(
        b"WebAppData",
        settings.bots.bot_token.encode(),
        hashlib.sha256,
    ).digest()
    data["hash"] = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()
    init_data = urlencode(data)
    user_headers[message.from_user.id] = {
        "Authorization": f"tma {init_data}"
    }

    welcome = (
        f"👋 Привет, <b>{message.from_user.first_name}</b>!\n"
        "Добро пожаловать в <b>Immersia</b> — здесь вы можете "
        "создавать собственные интерактивные истории.\n"
        "Отправьте <b>/new_game</b>, чтобы начать приключение."
    )
    await message.answer(welcome, parse_mode=ParseMode.HTML)


@router.message(Command(commands=["help"]))
async def help_command(message: Message):
    """Show help message to the user."""

    help_message = (
        "ℹ️ <b>Помощь</b>\n\n"
        "<b>/new_game</b> — создать новую игру\n"
        "<b>/my_games</b> — список ваших активных игр\n"
        "<b>/end_game</b> — завершить текущую сессию\n"
        "<b>/help</b> — показать это сообщение"
    )
    await message.answer(
        help_message,
        parse_mode=ParseMode.HTML,
        reply_markup=remove_kb,
    )
