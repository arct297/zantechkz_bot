from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

from vars import bot_db_client, communicator

from .bot_admins_kb import generate_bot_admin_kb_builder

def create_keyboard_by_access(
        user_id : int = 0, 
        # is_manager : bool | None = None, 
        # is_owner : bool | None = None,
        is_bot_admin : bool | None = None,
    ) -> InlineKeyboardMarkup:
    """
    Creates InlineKeyboardMarkup according to user's status
    """

    builder = InlineKeyboardBuilder()

    # if (is_manager != False) and (is_manager or (user_id in bot_db_client.get_managers_list(only_ids = True))):
    #     builder.attach(generate_manager_kb_builder())
    
    # if (is_owner != False) and (is_owner or (user_id in bot_db_client.get_owners_list(only_ids = True))):
    #     builder.attach(generate_owner_kb_builder())
    
    if (is_bot_admin != False) and (is_bot_admin or (user_id in bot_db_client.get_bot_admins_list())):
        builder.attach(generate_bot_admin_kb_builder())

    builder.adjust(1)

    return builder.as_markup()
