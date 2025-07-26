from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import httpx

from settings import settings
from filters.chat_filters import AdminFilter
from handlers.basic import user_headers

templates_store = {}
sessions_store = {}

router = Router()
INSIGHTS_URL = f"{settings.bots.app_url}/api/v1/resume"


@router.message(AdminFilter(), Command("admin"))
async def admin_cmd(msg: Message):
    txt = (
        'Доступные команды:\n'
        '/health - Проверить состояние API\n'
        '/create_template - Создать шаблон игры\n'
        '/list_templates - Список шаблонов\n'
        '/start_session - Начать сессию\n'
        '/make_choice - Отправить выбор\n'
        '/history - История сцен\n'
        '/plans - Тарифы\n'
        '/subscribe - Оформить подписку\n'
        '/status - Статус подписки\n'
    )
    await msg.answer(txt)


@router.message(AdminFilter(), Command(commands=["health"]))
async def health_command(message: Message):
    url = f"{settings.bots.app_url}/api/v1/health_check"
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(url)
    status = "✅ API работает" if resp.status_code == 200 else "❌ Нет связи"
    await message.answer(status)


@router.message(AdminFilter(), Command("create_template"))
async def create_template_cmd(message: Message):
    url = f"{settings.bots.app_url}/api/v1/templates"
    payload = {
        "setting_desc": "Test world",
        "char_name": "Tester",
        "char_age": "30",
        "char_background": "Background",
        "char_personality": "Personality",
        "genre": "Adventure",
    }
    async with httpx.AsyncClient(timeout=5.0, headers=user_headers.get(message.from_user.id)) as client:
        resp = await client.post(url, json=payload)
    if resp.status_code == 201:
        templates_store[message.from_user.id] = resp.json()["id"]
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("list_templates"))
async def list_templates_cmd(message: Message):
    url = f"{settings.bots.app_url}/api/v1/templates"
    async with httpx.AsyncClient(timeout=5.0, headers=user_headers.get(message.from_user.id)) as client:
        resp = await client.get(url)
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("start_session"))
async def start_session_cmd(message: Message):
    template_id = templates_store.get(message.from_user.id)
    url = f"{settings.bots.app_url}/api/v1/sessions"
    async with httpx.AsyncClient(timeout=5.0, headers=user_headers.get(message.from_user.id)) as client:
        resp = await client.post(url, json={"template_id": template_id})
    if resp.status_code == 201:
        sessions_store[message.from_user.id] = resp.json()["id"]
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("make_choice"))
async def make_choice_cmd(message: Message):
    session_id = sessions_store.get(message.from_user.id)
    if not session_id:
        await message.answer("Нет активной сессии")
        return
    url = f"{settings.bots.app_url}/api/v1/sessions/{session_id}/choice"
    async with httpx.AsyncClient(timeout=5.0, headers=user_headers.get(message.from_user.id)) as client:
        resp = await client.post(url, json={"choice_text": "test choice"})
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("history"))
async def history_cmd(message: Message):
    session_id = sessions_store.get(message.from_user.id)
    if not session_id:
        await message.answer("Нет активной сессии")
        return
    url = f"{settings.bots.app_url}/api/v1/sessions/{session_id}/history"
    async with httpx.AsyncClient(timeout=5.0, headers=user_headers.get(message.from_user.id)) as client:
        resp = await client.get(url)
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("plans"))
async def plans_cmd(message: Message):
    url = f"{settings.bots.app_url}/api/v1/plans"
    async with httpx.AsyncClient(timeout=5.0, headers=user_headers.get(message.from_user.id)) as client:
        resp = await client.get(url)
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("subscribe"))
async def subscribe_cmd(message: Message):
    url = f"{settings.bots.app_url}/api/v1/subscribe"
    async with httpx.AsyncClient(timeout=5.0, headers=user_headers.get(message.from_user.id)) as client:
        resp = await client.post(url)
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("status"))
async def status_cmd(message: Message):
    url = f"{settings.bots.app_url}/api/v1/subscription/status"
    async with httpx.AsyncClient(timeout=5.0, headers=user_headers.get(message.from_user.id)) as client:
        resp = await client.get(url)
    await message.answer(str(resp.json()))
