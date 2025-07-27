"""Fallback handler for unknown messages."""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()


@router.message(F.text)
async def unknown_message(message: Message, state: FSMContext):
    """Reply when user input is not recognized by any handler."""

    answer = (
        "🤖 <b>Agent:</b> I didn't understand that. "
        "Please ask me something else or use the buttons below."
    )
    await message.answer(answer, parse_mode="Markdown")
