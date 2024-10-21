from aiogram.fsm.context import FSMContext

from aiogram.types import InlineKeyboardMarkup

from logger import regist_error, define_caller

from vars import bot, communicator


async def operate_error_case(
        error_text : str = "Something went wrong",
        error_type : Exception = "undefined error type",
        source : str = None,
        user_id : int = 0,
        call_user : bool = True, 
        message_to_user : str = None,   
        save_state : bool = False,
        current_state : FSMContext = None,
        send_markup : InlineKeyboardMarkup = None,
        error_event : str = None,
) -> None:
    try:
        if message_to_user is None:
            message_to_user = communicator.get_message("default_error")
        # getting current state and finish it if neccessary 
        try:
            if (not save_state) and (current_state) and (await current_state.get_state() is not None): 
                await current_state.clear()                
        except: 
            pass

        error_description = f"An error was happened in bot script.\n\nError type: {error_type}\nUser id: {user_id}\nCurrent state: {await current_state.get_state() if current_state else None}\nDescription: {error_text}"
        regist_error(
            error_description = error_description, 
            error_type = "bot script error",
            raised_by = source if source else define_caller(is_full_path = True, from_source = True),
            from_source = True 
        )
        
        if error_event:
            regist_error(f"Error event: {error_event}", "event-information", "event-information", silent_mode = True)

        if call_user and user_id:
            await bot.send_message(user_id, message_to_user, reply_markup = send_markup)
        
    except Exception as error_case_error:
        regist_error(
            error_description = f"Error was happened when error case was operated: {error_case_error}", 
            error_type = type(error_case_error),
        )