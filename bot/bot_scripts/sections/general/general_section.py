from aiogram import Router

from aiogram.filters import Command, CommandStart, StateFilter, and_f


from aiogram.types import Message

from aiogram import html, F

from logger import record_log, regist_error

from vars import communicator, bot_db_client

from ...custom_filters import IsPrivateChatFilter

from ...error_case import operate_error_case

from ...keyboards import create_keyboard_by_access

general_router = Router(name = "general")


@general_router.message(and_f(CommandStart(), IsPrivateChatFilter(), StateFilter(None)))
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    try:
        user_id = message.from_user.id

        # await message.answer(
        #     text = communicator.get_message("start").replace("*USER_ID*", f"{message.from_user.id}"),
        #     reply_markup = None
        # )

        # username = message.from_user.username
        # first_name = message.from_user.first_name
        # last_name = message.from_user.last_name
        # if not bot_db_client.register_user(
        #     user_id = user_id,
        #     username = username,
        #     first_name = first_name,
        #     last_name = last_name
        # ):
        #     regist_error(
        #         error_description = "User ("
        #             f"{user_id=}, {username=}, {first_name=}, {last_name=}) " 
        #             "has not been registered in bot database as user.",
        #         error_type = "database response is not ok"
        #     )
        
    except Exception as error:
        await operate_error_case(
            error_text = f"Handle start command error: {error}\n\nMessage: {message}",
            error_type = type(error),
            user_id = message.from_user.id,
        )    


@general_router.message(and_f(F.text.lower() == "меню", IsPrivateChatFilter(), StateFilter(None)))
async def menu(message: Message) -> None:
    """
    This handler operates sending menu
    """
    try:
        user_id = message.from_user.id

        await message.answer(
            text = communicator.get_message("menu_header"),
            reply_markup = create_keyboard_by_access(user_id)
        )
        
    except Exception as error:
        await operate_error_case(
            error_text = f"Handle update error: {error}\n\nMessage: {message}",
            error_type = type(error),
            user_id = message.from_user.id,
        )    