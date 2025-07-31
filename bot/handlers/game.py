"""Game interaction handlers."""

from __future__ import annotations

import httpx
import base64
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from settings import settings
from .basic import user_headers
from keyboards.inline import (
    setup_keyboard,
    cancel_keyboard,
    games_keyboard,
    language_keyboard,
    stories_keyboard,
    open_app_keyboard,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.states import GameSetup, GamePlay

http_client = httpx.AsyncClient(
    base_url=settings.bots.app_url,
    timeout=httpx.Timeout(60.0),
)


router = Router()

# In-memory store for active sessions
active_sessions: dict[int, list[dict]] = {}

# Default game template values
DEFAULT_TEMPLATE = {
    "story_desc": (
        "A post-apocalyptic wasteland where survivors struggle to rebuild "
        "civilization among the ruins of the old world"
    ),
    "char_name": "Marcus Steelborn",
    "char_age": "32",
    "char_background": (
        "A former soldier turned cybernetic engineer in a dystopian future, "
        "seeking to expose corporate corruption"
    ),
    "char_personality": (
        "Brave, tech-savvy, has trust issues but deeply loyal to those who "
        "earn his respect"
    ),
    "genre": "Adventure",
}


def _build_setup_text(data: dict) -> str:
    """Build setup message with current template data."""
    return (
        f"Setting Description: {data.get('story_desc') or '-'}\n"
        f"Character Name: {data.get('char_name') or '-'}\n"
        f"Character Age: {data.get('char_age') or '-'}\n"
        f"Character Background: {data.get('char_background') or '-'}\n"
        f"Character Personality: {data.get('char_personality') or '-'}\n"
        f"Genre: {data.get('genre') or '-'}"
    )


async def _send_scene(
    chat_id: int,
    bot,
    scene: dict,
    session_id: str,
    state: FSMContext,
):
    """Send scene description and handle next choice state."""
    text = scene.get("description") or ""
    choices = []
    if scene.get("choices_json"):
        choices = scene["choices_json"].get("choices", [])

    reply_kb = None
    choice_map = {}
    if choices:
        kb = InlineKeyboardBuilder()
        for idx, choice in enumerate(choices):
            kb.button(text=choice["text"], callback_data=f"choice:{idx}")
            choice_map[str(idx)] = choice["text"]
        kb.adjust(1)
        reply_kb = kb.as_markup()

    is_photo = False
    if scene.get("image_data"):
        # Convert base64 PNG data returned by backend into aiogram-readable file
        image_bytes = base64.b64decode(scene["image_data"])
        photo = BufferedInputFile(image_bytes, filename="scene.png")
        msg = await bot.send_photo(
            chat_id,
            photo,
            caption=text,
            reply_markup=reply_kb,
        )
        is_photo = True
    else:
        msg = await bot.send_message(chat_id, text, reply_markup=reply_kb)

    if choices:
        await state.set_state(GamePlay.waiting_choice)
        await state.update_data(
            session_id=session_id,
            last_scene_id=msg.message_id,
            last_scene_text=text,
            last_scene_photo=is_photo,
            choices_map=choice_map,
        )
    else:
        await state.clear()
        for g in active_sessions.get(chat_id, []):
            if g["id"] == session_id:
                active_sessions[chat_id].remove(g)
                break


def _get_headers(uid: int) -> dict | None:
    """Return auth headers for a user or ``None`` if missing."""

    return user_headers.get(uid)


async def _has_pro(uid: int) -> bool:
    headers = _get_headers(uid)
    if not headers:
        return False
    resp = await http_client.get("/api/v1/subscription/status", headers=headers)
    if resp.status_code != 200:
        return False
    data = resp.json()
    return data.get("status") == "active" and data.get("plan") == "pro"




@router.message(Command(commands=["my_game"]))
async def play_cmd(message: Message, state: FSMContext):
    """Begin game setup by sending initial template."""

    if not await _has_pro(message.from_user.id):
        await message.answer(
            "Создай собственную историю в веб-приложении",
            reply_markup=open_app_keyboard(settings.bots.web_url),
        )
        return

    data = DEFAULT_TEMPLATE.copy()
    txt = _build_setup_text(data)
    kb = setup_keyboard()
    msg = await message.answer(txt, reply_markup=kb)
    await state.clear()
    await state.update_data(base_id=msg.message_id, template=data)


@router.callback_query(F.data.startswith("edit:"))
async def edit_field(call: CallbackQuery, state: FSMContext):
    """Prompt the user to edit a template field."""

    field = call.data.split(":", 1)[1]
    prompts = {
        "story_desc": "Введите описание сеттинга",
        "char_name": "Введите имя персонажа",
        "char_age": "Введите возраст персонажа",
        "char_background": "Введите предысторию персонажа",
        "char_personality": "Введите характер персонажа",
        "genre": "Введите жанр",
    }
    msg = await call.message.answer(
        prompts[field],
        reply_markup=cancel_keyboard(),
    )
    await state.update_data(edit_field=field, prompt_id=msg.message_id)
    await state.set_state(GameSetup.waiting_input)
    await call.answer()


@router.callback_query(GameSetup.waiting_input, F.data == "cancel")
async def cancel_input(call: CallbackQuery, state: FSMContext):
    """Cancel input and reset state."""

    await call.message.delete()
    await state.set_state(None)
    await call.answer()


@router.message(GameSetup.waiting_input)
async def receive_input(message: Message, state: FSMContext):
    """Process user input and update the template."""

    data = await state.get_data()
    field = data.get("edit_field")
    template = data.get("template", {})
    template[field] = message.text
    prompt_id = data.get("prompt_id")
    base_id = data.get("base_id")
    await state.update_data(template=template)
    await message.delete()
    if prompt_id:
        try:
            await message.bot.delete_message(message.chat.id, prompt_id)
        except Exception:
            pass
    txt = _build_setup_text(template)
    kb = setup_keyboard()
    await message.bot.edit_message_text(
        text=txt,
        chat_id=message.chat.id,
        message_id=base_id,
        reply_markup=kb,
    )
    await state.set_state(None)


@router.callback_query(F.data == "start_game")
async def start_game(call: CallbackQuery, state: FSMContext):
    """Create template and start a new game session."""

    data = await state.get_data()
    template = data.get("template") or DEFAULT_TEMPLATE.copy()

    headers = _get_headers(call.from_user.id)
    if not headers:
        await call.answer("Сначала выполните /start", show_alert=True)
        return

    resp = await http_client.post(
        "/api/v1/stories",
        json={
            "title": template.get("genre"),
            "story_desc": template.get("story_desc"),
            "genre": template.get("genre"),
            "character": {
                "char_name": template.get("char_name"),
                "char_age": template.get("char_age"),
                "char_background": template.get("char_background"),
                "char_personality": template.get("char_personality"),
            },
            "is_free": False,
        },
        headers=headers,
    )
    if resp.status_code != 201:
        if resp.status_code == 403:
            await call.message.answer(
                "Создай собственную историю в веб-приложении",
                reply_markup=open_app_keyboard(settings.bots.web_url),
            )
            await state.clear()
        else:
            await call.answer("Ошибка истории", show_alert=True)
        return
    story_id = resp.json()["id"]
    resp = await http_client.post(
        "/api/v1/sessions",
        json={"story_id": story_id},
        headers=headers,
    )
    if resp.status_code != 201:
        await call.answer("Ошибка сессии", show_alert=True)
        return
    session_id = resp.json()["id"]
    resp = await http_client.get(
        f"/api/v1/sessions/{session_id}",
        headers=headers,
    )
    if resp.status_code != 200:
        await call.answer("Ошибка сцены", show_alert=True)
        return
    scene = resp.json()

    active_sessions.setdefault(call.from_user.id, []).append(
        {"id": session_id, "title": template.get("genre")}
    )

    await call.message.delete()
    await _send_scene(
        call.message.chat.id, call.bot, scene, session_id, state
    )
    await call.answer()


@router.callback_query(F.data.startswith("preset:"))
async def select_preset(call: CallbackQuery, state: FSMContext):
    story_id = call.data.split(":", 1)[1]
    headers = _get_headers(call.from_user.id)
    if not headers:
        await call.answer("Сначала выполните /start", show_alert=True)
        return
    try:
        await call.message.delete()
    except Exception:
        pass
    resp = await http_client.get(f"/api/v1/stories/{story_id}", headers=headers)
    if resp.status_code != 200:
        await call.answer("Ошибка", show_alert=True)
        return
    story = resp.json()
    world_resp = await http_client.get(
        f"/api/v1/worlds/{story['world_id']}", headers=headers
    )
    image_url = None
    if world_resp.status_code == 200:
        image_url = world_resp.json().get("image_url")
    if image_url:
        try:
            await call.message.answer_photo(image_url, caption=story.get("story_desc", ""))
        except Exception:
            await call.message.answer(text=story.get("story_desc", ""))
    else:
        await call.message.answer(story.get("story_desc", ""))
    resp = await http_client.post(
        "/api/v1/sessions",
        json={"story_id": story_id},
        headers=headers,
    )
    if resp.status_code != 201:
        await call.answer("Ошибка", show_alert=True)
        return
    session_id = resp.json()["id"]
    resp = await http_client.get(
        f"/api/v1/sessions/{session_id}",
        headers=headers,
    )
    if resp.status_code != 200:
        await call.answer("Ошибка", show_alert=True)
        return
    scene = resp.json()
    active_sessions.setdefault(call.from_user.id, []).append(
        {"id": session_id, "title": story.get("title")}
    )
    await _send_scene(call.message.chat.id, call.bot, scene, session_id, state)
    await call.answer()


@router.callback_query(F.data.startswith("choice:"))
async def make_choice(call: CallbackQuery, state: FSMContext):
    """Handle choice selection via inline button."""

    choice_idx = call.data.split(":", 1)[1]
    data = await state.get_data()
    session_id = data.get("session_id")
    last_scene_id = data.get("last_scene_id")
    last_text = data.get("last_scene_text", "")
    last_photo = data.get("last_scene_photo", False)
    choices_map = data.get("choices_map", {})
    choice = choices_map.get(choice_idx)
    headers = _get_headers(call.from_user.id)
    if not session_id or not headers or not choice:
        await call.answer()
        return

    resp = await http_client.post(
        f"/api/v1/sessions/{session_id}/choice",
        json={"choice_text": choice},
        headers=headers,
    )
    if resp.status_code != 201:
        await call.answer("Ошибка", show_alert=True)
        return
    scene = resp.json()

    await call.bot.edit_message_reply_markup(
        chat_id=call.message.chat.id,
        message_id=last_scene_id,
        reply_markup=None,
    )
    try:
        if last_photo:
            await call.bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=last_scene_id,
                caption=f"{last_text}\n\nВы выбрали: {choice}",
            )
        else:
            await call.bot.edit_message_text(
                text=f"{last_text}\n\nВы выбрали: {choice}",
                chat_id=call.message.chat.id,
                message_id=last_scene_id,
            )
    except Exception:
        pass

    await _send_scene(
        call.message.chat.id, call.bot, scene, session_id, state
    )
    await call.answer()


