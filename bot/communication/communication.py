from logger import record_log, regist_error

from .messages_patterns_db_client import MessagesPatternsDBClient

class Communicator:
    messages_patterns : dict = {}
    keyboards_patterns : dict = {}


    def __init__(self) -> None:
        if not self.update_patterns():
            regist_error("Communicator initializing error")

    
    def get_message(self, key : str) -> str:
        try:
            return self.messages_patterns[key]
        except KeyError:
            regist_error(
                error_description = f"Get message-pattern error: key '{key}' is not found",
                error_type = KeyError,
            )
            return "Ой, здесь должен быть текст сообщения... Ошибка уже исправляется!"


    def get_keyboard_title(self, key : str) -> str:
        try:
            return self.keyboards_patterns[key]
        except KeyError:
            regist_error(
                error_description = f"Get keyboard-pattern error: key '{key}' is not found",
                error_type = KeyError,
            )
            return "Ой, ошибка уже исправляется..."


    def update_patterns(self) -> bool:
        relations_list = MessagesPatternsDBClient().get_all_messages_patterns()
        if not relations_list:
            regist_error(
                error_description = f"Update messages_patterns error: relations db client returned not ok value: {relations_list}",
                error_type = ValueError,
            )
            return False

        self.messages_patterns = {}
        for key, message_pattern_text in relations_list:
            self.messages_patterns[key] = message_pattern_text
        
        relations_list = MessagesPatternsDBClient().get_all_keyboards_patterns()
        if not relations_list:
            regist_error(
                error_description = f"Update keyboards_patterns error: relations db client returned not ok value: {relations_list}",
                error_type = ValueError,
            )
            return False
        
        self.keyboards_patterns = {}
        for key, keyboard_pattern_text in relations_list:
            self.keyboards_patterns[key] = keyboard_pattern_text

        record_log("Request for communicator-content successfully operated!")
        return True
    

    def get_messages_content(self) -> dict:
        return self.messages_patterns


    def get_keyboards_content(self) -> dict:
        return self.keyboards_patterns
    

    def update_message_content(self, message_key : str, new_message_content : str) -> bool:
        return MessagesPatternsDBClient().update_message_pattern_text(message_key, new_message_content)
    
    
    def update_keyboard_content(self, keyboard_key : str, new_keyboard_content : str) -> bool:
        return MessagesPatternsDBClient().update_keyboard_pattern_text(keyboard_key, new_keyboard_content)
