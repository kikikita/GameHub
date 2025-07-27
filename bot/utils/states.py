from aiogram.fsm.state import StatesGroup, State


class Basic(StatesGroup):
    basic = State()


class GameSetup(StatesGroup):
    waiting_input = State()


class GamePlay(StatesGroup):
    waiting_choice = State()
