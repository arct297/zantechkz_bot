from aiogram.filters.state import State, StatesGroup


class UpdateContentFSM(StatesGroup):
    content_key = State()
    new_content = State()


class ShowContentListFSM(StatesGroup):
    content_type = State()


    