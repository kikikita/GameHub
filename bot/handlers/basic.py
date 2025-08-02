"""Basic user commands handlers."""

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
import logging

logger = logging.getLogger(__name__)

router = Router()

client = httpx.AsyncClient(timeout=60.0, headers={
    "X-Server-Auth": settings.bots.server_auth_token.get_secret_value()
})


@router.message(Command("start"))
async def start_command(message: Message):
    """Register and authenticate the user on the backend."""
    url = f"{settings.bots.app_url}/api/v1/auth/register/"
    uid = message.from_user.id
    payload = {
        "tg_id": uid,
        "username": message.from_user.username,
    }

    resp = await client.post(url, json=payload, headers={"X-User-Id": str(uid)})
    if resp.status_code == 409:
        await show_presets(message.chat.id, message.bot)
        return
    if resp.status_code != 201:
        await message.answer("Не удалось зарегистрироваться")
        logger.error(f"Failed to register user {uid}: {resp}")
        return

    resp = await client.get(f"{settings.bots.app_url}/api/v1/users/me/", headers={"X-User-Id": str(uid)})
        
    language = None
    if resp.status_code == 200:
        language = resp.json().get("language")
    if not language:
        # If the user's first name contains Cyrillic, set the language to Russian automatically
        if any("\u0400" <= c <= "\u04FF" for c in message.from_user.first_name):
            language = "ru"
            await client.patch(
                f"{settings.bots.app_url}/api/v1/users/me/",
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
    await show_presets(message.chat.id, message.bot)


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
    await client.patch(
            f"{settings.bots.app_url}/api/v1/users/me/",
            headers={"X-User-Id": str(call.from_user.id)},
            json={"language": lang},
        )
    await call.message.delete()
    await show_presets(call.message.chat.id, call.message.bot)
    await call.answer()
