from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

remove_kb = ReplyKeyboardRemove()


def example_reply_kb():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(
        text='Reply Button1',
    )

    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=False,
        )
