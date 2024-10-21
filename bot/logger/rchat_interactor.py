"""
This module provides ways function for sending message to developer of developer group through Telgeram.
The Telegram ids of chats must be defined in project`s config 
"""

import requests

from .logger import record_log
from config import get_bot_reporter_token, get_report_chat_id, get_dev_tg_id

REPORTER_BOT_TOKEN = get_bot_reporter_token()
REPORT_CHAT_ID = get_report_chat_id()
DEV_ID = get_dev_tg_id()


def _send_message_via_bot(message_text : str, receiver_id : int) -> None:
    """
    Sends message-text through bot to passed receiver.

    In case of error during message sending prints (through print function) text about request failing and passed args.
    

    Parameters:
    -----------
    message_text : str
        text of the message
    receiver_id : int
        Telegram-ID of receivering chat 
        
    Returns:
    --------
        None
    """

    api_url = f'https://api.telegram.org/bot{REPORTER_BOT_TOKEN}/sendMessage'
    params = {
        'chat_id': receiver_id,
        'text': message_text,
        # 'parse_mode' : 'Markdown'
    }
    response = requests.post(api_url, params=params)
    if response.status_code != 200:
        record_log(f"Message was not sent to receiver. Response: Status<{response.status_code}> JSON: {response.json()}; {message_text=} {receiver_id=}")


def send_message_to_report_chat(message_text : str) -> None:
    """
    Sends message-text through bot to report chat.

    Uses _send_message_via_bot function.    

    Parameters:
    -----------
    message_text : str
        text of the message
        
    Returns:
    --------
        None
    """
    _send_message_via_bot(message_text, REPORT_CHAT_ID)


def send_message_to_developer(message_text : str) -> None:
    """
    Sends message-text through bot to developer chat.

    Uses _send_message_via_bot function.    

    Parameters:
    -----------
    message_text : str
        text of the message
        
    Returns:
    --------
        None
    """
    _send_message_via_bot(message_text, DEV_ID)

