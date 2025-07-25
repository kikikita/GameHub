from typing import Iterable

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def example_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='✅ Button1', callback_data='example:Button1')
    kb.button(text='❌ Button2', callback_data='example:Button2')
    kb.adjust(2)
    return kb.as_markup()
