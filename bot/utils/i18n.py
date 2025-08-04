from __future__ import annotations

import httpx
from settings import settings


TRANSLATIONS = {
    "en": {
        "choose_language": "Choose your language",
        "registration_failed": "Failed to register",
        "start_welcome": "👋 Hello, <b>{name}</b>!\nWelcome to <b>Immersia</b>",
        "help_message": (
            "ℹ️ <b>Help</b>\n\n"
            "<b>/new_game</b> — create a new game\n"
            "<b>/my_games</b> — list your active games\n"
            "<b>/end_game</b> — finish current session\n"
            "<b>/help</b> — show this message"
        ),
        "no_stories": "No available stories",
        "choose_story": "Choose your story:",
        "open_all_stories": "✨ Open all stories",
        "open_web_app": "✨ Open web app",
        "create_story_webapp": "Create your own story in the web app",
        "create_story_btn": "✨{cost} Create own story",
        "setup_setting": "Setting",
        "setup_char_name": "Char Name",
        "setup_char_age": "Char Age",
        "setup_char_background": "Char Background",
        "setup_char_personality": "Char Personality",
        "setup_genre": "Genre",
        "start_game": "Start game",
        "cancel": "Cancel",
        "enter_setting_desc": "Enter setting description",
        "enter_char_name": "Enter character name",
        "enter_char_age": "Enter character age",
        "enter_char_background": "Enter character background",
        "enter_char_personality": "Enter character personality",
        "enter_genre": "Enter genre",
        "error_story": "Story error",
        "error_session": "Session error",
        "error_scene": "Scene error",
        "error_generic": "Error",
        "you_chose": "You chose: {choice}",
        "no_active_games": "You have no active games yet. Use /new_game to start.",
        "resume_game_prompt": "You can continue one of your current games:",
        "no_active_game": "No active game",
        "session_finished": "Session finished",
        "not_enough_wishes": "😯✨ Not enough wishes to create a story",
        "top_up_whishes": "✨ Top up wishes",
        "top_up_energy": "⚡️ Top up energy",
        "not_enough_energy_title": "😯⚡️ Not enough energy to make a choice.",
        "not_enough_energy_subtitle": "Top up your energy or wait for it to recharge — you gain 1 energy every hour.",
        "label_setting_desc": "Setting Description",
        "label_char_name": "Character Name",
        "label_char_age": "Character Age",
        "label_char_background": "Character Background",
        "label_char_personality": "Character Personality",
        "label_genre": "Genre",
        "genre_Horror": "Horror",
        "genre_Romantic": "Romantic",
        "genre_Adventure": "Adventure",
        "genre_Fantasy": "Fantasy",
        "genre_Sci-Fi": "Sci-Fi",
    },
    "ru": {
        "choose_language": "Выберите язык",
        "registration_failed": "Не удалось зарегистрироваться",
        "start_welcome": "👋 Привет, <b>{name}</b>!\nДобро пожаловать в <b>Immersia</b>",
        "help_message": (
            "ℹ️ <b>Помощь</b>\n\n"
            "<b>/new_game</b> — создать новую игру\n"
            "<b>/my_games</b> — список ваших активных игр\n"
            "<b>/end_game</b> — завершить текущую сессию\n"
            "<b>/help</b> — показать это сообщение"
        ),
        "no_stories": "Нет доступных историй",
        "choose_story": "Выберите вашу историю:",
        "open_all_stories": "✨ Откройте все истории",
        "open_web_app": "✨ Откройте веб-приложение",
        "create_story_webapp": "Создай собственную историю в веб-приложении",
        "create_story_btn": "✨{cost} Создать свою историю",
        "setup_setting": "Сеттинг",
        "setup_char_name": "Имя персонажа",
        "setup_char_age": "Возраст персонажа",
        "setup_char_background": "Предыстория",
        "setup_char_personality": "Характер",
        "setup_genre": "Жанр",
        "start_game": "Начать игру",
        "cancel": "Отмена",
        "enter_setting_desc": "Введите описание сеттинга",
        "enter_char_name": "Введите имя персонажа",
        "enter_char_age": "Введите возраст персонажа",
        "enter_char_background": "Введите предысторию персонажа",
        "enter_char_personality": "Введите характер персонажа",
        "enter_genre": "Введите жанр",
        "error_story": "Ошибка истории",
        "error_session": "Ошибка сессии",
        "error_scene": "Ошибка сцены",
        "error_generic": "Ошибка",
        "you_chose": "Вы выбрали: {choice}",
        "no_active_games": "У вас пока нет активных игр. Используйте /new_game, чтобы начать.",
        "resume_game_prompt": "Вы можете продолжить одну из текущих игр:",
        "no_active_game": "Нет активной игры",
        "session_finished": "Сессия завершена",
        "not_enough_wishes": "😯✨ Не хватает желаний для создания истории.",
        "top_up_whishes": "✨ Пополнить желания",
        "top_up_energy": "⚡️ Пополнить энергию",
        "not_enough_energy_title": "😯⚡️ Недостаточно энергии для совершения выбора.",
        "not_enough_energy_subtitle": "Пополните энергию или подождите восстановления — 1 энергия начисляется каждый час.",
        "label_setting_desc": "Описание сеттинга",
        "label_char_name": "Имя персонажа",
        "label_char_age": "Возраст персонажа",
        "label_char_background": "Предыстория персонажа",
        "label_char_personality": "Характер персонажа",
        "label_genre": "Жанр",
        "genre_Horror": "Ужасы",
        "genre_Romantic": "Романтика",
        "genre_Adventure": "Приключение",
        "genre_Fantasy": "Фэнтези",
        "genre_Sci-Fi": "Научная фантастика",
    },
}

DEFAULT_LANG = "en"


# Reusable HTTPX client for backend requests
client = httpx.AsyncClient(
    base_url=settings.bots.app_url,
    timeout=10.0,
    headers={"X-Server-Auth": settings.bots.server_auth_token.get_secret_value()},
)


_LANG_CACHE: dict[int, str] = {}


def t(lang: str, key: str, **kwargs) -> str:
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANG])
    text = lang_dict.get(key) or TRANSLATIONS[DEFAULT_LANG].get(key, "")
    return text.format(**kwargs)


async def get_user_language(uid: int, *, refresh: bool = False) -> str:
    """Return the language for a user, using a simple in-memory cache."""

    if not refresh and uid in _LANG_CACHE:
        return _LANG_CACHE[uid]

    resp = await client.get(
        "/api/v1/users/me/",
        headers={"X-User-Id": str(uid)},
    )
    if resp.status_code == 200:
        lang = resp.json().get("language") or DEFAULT_LANG
    else:
        lang = DEFAULT_LANG
    _LANG_CACHE[uid] = lang
    return lang


def set_user_language(uid: int, lang: str) -> None:
    """Update the cached language for a user (e.g. after miniapp change)."""
    _LANG_CACHE[uid] = lang
