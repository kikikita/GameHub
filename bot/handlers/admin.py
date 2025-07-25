from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import httpx

from settings import settings
from filters.chat_filters import AdminFilter

router = Router()
INSIGHTS_URL = f"{settings.bots.app_url}/api/v1/resume"


@router.message(AdminFilter(), Command("admin"))
async def admin_cmd(msg: Message):
    txt = ('Доступные команды:\n' +
           '/health -> Проверить состояние API\n'
           )
    await msg.answer(txt)


@router.message(AdminFilter(), Command(commands=["health"]))
async def health_command(message: Message):
    url = f"{settings.bots.app_url}/api/v1/health_check"
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(url)
    status = "✅ API работает" if resp.status_code == 200 else "❌ Нет связи"
    await message.answer(status)
