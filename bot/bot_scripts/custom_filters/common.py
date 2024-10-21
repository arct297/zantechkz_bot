from aiogram import types

from aiogram.filters import BaseFilter

import vars

CHAT_TYPES : tuple[str] = ("group", "supergroup")


class IsPrivateChatFilter(BaseFilter):
    async def __call__(self, incomming_entity : types.Message | types.CallbackQuery) -> bool:
        return True if isinstance(incomming_entity, types.CallbackQuery) else incomming_entity.chat.type == "private"
    

class IsGroupChatFilter(BaseFilter):
    async def __call__(self, incomming_entity : types.Message | types.CallbackQuery | types.MessageReactionUpdated) -> bool:
        return True if (incomming_entity.chat.type in CHAT_TYPES) else False
    

class IsCustomerChatFilter(BaseFilter):
    async def __call__(self, message : types.Message | types.MessageReactionUpdated) -> bool:
        chat_info = vars.bot_db_client.get_chat_info(message.chat.id)
        if (not chat_info) or (chat_info.get("chat_type") != "customer"):
            return False
        return True
    