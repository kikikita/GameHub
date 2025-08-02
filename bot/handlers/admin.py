"""Administrative bot command handlers."""

import httpx
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from filters.chat_filters import AdminFilter
from settings import settings


stories_store: dict[int, str] = {}
sessions_store: dict[int, str] = {}

router = Router()
INSIGHTS_URL = f"{settings.bots.app_url}/api/v1/resume"

client = httpx.AsyncClient(
    base_url=settings.bots.app_url,
    timeout=httpx.Timeout(60.0),
    headers={"X-Server-Auth": settings.bots.server_auth_token.get_secret_value()},
)


@router.message(AdminFilter(), Command("admin"))
async def admin_cmd(msg: Message):
    """Show available admin commands."""

    txt = (
        "Доступные команды:\n"
        "/health - Проверить состояние API\n"
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
    resp = await client.get(url, headers={"X-User-Id": str(message.from_user.id)})
    status = "✅ API работает" if resp.status_code == 200 else "❌ Нет связи"
    await message.answer(status)


@router.message(AdminFilter(), Command("upload_presets"))
async def upload_presets_cmd(message: Message):
    """Upload a JSON file with preset worlds and stories."""

    if not message.document:
        await message.answer("Пришлите JSON файл")
        return
    file_id = message.document.file_id
    file_info = await message.bot.get_file(file_id)
    file = await message.bot.download_file(file_info.file_path)
    url = f"{settings.bots.app_url}/api/v1/presets/upload/"
    files = {"file": (message.document.file_name, file.read())}
    resp = await client.post(
        url, files=files, headers={"X-User-Id": str(message.from_user.id)}
    )
    await message.answer(str(resp.status_code))


@router.message(AdminFilter(), Command("start_session"))
async def start_session_cmd(message: Message):
    """Start a new game session based on stored template."""
    uid = message.from_user.id
    story_id = stories_store.get(uid)
    if not story_id:
        worlds = await client.get(
            f"{settings.bots.app_url}/api/v1/worlds/", headers={"X-User-Id": str(uid)}
        )
        if worlds.status_code != 200:
            await message.answer("Ошибка миров")
            return
        world_id = worlds.json()[0]["id"]
        stories = await client.get(
            f"{settings.bots.app_url}/api/v1/worlds/{world_id}/stories/"
        )
        if stories.status_code != 200 or not stories.json():
            await message.answer("Нет историй")
            return
        story_id = stories.json()[0]["id"]
        stories_store[uid] = story_id
    url = f"{settings.bots.app_url}/api/v1/sessions/"
    resp = await client.post(
        url, json={"story_id": story_id}, headers={"X-User-Id": str(uid)}
    )
    if resp.status_code == 201:
        sessions_store[uid] = resp.json()["id"]
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("make_choice"))
async def make_choice_cmd(message: Message):
    """Send a test choice to the active session."""

    session_id = sessions_store.get(message.from_user.id)
    if not session_id:
        await message.answer("Нет активной сессии")
        return
    url = f"{settings.bots.app_url}/api/v1/sessions/{session_id}/choice/"
    resp = await client.post(url, json={"choice_text": "test choice"}, headers={"X-User-Id": str(message.from_user.id)})
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("history"))
async def history_cmd(message: Message):
    """Show history of scenes for the active session."""

    session_id = sessions_store.get(message.from_user.id)
    if not session_id:
        await message.answer("Нет активной сессии")
        return
    url = f"{settings.bots.app_url}/api/v1/sessions/{session_id}/history/"
    resp = await client.get(url, headers={"X-User-Id": str(message.from_user.id)})
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("plans"))
async def plans_cmd(message: Message):
    """Retrieve available subscription plans."""

    url = f"{settings.bots.app_url}/api/v1/plans/"
    resp = await client.get(url, headers={"X-User-Id": str(message.from_user.id)})
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("subscribe"))
async def subscribe_cmd(message: Message):
    """Subscribe the user to a plan."""

    url = f"{settings.bots.app_url}/api/v1/subscribe/"
    resp = await client.post(url, headers={"X-User-Id": str(message.from_user.id)})
    await message.answer(str(resp.json()))


@router.message(AdminFilter(), Command("status"))
async def status_cmd(message: Message):
    """Get user's subscription status."""

    url = f"{settings.bots.app_url}/api/v1/subscription/status/"
    resp = await client.get(url, headers={"X-User-Id": str(message.from_user.id)})
    await message.answer(str(resp.json()))


@router.message(
    AdminFilter(), Command(commands=["change_plan_pro", "change_plan_free"])
)
async def change_plan_cmd(message: Message):
    """Change the current user's subscription plan."""

    plan = message.text.split("_")[-1]
    url = f"{settings.bots.app_url}/api/v1/subscription/change-plan/"
    resp = await client.post(url, params={"plan": plan}, headers={"X-User-Id": str(message.from_user.id)})
    await message.answer(str(resp.json()))
