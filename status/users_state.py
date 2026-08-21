from aiogram.fsm.state import StatesGroup, State
class users_create_menu(StatesGroup):
    text_state = State()
    photo_state_question = State()
    photo_state = State()
    check_state = State()
    