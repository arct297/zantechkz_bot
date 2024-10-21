from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from vars import communicator


def generate_owner_kb_builder():
    owner_kb_builder = InlineKeyboardBuilder()
    owner_kb_builder.button(text = communicator.get_keyboard_title("managers_list"), callback_data = "owner:manager=list")
    owner_kb_builder.button(text = communicator.get_keyboard_title("add_manager"), callback_data = "owner:manager=add")
    owner_kb_builder.button(text = communicator.get_keyboard_title("delete_manager"), callback_data = "owner:manager=delete")
    return owner_kb_builder
