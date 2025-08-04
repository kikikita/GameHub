"""Inline keyboards used in game interactions."""

from typing import Iterable

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.i18n import t
from settings import settings


def example_keyboard() -> InlineKeyboardMarkup:
    """Return a demo inline keyboard used for tests."""

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Button1", callback_data="example:Button1")
    kb.button(text="❌ Button2", callback_data="example:Button2")
    kb.adjust(2)
    return kb.as_markup()


def setup_keyboard(
    lang: str, wishes_cost: int | None = None
) -> InlineKeyboardMarkup:
    """Keyboard for the game setup step."""
    if wishes_cost is None:
        wishes_cost = settings.create_story_cost

    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "setup_setting"), callback_data="edit:story_desc")
    kb.button(text=t(lang, "setup_char"), callback_data="edit:char_desc")
    kb.button(text=t(lang, "setup_genre"), callback_data="edit:genre")
    kb.button(
        text=t(lang, "create_story_btn", cost=wishes_cost),
        callback_data="start_game",
    )
    kb.adjust(3, 1)
    return kb.as_markup()


def cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Keyboard with a single cancel button."""

    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "cancel"), callback_data="cancel")
    kb.adjust(1)
    return kb.as_markup()


def choices_keyboard(choices: Iterable[dict]) -> InlineKeyboardMarkup:
    """Keyboard with a list of choices using short callback data."""

    kb = InlineKeyboardBuilder()
    for idx, choice in enumerate(choices):
        kb.button(text=choice["text"], callback_data=f"choice:{idx}")
    kb.adjust(1)
    return kb.as_markup()


def games_keyboard(games: Iterable[dict]) -> InlineKeyboardMarkup:
    """Keyboard to resume active games."""

    kb = InlineKeyboardBuilder()
    for game in games:
        title = game.get("title") or str(game.get("id"))
        kb.button(text=title, callback_data=f"resume:{game['id']}")
    kb.adjust(1)
    return kb.as_markup()


def language_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Русский", callback_data="lang:ru")
    kb.button(text="English", callback_data="lang:en")
    kb.adjust(2)
    return kb.as_markup()


def stories_keyboard(stories: Iterable[dict], web_url: str, lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for story in stories:
        title = story.get("title")
        if isinstance(title, dict):
            title = title.get(lang) or title.get("en") or next(iter(title.values()), "")
        kb.button(text=title, callback_data=f"preset:{story['id']}")
    kb.adjust(2)
    kb.row(
        InlineKeyboardButton(
            text=t(lang, "open_all_stories"),
            web_app=WebAppInfo(url=web_url),
        )
    )
    return kb.as_markup()


def open_app_keyboard(web_url: str, lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(
            text=t(lang, "open_web_app"), web_app=WebAppInfo(url=web_url)
        )
    )
    return kb.as_markup()


def top_up_keyboard(web_url: str, lang: str, type: str = 'energy') -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if type == 'energy':
        kb.row(
            InlineKeyboardButton(
                text=t(lang, "top_up_energy"), web_app=WebAppInfo(url=web_url)
            )
        )
    else:
        kb.row(
            InlineKeyboardButton(
                text=t(lang, "top_up_wishes"), web_app=WebAppInfo(url=web_url)
            )
        )
    return kb.as_markup()
