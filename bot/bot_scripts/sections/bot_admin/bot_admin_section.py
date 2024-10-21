from os import path
from os import remove
from datetime import datetime

from aiogram import Router
from aiogram import types
from aiogram import F
from aiogram.filters import Command, and_f, StateFilter

from aiogram.fsm.context import FSMContext

from logger import PATH_TO_LOG
from logger import record_log, regist_error

from vars import bot, communicator

from ...FSMs import ShowContentListFSM
from ...FSMs import UpdateContentFSM

from ...custom_filters import IsBotAdminFilter
from ...custom_filters import IsPrivateChatFilter

from ...error_case import operate_error_case


from ...keyboards import create_keyboard_by_access
from ...keyboards import content_type_choose_kb
from ...keyboards import PagedKeyboard


admin_router = Router(name = "admin")


@admin_router.callback_query(and_f(F.data == "bot_admin:communication=list", IsBotAdminFilter(), StateFilter(None)))
async def get_bot_communication_type(callback : types.CallbackQuery, state : FSMContext):
    """
    Shows content of bot`s communicator
    """
    try:
        user_id = callback.from_user.id

        try:
            await callback.message.delete()
        except:
            pass

        await state.set_state(ShowContentListFSM.content_type)
        await callback.message.answer(communicator.get_message("choose_content_type"), reply_markup = content_type_choose_kb)

    except Exception as error:
        await operate_error_case(
            error_text = f"Update operating error: {error};", 
            error_type = type(error), 
            user_id = user_id,
            send_markup = create_keyboard_by_access(user_id, is_bot_admin = True),
            error_event = callback.model_dump_json()
        )
    finally:
        try: 
            await callback.answer()
        except: 
            pass


@admin_router.callback_query(and_f(F.data.startswith("content_type="), IsBotAdminFilter()), ShowContentListFSM.content_type)
async def show_bot_communication_content(callback : types.CallbackQuery, state : FSMContext):
    """
    Shows content of bot`s communicator
    """
    try:
        user_id = callback.from_user.id

        try:
            await callback.message.delete()
        except:
            pass

        content_type = callback.data.split("=", 1)[-1]

        match content_type:
            case "messages":
                content = communicator.get_messages_content()
                message_text = communicator.get_message("messages_list_header") + "\n"

            case "keyboards":
                content = communicator.get_keyboards_content()
                message_text = communicator.get_message("keyboards_list_header") + "\n"

            case unexpected_content_type:
                raise ValueError(f"Unexpected content type: {unexpected_content_type}")
            
        text_blocks = []
        await state.update_data(header = message_text)

        block = ""
        for key, text in content.items():
            text = "\n" + communicator.get_message("content_list_pattern").replace(
                    "*KEY*", 
                    f'""{key}""'
                ).replace(
                    "*CONTENT_TEXT*",
                    f'""{text}""'
                ) + "\n"
            
            if len(block) + len(text) > 3900:
                text_blocks.append(block)
                block = text
            else:
                block += text
        else:
            text_blocks.append(block)
        
        if len(text_blocks) == 1:
            message_text += "".join(text_blocks)

            await callback.message.answer(message_text, parse_mode = None)
            await state.clear()
            await callback.message.answer(
                text = communicator.get_message("menu_header"),
                reply_markup = create_keyboard_by_access(user_id, is_bot_admin = True),
            )
            return

        paged_kb_object = PagedKeyboard(
            items = text_blocks, 
            callback_header = "bot_admin:communication=list", 
        )
        message_content = paged_kb_object.next()
        await state.update_data(paged_kb_object = paged_kb_object)
        
        await callback.message.answer(text = message_content.message_text, reply_markup = message_content.keyboard_markup, parse_mode = None)

    except Exception as error:
        await operate_error_case(
            error_text = f"Update operating error: {error};", 
            error_type = type(error), 
            user_id = user_id,
            current_state = state,
            send_markup = create_keyboard_by_access(user_id, is_bot_admin = True),
            error_event = callback.model_dump_json(),
        )
    finally:
        try: 
            await callback.answer()
        except: 
            pass


@admin_router.callback_query(and_f(F.data.startswith("bot_admin:communication=list=")), ShowContentListFSM.content_type)
async def update_bot_communication(callback : types.CallbackQuery, state : FSMContext):
    try:
        user_id = callback.from_user.id

        state_data = await state.get_data()
        paged_kb_object : PagedKeyboard = state_data.get("paged_kb_object")
        if not paged_kb_object:
            raise ValueError("Paged keyboard is not found")

        action = callback.data.rsplit("=", 1)[-1]
        match action:
            case "next":
                message_content = paged_kb_object.next()
            case "previous":
                message_content = paged_kb_object.previous()
            case "stop":
                await state.clear()
                await callback.message.edit_reply_markup(reply_markup = None)
                await callback.message.answer(
                    text = communicator.get_message("menu_header"),
                    reply_markup = create_keyboard_by_access(user_id, is_bot_admin = True),
                )
                return
            case undefined_case:
                raise ValueError(f"Unexpected action: {undefined_case}")

        message_text = state_data.get("header") + message_content.message_text

        await callback.message.edit_text(message_text, parse_mode = None)
        await callback.message.edit_reply_markup(reply_markup = message_content.keyboard_markup) 

    except Exception as error:
        await operate_error_case(
            error_text = f"Update operating error: {error};", 
            error_type = type(error), 
            user_id = user_id,
            current_state = state,
            send_markup = create_keyboard_by_access(user_id, is_bot_admin = True),
            error_event = callback.model_dump_json(),
        )
    finally:
        try: 
            await callback.answer()
        except: 
            pass


