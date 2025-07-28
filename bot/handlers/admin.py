"""Administrative bot command handlers."""

import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from filters.chat_filters import AdminFilter
from handlers.basic import user_headers
from settings import settings


def _get_headers(uid: int) -> dict | None:
    """Return auth headers for a user or None if not registered."""
    return user_headers.get(uid)


templates_store: dict[int, str] = {}
sessions_store: dict[int, str] = {}

router = Router()
INSIGHTS_URL = f"{settings.bots.app_url}/api/v1/resume"


@router.message(AdminFilter(), Command("admin"))
async def admin_cmd(msg: Message):
    """Show available admin commands."""

    txt = (
        "Доступные команды:\n"
        "/health - Проверить состояние API\n"
        "/create_template - Создать шаблон игры\n"
        "/list_templates - Список шаблонов\n"
        "/start_session - Начать сессию\n"
        "/make_choice - Отправить выбор\n"
        "/history - История сцен\n"
        "/plans - Тарифы\n"
        "/subscribe - Оформить подписку\n"
        "/status - Статус подписки\n"
        "/change_plan_pro - Включить Pro\n"
        "/change_plan_free - Включить Free\n"
        "/upload_presets - Загрузить пресеты из JSON"
    )
    await msg.answer(txt)


@router.message(AdminFilter(), Command(commands=["health"]))
async def health_command(message: Message):
    """Check backend service health and report status."""

    url = f"{settings.bots.app_url}/api/v1/health_check"
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(url)
    status = "✅ API работает" if resp.status_code == 200 else "❌ Нет связи"
    await message.answer(status)


@router.message(AdminFilter(), Command("create_template"))
async def create_template_cmd(message: Message):
    """Create a game template using test data."""

    headers = _get_headers(message.from_user.id)
    if not headers:
        await message.answer("Сначала выполните /start для авторизации")
        return
    url = f"{settings.bots.app_url}/api/v1/templates"
    payload = {
        "setting_desc": "Test world",
        "char_name": "Tester",
        "char_age": "30",
        "char_background": "Background",
        "char_personality": "Personality",
        "genre": "Adventure",
    }
    async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
        resp = await client.post(url, json=payload)
    if resp.status_code == 201:
        templates_store[message.from_user.id] = resp.json()["id"]
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("list_templates"))
async def list_templates_cmd(message: Message):
    """List available templates for the user."""

    headers = _get_headers(message.from_user.id)
    if not headers:
        await message.answer("Сначала выполните /start для авторизации")
        return
    url = f"{settings.bots.app_url}/api/v1/templates"
    async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
        resp = await client.get(url)
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("upload_presets"))
async def upload_presets_cmd(message: Message):
    """Upload a JSON file with preset templates."""

    if not message.document:
        await message.answer("Пришлите JSON файл")
        return
    headers = _get_headers(message.from_user.id)
    if not headers:
        await message.answer("Сначала выполните /start для авторизации")
        return
    file_id = message.document.file_id
    file_info = await message.bot.get_file(file_id)
    file = await message.bot.download_file(file_info.file_path)
    url = f"{settings.bots.app_url}/api/v1/templates/upload"
    async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
        files = {"file": (message.document.file_name, file.read())}
        resp = await client.post(url, files=files)
    await message.answer(str(resp.status_code))


@router.message(AdminFilter(), Command("start_session"))
async def start_session_cmd(message: Message):
    """Start a new game session based on stored template."""

    headers = _get_headers(message.from_user.id)
    if not headers:
        await message.answer("Сначала выполните /start для авторизации")
        return
    template_id = templates_store.get(message.from_user.id)
    url = f"{settings.bots.app_url}/api/v1/sessions"
    async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
        resp = await client.post(url, json={"template_id": template_id})
    if resp.status_code == 201:
        sessions_store[message.from_user.id] = resp.json()["id"]
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("make_choice"))
async def make_choice_cmd(message: Message):
    """Send a test choice to the active session."""

    session_id = sessions_store.get(message.from_user.id)
    if not session_id:
        await message.answer("Нет активной сессии")
        return
    headers = _get_headers(message.from_user.id)
    if not headers:
        await message.answer("Сначала выполните /start для авторизации")
        return
    url = f"{settings.bots.app_url}/api/v1/sessions/{session_id}/choice"
    async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
        resp = await client.post(url, json={"choice_text": "test choice"})
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("history"))
async def history_cmd(message: Message):
    """Show history of scenes for the active session."""

    session_id = sessions_store.get(message.from_user.id)
    if not session_id:
        await message.answer("Нет активной сессии")
        return
    headers = _get_headers(message.from_user.id)
    if not headers:
        await message.answer("Сначала выполните /start для авторизации")
        return
    url = f"{settings.bots.app_url}/api/v1/sessions/{session_id}/history"
    async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
        resp = await client.get(url)
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("plans"))
async def plans_cmd(message: Message):
    """Retrieve available subscription plans."""

    headers = _get_headers(message.from_user.id)
    if not headers:
        await message.answer("Сначала выполните /start для авторизации")
        return
    url = f"{settings.bots.app_url}/api/v1/plans"
    async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
        resp = await client.get(url)
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("subscribe"))
async def subscribe_cmd(message: Message):
    """Subscribe the user to a plan."""

    headers = _get_headers(message.from_user.id)
    if not headers:
        await message.answer("Сначала выполните /start для авторизации")
        return
    url = f"{settings.bots.app_url}/api/v1/subscribe"
    async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
        resp = await client.post(url)
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("status"))
async def status_cmd(message: Message):
    """Get user's subscription status."""

    headers = _get_headers(message.from_user.id)
    if not headers:
        await message.answer("Сначала выполните /start для авторизации")
        return
    url = f"{settings.bots.app_url}/api/v1/subscription/status"
    async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
        resp = await client.get(url)
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command(commands=["change_plan_pro", "change_plan_free"]))
async def change_plan_cmd(message: Message):
    """Change the current user's subscription plan."""

    plan = message.text.split("_")[-1]
    headers = _get_headers(message.from_user.id)
    if not headers:
        await message.answer("Сначала выполните /start для авторизации")
        return
    url = f"{settings.bots.app_url}/api/v1/subscription/change-plan"
    async with httpx.AsyncClient(timeout=5.0, headers=headers) as client:
        resp = await client.post(url, params={"plan": plan})
    await message.answer(str(resp.json()))
