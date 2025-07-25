from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards.inline import consent_kb
from settings import settings

router = Router()


@router.message(F.text)
async def unknown_message(message: Message, state: FSMContext):
    answer = (
        "🤖 <b>Agent:</b> I didn't understand that. "
        "Please ask me something else or use the buttons below."
    )
    await message.answer(answer, parse_mode="Markdown")
