from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from vars import communicator


def generate_bot_admin_kb_builder():
    bot_admin_kb_builder = InlineKeyboardBuilder()
    bot_admin_kb_builder.button(text = communicator.get_keyboard_title("communication_list"), callback_data = "bot_admin:communication=list")
    # bot_admin_kb_builder.button(text = communicator.get_keyboard_title("update_communication"), callback_data = "bot_admin:communication=update")
    bot_admin_kb_builder.button(text = communicator.get_keyboard_title("update_message_text"), callback_data = "bot_admin:communication=change_msg")
    bot_admin_kb_builder.button(text = communicator.get_keyboard_title("update_keyboard_text"), callback_data = "bot_admin:communication=change_kb")
    return bot_admin_kb_builder


def generate_content_type_choose_kb_builder():
    content_type_choose_kb_builder = InlineKeyboardBuilder()
    content_type_choose_kb_builder.button(text = communicator.get_keyboard_title("messages_content_type"), callback_data = "content_type=messages")
    content_type_choose_kb_builder.button(text = communicator.get_keyboard_title("keyboards_content_type"), callback_data = "content_type=keyboards")
    content_type_choose_kb_builder.adjust(1)
    return content_type_choose_kb_builder


