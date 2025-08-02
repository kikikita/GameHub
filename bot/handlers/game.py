"""Game interaction handlers."""

from __future__ import annotations

import asyncio
from contextlib import suppress

import base64
import httpx
from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.bot import bot_instance, dp_instance
from keyboards.inline import (
    cancel_keyboard,
    games_keyboard,
    open_app_keyboard,
    setup_keyboard,
)
from settings import settings
from utils.i18n import get_user_language, t
from utils.states import GamePlay, GameSetup

http_client = httpx.AsyncClient(
    base_url=settings.bots.app_url,
    timeout=httpx.Timeout(60.0),
    headers={"X-Server-Auth": settings.bots.server_auth_token.get_secret_value()}
)


router = Router()

# In-memory store for active sessions
active_sessions: dict[int, list[dict]] = {}

# Default game template values per language
DEFAULT_TEMPLATES = {
    "en": {
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
    },
    "ru": {
        "story_desc": (
            "Постапокалиптическая пустошь, где выжившие пытаются восстановить "
            "цивилизацию среди руин старого мира"
        ),
        "char_name": "Маркус Стилборн",
        "char_age": "32",
        "char_background": (
            "Бывший солдат, ставший кибернетическим инженером в антиутопичном "
            "будущем, стремится раскрыть корпоративную коррупцию"
        ),
        "char_personality": (
            "Храбрый, технически подкованный, не доверяет никому, но предан тем, "
            "кто заслуживает его уважения"
        ),
        "genre": "Приключение",
    },
}


def _get_default_template(lang: str) -> dict:
    return DEFAULT_TEMPLATES.get(lang, DEFAULT_TEMPLATES["en"]).copy()


def _build_setup_text(data: dict, lang: str) -> str:
    """Build setup message with current template data."""
    return (
        f"{t(lang, 'label_setting_desc')}: {data.get('story_desc') or '-'}\n"
        f"{t(lang, 'label_char_name')}: {data.get('char_name') or '-'}\n"
        f"{t(lang, 'label_char_age')}: {data.get('char_age') or '-'}\n"
        f"{t(lang, 'label_char_background')}: {data.get('char_background') or '-'}\n"
        f"{t(lang, 'label_char_personality')}: {data.get('char_personality') or '-'}\n"
        f"{t(lang, 'label_genre')}: {data.get('genre') or '-'}"
    )


async def _typing_loop(bot: Bot, chat_id: int, stop: asyncio.Event, interval: float = 4.0) -> None:
    """Continuously send typing action until stop is set."""
    while not stop.is_set():
        try:
            await bot.send_chat_action(chat_id, "typing")
            await asyncio.wait_for(stop.wait(), timeout=interval)
        except asyncio.TimeoutError:
            continue


