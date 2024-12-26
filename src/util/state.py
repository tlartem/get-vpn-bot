from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    how_often_use = State()
    does_youtube_use = State()


class AddServerStates(StatesGroup):
    waiting_for_json = State()