@router.message(GamePlay.waiting_choice)
async def choice_text(message: Message, state: FSMContext):
    """Handle text choice input during gameplay."""

    choice = message.text
    data = await state.get_data()
    session_id = data.get("session_id")
    last_scene_id = data.get("last_scene_id")
    last_text = data.get("last_scene_text", "")
    last_photo = data.get("last_scene_photo", False)
    headers = _get_headers(message.from_user.id)
    await message.delete()
    if not session_id or not headers:
        return
    resp = await http_client.post(
        f"/api/v1/sessions/{session_id}/choice",
        json={"choice_text": choice},
        headers=headers,
    )
    if resp.status_code != 201:
        return
    scene = resp.json()

    await message.bot.edit_message_reply_markup(
        chat_id=message.chat.id,
        message_id=last_scene_id,
        reply_markup=None,
    )
    try:
        if last_photo:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_scene_id,
                caption=f"{last_text}\n\nВы выбрали: {choice}",
            )
        else:
            await message.bot.edit_message_text(
                text=f"{last_text}\n\nВы выбрали: {choice}",
                chat_id=message.chat.id,
                message_id=last_scene_id,
            )
    except Exception:
        pass

    await _send_scene(
        message.chat.id, message.bot, scene, session_id, state
    )


@router.message(Command("my_games"))
async def my_games_cmd(message: Message):
    """Show list of active games."""

    games = active_sessions.get(message.from_user.id)
    if not games:
        await message.answer(
            "У вас пока нет активных игр. Используйте /new_game, чтобы начать."
        )
        return
    kb = games_keyboard(games)
    await message.answer(
        "Вы можете продолжить одну из текущих игр:", reply_markup=kb
    )


