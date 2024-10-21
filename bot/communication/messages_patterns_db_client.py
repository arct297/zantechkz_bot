"""Here will be documentation"""

import sqlite3 as sqlt
 
from pathlib import Path

from logger import record_log, regist_error


INSTANCES_RELATIONS_DB_PATH = Path(__file__).parent / "communication.db"


class MessagesPatternsDBClient:
    """Here will be documentation"""
    database_path : str

    def __init__(self) -> None: 
        self.database_path = INSTANCES_RELATIONS_DB_PATH   
        self.create_database()


    def create_database(self) -> bool:
        """
        Creates local database taking self.database_path
        """

        try:
            with sqlt.connect(self.database_path) as connection:
                cursor = connection.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages_patterns (
                        message_key TEXT PRIMARY KEY,
                        message_pattern_text TEXT NOT NULL
                    )"""
                )
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS keyboards_patterns (
                        keyboard_key TEXT PRIMARY KEY,
                        keyboard_pattern_text TEXT NOT NULL
                    )"""
                )
                connection.commit()
            return True
        except Exception as db_error:
            regist_error(
                error_description = f"Database creation error: {db_error}", 
                error_type = type(db_error), 
            )
            return False


    def add_message_pattern(self, key : str, message_pattern_text : str) -> bool | None:
        """
        Sets new "key-message_pattern_text" relation into database.
        """

        try:
            with sqlt.connect(self.database_path) as connection:
                cursor = connection.cursor()
                cursor.execute(f"INSERT INTO messages_patterns VALUES (?, ?)", (key, message_pattern_text))
                connection.commit()
            return True
        
        except sqlt.IntegrityError:
            return None
        
        except Exception as db_error:
            regist_error(
                error_description = f"Set new key-message_pattern_text relation error: {db_error}", 
                error_type = type(db_error), 
            )
            return False
        

    def update_message_pattern_text(self, key : str, new_message_pattern_content : str) -> bool:
        """
        Updates message pattern text setting new value to passed key

        Be shure about existing of key
        """
        try:
            with sqlt.connect(self.database_path) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE messages_patterns SET message_pattern_text = (?) WHERE message_key = (?)",
                    (new_message_pattern_content, key)
                )
                connection.commit()
            return True
        except Exception as db_error:
            regist_error(
                error_description = f"Update message_pattern_text for key '{key}' error: {db_error}", 
                error_type = type(db_error), 
            )
            return False
    

    def get_all_messages_patterns(self) -> list[tuple] | bool:
        """
        Returns all key-message_pattern_text relations in list [(key, message_pattern_text), ...]
        """
        try:
            with sqlt.connect(self.database_path) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT * FROM messages_patterns",
                )
                result : list[tuple] = cursor.fetchall()
                return result
                
        except Exception as db_error:
            regist_error(
                error_description = f"Get all relations error: {db_error}", 
                error_type = type(db_error), 
            )
            return False

    
    def add_keyboard_pattern(self, key : str, keyboard_pattern_text : str) -> bool | None:
        """
        Sets new "key-keyboard_pattern_text" relation into database.
        """

        try:
            with sqlt.connect(self.database_path) as connection:
                cursor = connection.cursor()
                cursor.execute(f"INSERT INTO keyboards_patterns VALUES (?, ?)", (key, keyboard_pattern_text))
                connection.commit()
            return True
        
        except sqlt.IntegrityError:
            return None
        
        except Exception as db_error:
            regist_error(
                error_description = f"Set new key-keyboard_pattern_text relation error: {db_error}", 
                error_type = type(db_error), 
            )
            return False
        

    def update_keyboard_pattern_text(self, key : str, new_keyboard_pattern_content : str) -> bool:
        """
        Updates keyboard pattern text setting new value to passed key

        Be shure about existing of key
        """
        try:
            with sqlt.connect(self.database_path) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE keyboards_patterns SET keyboard_pattern_text = (?) WHERE keyboard_key = (?)",
                    (new_keyboard_pattern_content, key)
                )
                connection.commit()
            return True
        except Exception as db_error:
            regist_error(
                error_description = f"Update keyboard_pattern_text for key '{key}' error: {db_error}", 
                error_type = type(db_error), 
            )
            return False
    

    def get_all_keyboards_patterns(self) -> list[tuple] | bool:
        """
        Returns all key-keyboard_pattern_text relations in list [(key, keyboard_pattern_text), ...]
        """
        try:
            with sqlt.connect(self.database_path) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT * FROM keyboards_patterns",
                )
                result : list[tuple] = cursor.fetchall()
                return result
                
        except Exception as db_error:
            regist_error(
                error_description = f"Get all relations error: {db_error}", 
                error_type = type(db_error), 
            )
            return False

