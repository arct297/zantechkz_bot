from aiogram import types

from aiogram.filters import BaseFilter

from vars import bot_db_client


class IsBotAdminFilter(BaseFilter):
    async def __call__(self, incoming_entity : types.Message | types.CallbackQuery) -> bool:
        return incoming_entity.from_user.id in bot_db_client.get_bot_admins_list()
    