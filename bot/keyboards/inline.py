"""Inline keyboards used in game interactions."""

from typing import Iterable

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def example_keyboard() -> InlineKeyboardMarkup:
    """Return a demo inline keyboard used for tests."""

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Button1", callback_data="example:Button1")
    kb.button(text="❌ Button2", callback_data="example:Button2")
    kb.adjust(2)
    return kb.as_markup()


def setup_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for the game setup step."""
    kb = InlineKeyboardBuilder()
    kb.button(text="Setting", callback_data="edit:world_desc")
    kb.button(text="Char Name", callback_data="edit:char_name")
    kb.button(text="Char Age", callback_data="edit:char_age")
    kb.button(text="Char Background", callback_data="edit:char_background")
    kb.button(text="Char Personality", callback_data="edit:char_personality")
    kb.button(text="Genre", callback_data="edit:genre")
    kb.button(text="Начать игру", callback_data="start_game")
    kb.adjust(2, 2, 2, 1)
    return kb.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    """Keyboard with a single cancel button."""

    kb = InlineKeyboardBuilder()
    kb.button(text="Отмена", callback_data="cancel")
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


def stories_keyboard(stories: Iterable[dict], web_url: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for story in stories:
        kb.button(text=story.get("title"), callback_data=f"preset:{story['id']}")
    kb.adjust(2)
    kb.row(InlineKeyboardButton(text="✨ Откройте все истории", url=web_url))
    return kb.as_markup()


def open_app_keyboard(web_url: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text="✨ Откройте веб-приложение", url=web_url))
    return kb.as_markup()