async def _send_scene(
    chat_id: int,
    bot: Bot,
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


async def _has_pro(uid: int) -> bool:
    resp = await http_client.get("/api/v1/subscription/status/", headers={"X-User-Id": str(uid)})
    if resp.status_code != 200:
        return False
    data = resp.json()
    return data.get("status") == "active" and data.get("plan") == "pro"




@router.message(Command(commands=["my_game"]))
async def play_cmd(message: Message, state: FSMContext):
    """Begin game setup by sending initial template."""
    lang = await get_user_language(message.from_user.id)

    if not await _has_pro(message.from_user.id):
        await message.answer(
            t(lang, "create_story_webapp"),
            reply_markup=open_app_keyboard(settings.bots.web_url, lang),
        )
        return

    data = _get_default_template(lang)
    txt = _build_setup_text(data, lang)
    kb = setup_keyboard(lang)
    msg = await message.answer(txt, reply_markup=kb)
    await state.clear()
    await state.update_data(base_id=msg.message_id, template=data)


@router.callback_query(F.data.startswith("edit:"))
async def edit_field(call: CallbackQuery, state: FSMContext):
    """Prompt the user to edit a template field."""
    lang = await get_user_language(call.from_user.id)
    field = call.data.split(":", 1)[1]
    prompts = {
        "story_desc": t(lang, "enter_setting_desc"),
        "char_name": t(lang, "enter_char_name"),
        "char_age": t(lang, "enter_char_age"),
        "char_background": t(lang, "enter_char_background"),
        "char_personality": t(lang, "enter_char_personality"),
        "genre": t(lang, "enter_genre"),
    }
    msg = await call.message.answer(
        prompts[field],
        reply_markup=cancel_keyboard(lang),
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
    lang = await get_user_language(message.from_user.id)
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
    txt = _build_setup_text(template, lang)
    kb = setup_keyboard(lang)
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
    lang = await get_user_language(call.from_user.id)
    data = await state.get_data()
    template = data.get("template") or _get_default_template(lang)

    await call.answer()
    stop = asyncio.Event()
    typing_task = asyncio.create_task(
        _typing_loop(call.bot, call.message.chat.id, stop)
    )
    try:
        resp = await http_client.post(
            "/api/v1/stories/",
            json={
                "title": {lang: template.get("genre")},
                "story_desc": {lang: template.get("story_desc")},
                "genre": template.get("genre"),
                "character": {
                    "char_name": {lang: template.get("char_name")},
                    "char_age": template.get("char_age"),
                    "char_background": {lang: template.get("char_background")},
                    "char_personality": {lang: template.get("char_personality")},
                },
                "is_free": False,
            },
            headers={"X-User-Id": str(call.from_user.id)},
        )
        if resp.status_code != 201:
            if resp.status_code == 403:
                await call.message.answer(
                    t(lang, "create_story_webapp"),
                    reply_markup=open_app_keyboard(settings.bots.web_url, lang),
                )
                await state.clear()
            else:
                await call.message.answer(t(lang, "error_story"))
            return
        story_id = resp.json()["id"]
        resp = await http_client.post(
            "/api/v1/sessions/",
            json={"story_id": story_id},
            headers={"X-User-Id": str(call.from_user.id)},
        )
        if resp.status_code != 201:
            await call.message.answer(t(lang, "error_session"))
            return
        session_id = resp.json()["id"]
        resp = await http_client.get(
            f"/api/v1/sessions/{session_id}/",
            headers={"X-User-Id": str(call.from_user.id)},
        )
        if resp.status_code != 200:
            await call.message.answer(t(lang, "error_scene"))
            return
        scene = resp.json()

        active_sessions.setdefault(call.from_user.id, []).append(
            {"id": session_id, "title": template.get("genre")}
        )

        await call.message.delete()
        await _send_scene(
            call.message.chat.id, call.bot, scene, session_id, state
        )
    finally:
        stop.set()
        await typing_task


async def handle_external_game_start(story_id: str, user_id: int):
    lang = await get_user_language(user_id)
    state = dp_instance.fsm.resolve_context(bot=bot_instance, chat_id=user_id, user_id=user_id)
    resp = await http_client.get(
        f"/api/v1/stories/{story_id}/",
        params={"lang": lang},
        headers={"X-User-Id": str(user_id)},
    )
    if resp.status_code != 200:
        await bot_instance.send_message(user_id, t(lang, "error_generic"))
        return
    story = resp.json()
    world_resp = await http_client.get(
        f"/api/v1/worlds/{story['world_id']}/",
        params={"lang": lang},
        headers={"X-User-Id": str(user_id)},
    )
    image_url = None
    if world_resp.status_code == 200:
        image_url = world_resp.json().get("image_url")
    if image_url:
        try:
            await bot_instance.send_photo(user_id, image_url, caption=story.get("story_desc", ""))
        except Exception:
            await bot_instance.send_message(user_id, text=story.get("story_desc", ""))
    else:
        await bot_instance.send_message(user_id, story.get("story_desc", ""))
    await bot_instance.send_chat_action(user_id, "typing")
    resp = await http_client.post(
        "/api/v1/sessions/",
        json={"story_id": story_id},
        headers={"X-User-Id": str(user_id)},
    )
    if resp.status_code != 201:
        await bot_instance.send_message(user_id, t(lang, "error_generic"))
        return
    session_id = resp.json()["id"]
    resp = await http_client.get(
        f"/api/v1/sessions/{session_id}/",
        headers={"X-User-Id": str(user_id)},
    )
    if resp.status_code != 200:
        await bot_instance.send_message(user_id, t(lang, "error_generic"))
        return
    scene = resp.json()
    active_sessions.setdefault(user_id, []).append(
        {"id": session_id, "title": story.get("title")}
    )
    await _send_scene(user_id, bot_instance, scene, session_id, state)


@router.callback_query(F.data.startswith("preset:"))
async def select_preset(call: CallbackQuery | Message, state: FSMContext):
    story_id = call.data.split(":", 1)[1]
    uid = call.from_user.id
    lang = await get_user_language(uid)

    await call.answer()
    try:
        await call.message.delete()
    except Exception:
        pass
    resp = await http_client.get(
        f"/api/v1/stories/{story_id}/",
        params={"lang": lang},
        headers={"X-User-Id": str(uid)},
    )
    if resp.status_code != 200:
        await call.message.answer(t(lang, "error_generic"))
        return
    story = resp.json()
    world_resp = await http_client.get(
        f"/api/v1/worlds/{story['world_id']}/",
        params={"lang": lang},
        headers={"X-User-Id": str(uid)},
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

    stop = asyncio.Event()
    typing_task = asyncio.create_task(
        _typing_loop(call.bot, call.message.chat.id, stop)
    )
    try:
        resp = await http_client.post(
            "/api/v1/sessions/",
            json={"story_id": story_id},
            headers={"X-User-Id": str(uid)},
        )
        if resp.status_code != 201:
            await call.message.answer(t(lang, "error_generic"))
            return
        session_id = resp.json()["id"]
        resp = await http_client.get(
            f"/api/v1/sessions/{session_id}/",
            headers={"X-User-Id": str(uid)},
        )
        if resp.status_code != 200:
            await call.message.answer(t(lang, "error_generic"))
            return
        scene = resp.json()
        active_sessions.setdefault(uid, []).append(
            {"id": session_id, "title": story.get("title")}
        )
        await _send_scene(call.message.chat.id, call.bot, scene, session_id, state)
    finally:
        stop.set()
        await typing_task


@router.callback_query(F.data.startswith("choice:"))
async def make_choice(call: CallbackQuery, state: FSMContext):
    """Handle choice selection via inline button."""
    lang = await get_user_language(call.from_user.id)
    choice_idx = call.data.split(":", 1)[1]
    data = await state.get_data()
    session_id = data.get("session_id")
    last_scene_id = data.get("last_scene_id")
    last_text = data.get("last_scene_text", "")
    last_photo = data.get("last_scene_photo", False)
    choices_map = data.get("choices_map", {})
    choice = choices_map.get(choice_idx)
    if not session_id or not choice:
        await call.answer()
        return

    await call.answer()

    with suppress(TelegramBadRequest):
        if last_photo:
            await call.bot.edit_message_caption(
                chat_id=call.message.chat.id,
                message_id=last_scene_id,
                caption=f"{last_text}\n\n{t(lang, 'you_chose', choice=choice)}",
                reply_markup=None,
            )
        else:
            await call.bot.edit_message_text(
                text=f"{last_text}\n\n{t(lang, 'you_chose', choice=choice)}",
                chat_id=call.message.chat.id,
                message_id=last_scene_id,
                reply_markup=None,
            )

    stop = asyncio.Event()
    typing_task = asyncio.create_task(
        _typing_loop(call.bot, call.message.chat.id, stop)
    )
    try:
        resp = await http_client.post(
            f"/api/v1/sessions/{session_id}/choice/",
            json={"choice_text": choice},
            headers={"X-User-Id": str(call.from_user.id)},
        )
    finally:
        stop.set()
        await typing_task
    if resp.status_code != 201:
        await call.message.answer(t(lang, "error_generic"))
        return
    scene = resp.json()
    await _send_scene(
        call.message.chat.id, call.bot, scene, session_id, state
    )


@router.message(GamePlay.waiting_choice)
async def choice_text(message: Message, state: FSMContext):
    """Handle text choice input during gameplay."""
    lang = await get_user_language(message.from_user.id)
    choice = message.text
    data = await state.get_data()
    session_id = data.get("session_id")
    last_scene_id = data.get("last_scene_id")
    last_text = data.get("last_scene_text", "")
    last_photo = data.get("last_scene_photo", False)
    await message.delete()
    if not session_id:
        return

    with suppress(TelegramBadRequest):
        if last_photo:
            await message.bot.edit_message_caption(
                chat_id=message.chat.id,
                message_id=last_scene_id,
                caption=f"{last_text}\n\n{t(lang, 'you_chose', choice=choice)}",
                reply_markup=None,
            )
        else:
            await message.bot.edit_message_text(
                text=f"{last_text}\n\n{t(lang, 'you_chose', choice=choice)}",
                chat_id=message.chat.id,
                message_id=last_scene_id,
                reply_markup=None,
            )

    stop = asyncio.Event()
    typing_task = asyncio.create_task(
        _typing_loop(message.bot, message.chat.id, stop)
    )
    try:
        resp = await http_client.post(
            f"/api/v1/sessions/{session_id}/choice/",
            json={"choice_text": choice},
            headers={"X-User-Id": str(message.from_user.id)},
        )
    finally:
        stop.set()
        await typing_task
    if resp.status_code != 201:
        return
    scene = resp.json()

    await _send_scene(
        message.chat.id, message.bot, scene, session_id, state
    )


@router.message(Command("my_games"))
async def my_games_cmd(message: Message):
    """Show list of active games."""
    lang = await get_user_language(message.from_user.id)
    games = active_sessions.get(message.from_user.id)
    if not games:
        await message.answer(t(lang, "no_active_games"))
        return
    kb = games_keyboard(games)
    await message.answer(
        t(lang, "resume_game_prompt"), reply_markup=kb
    )


@router.callback_query(F.data.startswith("resume:"))
async def resume_game(call: CallbackQuery, state: FSMContext):
    """Resume a selected game session."""
    lang = await get_user_language(call.from_user.id)
    session_id = call.data.split(":", 1)[1]

    await call.answer()
    stop = asyncio.Event()
    typing_task = asyncio.create_task(
        _typing_loop(call.bot, call.message.chat.id, stop)
    )
    try:
        resp = await http_client.get(
            f"/api/v1/sessions/{session_id}/",
            headers={"X-User-Id": str(call.from_user.id)},
        )
        if resp.status_code != 200:
            await call.message.answer(t(lang, "error_generic"))
            return
        scene = resp.json()

        await call.message.delete()
        await _send_scene(call.message.chat.id, call.bot, scene, session_id, state)
    finally:
        stop.set()
        await typing_task


@router.message(Command("end_game"))
async def end_game_cmd(message: Message, state: FSMContext):
    """Finish current game session and clean up state."""
    lang = await get_user_language(message.from_user.id)
    data = await state.get_data()
    session_id = data.get("session_id")
    if not session_id:
        await message.answer(t(lang, "no_active_game"))
        return
    await http_client.delete(
        f"/api/v1/sessions/{session_id}/",
        headers={"X-User-Id": str(message.from_user.id)},
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
    await message.answer(t(lang, "session_finished"))