@admin_router.callback_query(and_f(F.data.startswith("bot_admin:communication=change_"), StateFilter(None)))
async def change_bot_communication(callback : types.CallbackQuery, state : FSMContext):
    """
    """
    try:
        user_id = callback.from_user.id

        try:
            await callback.message.delete()
        except:
            pass

        item_type = callback.data.rsplit("_", 1)[-1]
        match item_type:
            case "msg":
                item_type = "message"
                message_text = communicator.get_message("message_key_request")
            case "kb":
                item_type = "keyboard"
                message_text = communicator.get_message("keyboard_key_request")
            case undefined_case:
                raise ValueError(f"Unexpected item type: {undefined_case}")

        await state.set_state(UpdateContentFSM.content_key)
        await state.update_data(item_type = item_type)
        await callback.message.answer(message_text)

    except Exception as error:
        await operate_error_case(
            error_text = f"Update operating error: {error};", 
            error_type = type(error), 
            user_id = user_id,
            current_state = state,
            send_markup = create_keyboard_by_access(user_id, is_bot_admin = True),
            error_event = callback.model_dump_json(),
        )
    finally:
        try: 
            await callback.answer()
        except: 
            pass


@admin_router.message(and_f(IsBotAdminFilter(), IsPrivateChatFilter()), UpdateContentFSM.content_key)
async def get_content_key(message : types.Message, state : FSMContext):
    """
    """
    try:
        user_id = message.from_user.id
                
        content_key = message.text
        state_data = await state.get_data()
        item_type = state_data.get("item_type")
        match item_type:
            case "message":
                existed_keys = communicator.get_messages_content()
            case "keyboard":
                existed_keys = communicator.get_keyboards_content()
            case undefined_case:
                raise ValueError(f"Unexpected item type: {undefined_case}")
        
        if not (content_key in existed_keys):
            await message.answer(communicator.get_message("no_such_content_key"))
            await state.clear()
            await message.answer(
                text = communicator.get_message("menu_header"),
                reply_markup = create_keyboard_by_access(user_id, is_bot_admin = True),
            )
            return
        
        await state.update_data(content_key = content_key)

        await state.set_state(UpdateContentFSM.new_content)
        await message.answer(communicator.get_message(f"new_{item_type}_content"))

    except Exception as error:
        await operate_error_case(
            error_text = f"Update operating error: {error};", 
            error_type = type(error), 
            user_id = user_id,
            current_state = state,
            send_markup = create_keyboard_by_access(user_id, is_owner = True),
            error_event = message.model_dump_json()
        )


@admin_router.message(and_f(IsBotAdminFilter(), IsPrivateChatFilter()), UpdateContentFSM.new_content)
async def get_new_content(message : types.Message, state : FSMContext):
    """
    """
    try:
        user_id = message.from_user.id
                
        new_value = message.text
        
        state_data = await state.get_data()
        content_key = state_data.get("content_key")
        if content_key is None:
            raise ValueError("content key is not defined")
        
        item_type = state_data.get("item_type")
        match item_type:
            case "message":
                result = communicator.update_message_content(content_key, new_value)
            
            case "keyboard":
                if len(new_value) > 64:
                    await message.answer(communicator.get_message("invalid_kb_header"))
                    return
                result = communicator.update_keyboard_content(content_key, new_value)

            case undefined_case:
                raise ValueError(f"Unexpected item type: {undefined_case}")
        
        if result and communicator.update_patterns():
            await message.answer(communicator.get_message("content_updated"))
        else:
            await message.answer(communicator.get_message("content_not_updated"))
    
    except Exception as error:
        await operate_error_case(
            error_text = f"Update operating error: {error};", 
            error_type = type(error), 
            user_id = user_id,
            current_state = state,
            error_event = message.model_dump_json()
        )

    finally:
        await state.clear()
        await message.answer(
            text = communicator.get_message("menu_header"),
            reply_markup = create_keyboard_by_access(user_id, is_bot_admin = True),
        )


@admin_router.message(and_f(IsPrivateChatFilter(), Command(commands = ["getlog"]), IsBotAdminFilter()))
async def send_log(message : types.Message):
    """
    Sends log to requester, removes log file and creates new.
    """
    user_id = message.from_user.id
    try:
        # Log openning and sending
        creation_time = path.getctime(PATH_TO_LOG)
        await bot.send_document(
            chat_id = user_id, 
            document = types.FSInputFile(PATH_TO_LOG), 
            caption = f"#LOG\n\nBot`s log starting from {datetime.fromtimestamp(creation_time)} until {datetime.now()}"
        )

        try: remove(PATH_TO_LOG)
        except: ...

        # Log clearing:
        with open(PATH_TO_LOG, "w") as log_file:
            log_file.write(f"[Log is cleared now: {datetime.now()}]\n")

    except Exception as error:
        print(f"{error=}")
        await operate_error_case(text = f"Getting log_error: {error}", error_type = type(error), call_user = False)
    