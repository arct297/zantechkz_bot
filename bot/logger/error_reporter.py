"""
This module provides regist_error function for error registering, logging it and reporting to developers.
"""

from .logger import record_log
from .caller_definer import define_caller 
from .rchat_interactor import send_message_to_report_chat
from .rchat_interactor import send_message_to_developer


def regist_error(
        error_description : str = "W/O description", 
        error_type : str = "undefined", 
        raised_by : str = None, 
        only_dev : bool = True, 
        silent_mode : bool = False,
        from_source : bool = False,
    ) -> None:
    """
    Registers error into log.log and calls developer through telegram bot.

    ".logger.record_log()" is used for logging

    ".rchat_interactor.send_message_to_report_chat()" and ".rchat_interactor.send_message_to_developer()" are used accordingly for sending message to receiver. 

    In case of error during error registering prints (through print function) error of registering with passed parameters.
    

    Parameters:
    -----------
    error_description : str
        text of the error
    error_type : str
        type of the error 
    raised_by : str
        who is registering the error. If this parameter is not passed, caller is full module path to caller 
    only_dev : bool
        by default this flag is True. This flag defines who will get the message about error. If it is True, then only developer. Otherwise, message will be sent to both: dev and report group. 
    silent_mode : bool    
        by default this flag is False. If flag is True, then message won`t be sent to someone.

    Returns:
    --------
        None
    """

    try:
        if raised_by is None:
            raised_by = define_caller(is_full_path = True, from_source = from_source)

        record_log(is_error = True, source = raised_by, record_text = f"\n<--ERROR TEXT BEGINNING-->\n{error_description}\n<--ERROR TEXT END-->", error_type = error_type)
        
        if silent_mode:
            return
        
        if only_dev:
            send_message_to_developer(f"Report about error\n\nType: {error_type}\nDescription: {error_description}\n\nFrom: ```path {raised_by}```""")
        else:
            send_message_to_developer(f"Report about error\n\nType: {error_type}\nDescription: {error_description}\n\nFrom: ```path {raised_by}```")
            send_message_to_report_chat(f"Отчёт об ошибке.\n\nТип ошибки: {error_type}\nОписание: {error_description}\n\nИсточник: ```path {raised_by}```")
        
    except Exception as error:
        print(f"Error in registError:\n{error}\nType: {type(error)} {error_description=} {error_type=} {raised_by=} {only_dev=}")
