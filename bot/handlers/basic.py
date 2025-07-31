"""Basic user commands handlers."""

import hmac
import hashlib
import time
from urllib.parse import urlencode

import httpx
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram import F
from aiogram.types import Message, CallbackQuery

from keyboards.reply import remove_kb
from keyboards.inline import language_keyboard
from utils.presets import show_presets
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

    headers = user_headers[message.from_user.id]
    async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
        resp = await client.get(f"{settings.bots.app_url}/api/v1/users/me")
    language = None
    if resp.status_code == 200:
        language = resp.json().get("language")
    if not language:
        if any("\u0400" <= c <= "\u04FF" for c in message.from_user.first_name):
            language = "ru"
            async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
                await client.patch(
                    f"{settings.bots.app_url}/api/v1/users/me",
                    json={"language": language},
                )
        else:
            await message.answer("Choose your language", reply_markup=language_keyboard())
            return

    welcome = (
        f"👋 Привет, <b>{message.from_user.first_name}</b>!\n"
        "Добро пожаловать в <b>Immersia</b>"
    )
    await message.answer(welcome, parse_mode=ParseMode.HTML)
    await show_presets(message.chat.id, message.bot, headers)


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


@router.callback_query(F.data.startswith("lang:"))
async def set_language(call: CallbackQuery):
    lang = call.data.split(":", 1)[1]
    headers = user_headers.get(call.from_user.id)
    if not headers:
        await call.answer()
        return
    async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
        await client.patch(
            f"{settings.bots.app_url}/api/v1/users/me",
            json={"language": lang},
        )
    await call.message.delete()
    await show_presets(call.message.chat.id, call.message.bot, headers)
    await call.answer()
