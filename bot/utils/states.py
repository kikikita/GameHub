"""FSM states used in the bot."""

from aiogram.fsm.state import State, StatesGroup


class Basic(StatesGroup):
    """State group for simple interactions."""

    basic = State()


class GameSetup(StatesGroup):
    """States related to game template setup."""

    waiting_input = State()


class GamePlay(StatesGroup):
    """States used during active gameplay."""

    waiting_choice = State()
