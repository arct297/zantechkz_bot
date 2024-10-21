from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from vars import communicator


def generate_chat_activation_kb(builder : bool = False) -> InlineKeyboardBuilder | InlineKeyboardMarkup:
    chat_activation_kb_builder = InlineKeyboardBuilder()
    chat_activation_kb_builder.button(text = communicator.get_keyboard_title("chat_activation"), callback_data = "group_chat:chat=activate")
    return chat_activation_kb_builder if builder else chat_activation_kb_builder.as_markup() 