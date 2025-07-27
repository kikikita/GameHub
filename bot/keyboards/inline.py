from typing import Iterable

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def example_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Button1", callback_data="example:Button1")
    kb.button(text="❌ Button2", callback_data="example:Button2")
    kb.adjust(2)
    return kb.as_markup()


def setup_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for the game setup step."""
    kb = InlineKeyboardBuilder()
    kb.button(text="Setting", callback_data="edit:setting_desc")
    kb.button(text="Char Name", callback_data="edit:char_name")
    kb.button(text="Char Age", callback_data="edit:char_age")
    kb.button(text="Char Background", callback_data="edit:char_background")
    kb.button(text="Char Personality", callback_data="edit:char_personality")
    kb.button(text="Genre", callback_data="edit:genre")
    kb.button(text="Начать игру", callback_data="start_game")
    kb.adjust(2, 2, 2, 1)
    return kb.as_markup()


def cancel_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Отмена", callback_data="cancel")
    kb.adjust(1)
    return kb.as_markup()


def choices_keyboard(choices: Iterable[str]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for choice in choices:
        kb.button(text=choice, callback_data=f"choice:{choice}")
    kb.adjust(1)
    return kb.as_markup()


def games_keyboard(games: Iterable[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for game in games:
        title = game.get("title") or str(game.get("id"))
        kb.button(text=title, callback_data=f"resume:{game['id']}")
    kb.adjust(1)
    return kb.as_markup()