@router.callback_query(F.data.startswith("resume:"))
async def resume_game(call: CallbackQuery, state: FSMContext):
    """Resume a selected game session."""

    session_id = call.data.split(":", 1)[1]
    headers = _get_headers(call.from_user.id)
    if not headers:
        await call.answer("Сначала выполните /start", show_alert=True)
        return
    resp = await http_client.get(
        f"/api/v1/sessions/{session_id}",
        headers=headers,
    )
    if resp.status_code != 200:
        await call.answer("Ошибка", show_alert=True)
        return
    scene = resp.json()

    await call.message.delete()
    await _send_scene(call.message.chat.id, call.bot, scene, session_id, state)
    await call.answer()


@router.message(Command("end_game"))
async def end_game_cmd(message: Message, state: FSMContext):
    """Finish current game session and clean up state."""

    data = await state.get_data()
    session_id = data.get("session_id")
    if not session_id:
        await message.answer("Нет активной игры")
        return
    headers = _get_headers(message.from_user.id)
    if headers:
        await http_client.delete(
            f"/api/v1/sessions/{session_id}",
            headers=headers,
            timeout=5.0,
        )
    for g in active_sessions.get(message.from_user.id, []):
        if g["id"] == session_id:
            active_sessions[message.from_user.id].remove(g)
            break
    last_scene_id = data.get("last_scene_id")
    if last_scene_id:
        try:
            await message.bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=last_scene_id,
                reply_markup=None,
            )
        except Exception:
            pass
    await state.clear()
    await message.answer("Сессия завершена")
