import json
import sqlite3 as sqlt
from pathlib import Path
from contextlib import contextmanager
from logger import record_log, regist_error

INSTANCES_RELATIONS_DB_PATH = Path(__file__).parent / "bot_database.db"

class BotDBClient:
    """Here will be documentation"""
    database_path: str


    def __init__(self) -> None:
        self.database_path = INSTANCES_RELATIONS_DB_PATH
        if self.initialize_database():
            record_log("Database client successfully registered")
        else:
            raise Exception("Database initializing error")


    @contextmanager
    def _get_connection(self):
        """
        Context manager for database connection with foreign keys enabled
        """
        connection = sqlt.connect(self.database_path)
        connection.row_factory = sqlt.Row 
        try:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            yield cursor
            connection.commit()
        except Exception as db_error:
            connection.rollback()
            # regist_error(
            #     error_description = f"Database error: {db_error}",
            #     error_type = type(db_error),
            #     raised_by = "MAY BE IGNORED: BotDatabaseClient CONNECTION",
            #     silent_mode = True,
            # )
            raise
        finally:
            connection.close()


    def initialize_database(self) -> bool:
        """
        Initializes local database taking self.database_path. Creates all tables (creates only it does not exist)
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_tg_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT
                    )"""
                )
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS bot_admins (
                        user_tg_id INTEGER PRIMARY KEY,
                        FOREIGN KEY (user_tg_id) REFERENCES users(user_tg_id)
                    )"""
                )
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS companies (
                        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_name TEXT
                    )"""
                )
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS companies_settings (
                        company_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        redirect_chat_id TEXT,
                        working_time_start VARCHAR(5),
                        working_time_end VARCHAR(5),
                        message_response_timeout INTEGER,
                        weekend TEXT,
                        settings TEXT,                        
                        FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
                    )"""
                )
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chats (
                        chat_tg_id INTEGER PRIMARY KEY,
                        chat_title TEXT,
                        company_id INTEGER,
                        chat_type TEXT,
                        FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
                    )"""
                )
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS owners (
                        user_tg_id INTEGER,
                        company_id INTEGER,
                        PRIMARY KEY (user_tg_id, company_id),
                        FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
                        FOREIGN KEY (user_tg_id) REFERENCES users(user_tg_id)
                    )"""
                )
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS managers (
                        user_tg_id INTEGER,
                        company_id INTEGER,
                        extra_name TEXT,
                        PRIMARY KEY (user_tg_id, company_id),
                        FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
                        FOREIGN KEY (user_tg_id) REFERENCES users(user_tg_id)
                    )"""
                )
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks_counter (
                        company_id INTEGER PRIMARY KEY,
                        task_number INTEGER,
                        FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
                    )"""
                )
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ewords (
                        eword_content TEXT,
                        company_id INTEGER,
                        PRIMARY KEY (eword_content, company_id),
                        FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
                    )"""
                )
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS chats_limits (
                        chat_tg_id INTEGER PRIMARY KEY,
                        is_rest_message_registered INTEGER,
                        time_limit INTEGER,
                        message_link TEXT,
                        last_message_id INTEGER,
                        was_first_message INTEGER,
                        FOREIGN KEY (chat_tg_id) REFERENCES chats(chat_tg_id) ON DELETE CASCADE
                    )"""
                )
            return True
        except Exception as db_error:
            regist_error(
                error_description = f"Database creation error: {db_error}",
                error_type = type(db_error),
            )
            return False


    def register_user(self, user_id : int, username : str = None, first_name : str = None, last_name : str = None) -> bool:
        """
        Registers user in bot database. If user is already registered, then updates user's data.

        Parameters:
        -----
        user_id : int
            user ID in Telegram
        username : str
            user tag in Telegram - WITHOUT "@" CHARACTER!
        first_name : str
            optional
        last_name : str
            optional

        Returns:
        --------
        bool:
            True, if success. False, if error.
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (user_id, username, first_name, last_name))
            return True

        except sqlt.IntegrityError:
            return self.update_user(user_id = user_id, username=username, first_name = first_name, last_name = last_name)

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
                silent_mode = True
            )
            return False


    def update_user(self, user_id : int, username : str = None, first_name : str = None, last_name : str = None) -> bool:
        """
        Updates user in bot database, be sure about user existing in database.

        Parameters:
        -----
        user_id : int
            user ID in Telegram
        username : str
            user tag in Telegram - WITHOUT "@" CHARACTER!
        first_name : str
            optional
        last_name : str
            optional

        Returns:
        --------
        bool:
            False, if error, otherwise, True.
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute(
                    "UPDATE users SET username = ?, first_name = ?, last_name = ? WHERE user_tg_id = ?",
                    (username, first_name, last_name, user_id)
                )
            return True

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
                silent_mode = True
            )
            return False


    def get_users_list(self, only_ids : bool = False) -> list[tuple] | list[int] | list:
        """
        Returns list of users from table "users".
        
        Can return only list of users' IDs. If error is happened during data retrieving, 
        then empty list will be returned and developer will be notified about error.

        Parameters:
        -----
        only_ids : bool
            flag for returning only list of IDs

        Returns:
        --------
        list:
            empty list, if error. If only ids is True, then list[int], if not, then list[tuple]
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute(
                    f"""SELECT {"user_tg_id" if only_ids else "*"} FROM users""",
                )
                result = cursor.fetchall()
            return [user["user_tg_id"] for user in result] if only_ids else [dict(user) for user in result]

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return []
        
    
    def get_user_info(self, user_id : int) -> dict | None:
        """
        Returns information about concrete user from table "users".
        
        Can return None in case of error or case in which user is not in database.

        Parameters:
        -----
        user_id : int
            user ID in Telegram

        Returns:
        --------
        dict:
            information about user
        None:
            error or user with such ID is not in database
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute(
                    f"""SELECT * FROM users WHERE user_tg_id = (?)""",
                    (user_id,)
                )
                user = cursor.fetchone()
            return dict(user) if user else None

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return None    


    def register_company(
            self, 
            company_name : str, 
            redirect_chat_id : int,
            working_time_start : str,
            working_time_end : str,
            message_response_timeout : int,
            weekend : list[int],
            settings : dict,
        ) -> bool:
        """
        Registers new company in bot database.

        Parameters:
        -----
        company_name : str
            name of company, must be unique
        redirect_chat_id : int
            chat in which messages about delay will be sent 
        working_time_start : str 
            when bot starts consider delay. Format: "HH:MM" Example of value "10:33" (at most 5 characters)
        working_time_end : str
            when bot stops consider delay. Format: "HH:MM" Example of value "19:33" (at most 5 characters)
        message_response_timeout : int 
            time to answer for manager (in seconds)
        weekend : list[int] 
            list with days when bot does not consider delay. Values from 0 to 6, where 0 is monday and 6 is sunday.
        settings : dict 
            dictionary with extra settings.

        Returns:
        --------
        bool:
            True, if success. False, if error or company with passed name already exists.
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute("INSERT INTO companies (company_name) VALUES (?)", (company_name,))
                company_id = cursor.lastrowid

                cursor.execute(
                    "INSERT INTO companies_settings VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        company_id, 
                        redirect_chat_id,
                        working_time_start,
                        working_time_end,
                        message_response_timeout,
                        _convert_to_json(weekend),
                        _convert_to_json(settings),
                    )
                )
                cursor.execute("INSERT INTO tasks_counter (company_id, task_number) VALUES (?, ?)", (company_id, 0))
            return True

        except sqlt.IntegrityError:
            regist_error(f"""Company with name "{company_name}" already exists.""", "constraint error")
            return False

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
                silent_mode = True
            )
            return False


    def get_companies_list(self) -> dict[int, dict[str, (str | int)]]:
        """
        Returns dictionary `{integer_company_id : {"value1_name" : value1, ...}, ...}` for each company.

        Returns:
        --------
        dict[int, dict[str, (str | int)]]:
            List with dictionaries for each company.
        dict (empty dict)     
            In case of error or 0 companies exist
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute(
                    f"""
                    SELECT * FROM companies AS co 
                    INNER JOIN companies_settings AS cs ON co.company_id = cs.company_id
                    """,
                )
                companies_rows = cursor.fetchall()
            
            json_fields = ("weekend", "settings")

            companies_data = {}
            company : dict
            for company in companies_rows:
                company = dict(company)
                company_id = company.get("company_id")
                company.pop("company_id")

                for field_name in json_fields:
                    company[field_name] = _load_from_json(company[field_name]) 

                companies_data[company_id] = company
            return companies_data

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return {}


    def delete_company(self, company_id : int) -> bool:
        """
        Deletes company with passed ID, if it exists.

        PAY ATTENTION:
        COMPANY DELETING LEADS TO DELETING ANYTHING CONNECTED WITH THIS COMPANY!!!

        Parameters:
        -----
        company_id : int
            company id

        Returns:
        --------
        bool:
            True, if success. False, if error.
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute("DELETE FROM companies WHERE company_id = ?", (company_id,))
            return True

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
                silent_mode = True
            )
            return False


    def register_owner(self, user_id : int, owner_company_id : int) -> bool:
        """
        Registers new owner in bot database.

        Parameters:
        -----
        user_id : int
            user's Telegram ID
        owner_company_id : int
            integer ID of owner's company

        Returns:
        --------
        bool:
            True, if success. False, if error or owner with passed ID already exists.
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute("INSERT INTO owners VALUES (?, ?)", (user_id, owner_company_id))
            return True

        except sqlt.IntegrityError:
            regist_error(f"""Owner with Telegram ID "{user_id}" already exists OR another constraint is FAILED""", "constraint error")
            return False

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
                silent_mode = True
            )
            return False


    def delete_owner(self, user_id : int) -> bool:
        """
        Deletes owner with passed ID, if it exists.

        Parameters:
        -----
        user_id : int
            user's Telegram ID

        Returns:
        --------
        bool:
            True, if success. False, if error.
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute("DELETE FROM owners WHERE user_tg_id = ?", (user_id,))
            return True

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
                silent_mode = True
            )
            return False
        

    def get_owners_list(self, only_ids : bool = False) -> list[tuple] | list[int] | list:
        """
        Returns list of owners from table "owners".
        
        Can return only list of users' IDs. If error is happened during data retrieving, 
        then empty list will be returned and developer will be notified about error.

        Parameters:
        -----
        only_ids : bool
            flag for returning only list of IDs

        Returns:
        --------
        list:
            empty list, if error. If only ids is True, then list[int], if not, then list[tuple]
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute(
                    f"""SELECT {"user_tg_id" if only_ids else "*"} FROM owners""",
                )
                result = cursor.fetchall()
            return [user["user_tg_id"] for user in result] if only_ids else [dict(user) for user in result]

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return []
        
    
    def get_owner_info(self, user_id : int) -> dict | None:
        """
        Returns information about concrete owner from table "owners".
        
        Can return None in case of error or case in which user is not in database.

        Parameters:
        -----
        user_id : int
            owner ID in Telegram

        Returns:
        --------
        dict:
            information about owner
        None:
            error or owner with such ID is not in database
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute(
                    f"""SELECT * FROM owners WHERE user_tg_id = (?)""",
                    (user_id,)
                )
                user = cursor.fetchone()
            return dict(user) if user else None

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return None 
    

    def register_bot_admin(self, user_id : int) -> bool:
        """
        Registers new BOT-admin in bot database.

        Parameters:
        -----
        user_id : int
            user's Telegram ID
        Returns:
        --------
        bool:
            True, if success. False, if error or bot-admin with passed ID already exists.
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute("INSERT INTO bot_admins VALUES (?)", (user_id,))
            return True

        except sqlt.IntegrityError:
            regist_error(f"""Bot-admin with Telegram ID "{user_id}" already exists or another constraint is FAILED""", "constraint error")
            return False

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
                silent_mode = True
            )
            return False
    

    def delete_bot_admin(self, user_id : int) -> bool:
        """
        Deletes bot-admin with passed ID, if it exists.

        Be sure about existing of user with such ID in "bot_admins" table.

        Parameters:
        -----
        user_id : int
            user's ID in Telegram

        Returns:
        --------
        bool:
            True, if success. False, if error.
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute("DELETE FROM bot_admins WHERE user_tg_id = ?", (user_id,))
            return True

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
                silent_mode = True
            )
            return False


    def get_bot_admins_list(self) -> list[int] | list:
        """
        Returns list of bot-admins from table "bot_admins".
        
        If error is happened during data retrieving, 
        then empty list will be returned and developer will be notified about error.

        Returns:
        --------
        list:
            empty list, if error. If success, then list[int].
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute(
                    f"""SELECT * FROM bot_admins""",
                )
                result = cursor.fetchall()
            return [user["user_tg_id"] for user in result]

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return []
        
    
    def register_manager(self, user_id : int, manager_company_id : int = None, owner_id : int = None, extra_name : str = None) -> bool:
        """
        Registers new manager for passed company in bot database.

        Parameters:
        -----
        user_id : int
            user's Telegram ID
        manager_company_id : int
            integer ID of manager's company

        Returns:
        --------
        bool:
            True, if success. False, if error or manager with passed ID already exists.
        """
        try:
            if not manager_company_id and not owner_id:
                raise ValueError("0 required argument was passed")
            with self._get_connection() as cursor:
                if manager_company_id:
                    cursor.execute("INSERT INTO managers VALUES (?, ?, ?)", (user_id, manager_company_id, extra_name))
                else:
                    cursor.execute("INSERT INTO managers VALUES (?, (SELECT company_id FROM owners WHERE user_tg_id = (?) LIMIT 1), ?)", (user_id, owner_id, extra_name))
            return True

        except sqlt.IntegrityError:
            regist_error(f"""Manager with Telegram ID "{user_id}" already exists OR another constraint is FAILED""", "constraint error")
            return False

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
                silent_mode = True
            )
            return False


    def delete_manager(self, user_id : int, owner_id : int) -> bool:
        """
        Deletes manager with passed ID, if it exists in owner's company.

        Parameters:
        -----
        user_id : int
            manager-user's Telegram ID
        owner_id : int
            owner-user's Telegram ID

        Returns:
        --------
        bool:
            True, if success. False, if error.
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute("DELETE FROM managers WHERE user_tg_id = ? AND company_id = (SELECT company_id FROM owners WHERE user_tg_id = (?))", (user_id, owner_id))
            return True

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
                silent_mode = True
            )
            return False
    
    
    def get_managers_list(self, only_ids : bool = False) -> list[tuple] | list[int] | list:
        """
        Returns list of managers from table "managers".
        
        Can return only list of users' IDs. If error is happened during data retrieving, 
        then empty list will be returned and developer will be notified about error.

        Parameters:
        -----
        only_ids : bool
            flag for returning only list of IDs

        Returns:
        --------
        list:
            empty list, if error. If only ids is True, then list[int], if not, then list[tuple]
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute(
                    f"""SELECT {"user_tg_id" if only_ids else "*"} FROM managers""",
                )
                result = cursor.fetchall()
            return [user["user_tg_id"] for user in result] if only_ids else [dict(user) for user in result]

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return []
        

    
    # def get_managers_list_of_company(self, company_id : int) -> list[int] | list:
    #     """
    #     Returns list of managers from table "managers".
        
    #     If error is happened during data retrieving, 
    #     then empty list will be returned and developer will be notified about error.

    #     Parameters:
    #     -----
    #     company_id : int
    #         company ID for which is needed to return list of managers

    #     Returns:
    #     --------
    #     list:
    #         empty list, if error or company with such ID does not exist. If success, then list[int] with IDs.
    #     """
    #     try:
    #         with self._get_connection() as cursor:
    #             cursor.execute(
    #                 f"""SELECT user_tg_id FROM managers WHERE company_id = (?)""",
    #                 (company_id,)
    #             )
    #             result = cursor.fetchall()
    #         return [user["user_tg_id"] for user in result]

    #     except Exception as db_error:
    #         regist_error(
    #             error_description = f"Database error: {db_error}",
    #             error_type = type(db_error),
    #         )
    #         return []
        
    
    def get_manager_info(self, user_id : int = None, username : str = None) -> dict | None:
        """
        Returns information about concrete manager from table "managers" by user_id or username.
        
        Can return None in case of error, in case when at least one required parameter is not passed, in case in which user is not in database.

        Parameters:
        ----------
        [Required at least one]
        user_id : int
            manager ID in Telegram
        username : str
            user tag in Telegram (without "@")

        Returns:
        --------
        dict:
            information about manager
        None:
            error or manager with such ID is not in database
        """
        try:
            with self._get_connection() as cursor:
                if user_id:
                    cursor.execute(
                        f"""
                        SELECT * FROM managers AS m 
                        INNER JOIN users AS u ON u.user_tg_id = m.user_tg_id
                        WHERE u.user_tg_id = (?)
                        """,
                        (user_id,)
                    )
                elif username:
                    cursor.execute(
                        f"""
                        SELECT * FROM managers AS m 
                        INNER JOIN users AS u ON u.user_tg_id = m.user_tg_id
                        WHERE LOWER(u.username) = (?)
                        """,
                        (username,)
                    )
                else:
                    raise ValueError()
               
                user = cursor.fetchone()
            return dict(user) if user else None

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return None 
        
    
    def get_managers_list_of_owner(self, user_id : int, only_ids : bool = False) -> list[dict] | list[int] | list:
        """
        Returns information about all managers of owner's company from table "managers".
        
        Can return empty list [] in case of error or case in which owner has not managers.

        Parameters:
        -----
        user_id : int
            owner ID in Telegram
        only_ids : bool
            if flag is True, then list[int] with manager IDs will be returned. 
            If flag is False, then list[dict] will be returned, where key of dict are collumn names.  

        Returns:
        --------
        list[dict]:
            list of managers with full information about manager
        list (empty list []):
            error or owner with passed ID has not managers in company
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute(
                    f"""
                    SELECT {"m.user_tg_id" if only_ids else "*"} FROM managers AS m 
                    INNER JOIN owners AS o ON o.company_id = m.company_id
                    INNER JOIN users AS u ON u.user_tg_id = m.user_tg_id
                    WHERE o.user_tg_id = (?)
                    """,
                    (user_id,)
                )
                users = cursor.fetchall()
            return [user[0] for user in users] if only_ids else [dict(user) for user in users]

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return []


    def add_ewords(self, ewords_list : list[str], user_id : int):
        """
        Adds ewords into ewords to company of passed manager.

        !!! ATTENTION: USER MUST BE MANAGER !!!
         
        Parameters:
        -----
        ewords_list : list[str]
            list with ewords to add
        user_id : int
            manager ID in Telegram

        Returns:
        --------
        bool:
            result of implementation
        """

        try:
            with self._get_connection() as cursor:
                result = cursor.execute(
                    f"""
                    SELECT company_id FROM managers WHERE user_tg_id = (?)
                    """,
                    (user_id,)
                )
                company_id = result.fetchone()
                if company_id:
                    company_id = company_id["company_id"]
                else:
                    return False

                for eword in ewords_list:
                    cursor.execute(
                        f"""
                        INSERT INTO ewords VALUES (?, ?)
                        """,
                        (eword, company_id,)
                    )
            return True
        
        except sqlt.IntegrityError:
            return None

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return False 
    

    def delete_ewords(self, ewords_list : list[str], user_id : int):
        """
        Deletes all ewords from list from database by company of passed manager's.

        !!! ATTENTION: USER MUST BE MANAGER !!!
         
        Parameters:
        -----
        ewords_list : list[str]
            list of ewords to deleting
        user_id : int
            manager ID in Telegram

        Returns:
        --------
        bool:
            result of implementation
        """

        try:
            with self._get_connection() as cursor:
                result = cursor.execute(
                    f"""
                    SELECT company_id FROM managers WHERE user_tg_id = (?)
                    """,
                    (user_id,)
                )
                company_id = result.fetchone()
                if company_id:
                    company_id = company_id["company_id"]
                else:
                    return False

                for eword_content in ewords_list:
                    cursor.execute(
                        f"""
                        DELETE FROM ewords
                        WHERE company_id = (?) AND eword_content = (?)
                        """,
                        (company_id, eword_content,)
                    )
            return True

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return False 

    
    def get_ewords_list_of_company(self, company_id : int) -> list[str] | list:
        """
        Returns list of ewords (exception-words) of passed company.
        
        Using sql join retrieve ewords list of concrete company.

        Parameters:
        -----
        company_id : int

        Returns:
        --------
        list[str]:
            list of ewords
        list (empty list []):
            happens in case of: 1) error; 2) ewords list for this company is empty;
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute(
                    f"""
                    SELECT eword_content FROM ewords
                    WHERE company_id = (?)
                    """,
                    (company_id,)
                )
                ewords = cursor.fetchall()
            return [eword[0] for eword in ewords]

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return [] 


    def get_ewords_list_by_manager_id(self, user_id : int) -> list[str] | list:
        """
        Returns list of ewords (exception-words) of manager's company.
        
        Using sql join retrieve ewords list of concrete company.

        Parameters:
        -----
        user_id : int
            manager ID in Telegram

        Returns:
        --------
        list[str]:
            list of ewords
        list (empty list []):
            happens in case of: 1) error; 2) ewords list for this company is empty; 3) user is not in managers;
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute(
                    f"""
                    SELECT eword_content FROM ewords AS e 
                    INNER JOIN managers AS m ON e.company_id = m.company_id
                    WHERE m.user_tg_id = (?)
                    """,
                    (user_id,)
                )
                ewords = cursor.fetchall()
            return [eword[0] for eword in ewords]

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return [] 
        

    def get_registered_chats(self) -> list[int] | list:
        """
        Returns list of registered chats (only chats' IDs).
        
        Returns:
        --------
        list[int]:
            list of chats' ids
        list (empty list []):
            happens in case of: 1) error; 2) 0 chats are registered.
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute(
                    f"""
                    SELECT chat_tg_id FROM chats
                    """,
                )
                chats = cursor.fetchall()
            return [chat[0] for chat in chats]

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return [] 
        
    
    def register_chat(self, chat_id : int, chat_title : str, manager_id : int, chat_type : str = "customer") -> bool:
        """
        Registers chat in bot database.

        Parameters:
        -----
        chat_id : int
            chat ID in Telegram
        chat_title : str
            title of chat
        manager_id : str
            manager Telegram ID who is registering chat
        chat_type : str
            type of chat ("customer" chat or "command" chat) 

        Returns:
        --------
        bool:
            True, if success. False, if error.
        None:
            chat is already registered or some constraint is failed
        """
        try:
            with self._get_connection() as cursor:
                result = cursor.execute(
                    f"""
                    SELECT company_id FROM managers WHERE user_tg_id = (?)
                    """,
                    (manager_id,)
                )
                company_id = result.fetchone()
                if company_id:
                    company_id = company_id["company_id"]
                else:
                    raise ValueError(f"Manager {manager_id} is unregistered as a manager.")
                cursor.execute("INSERT INTO chats (chat_tg_id, chat_title, company_id, chat_type) VALUES (?, ?, ?, ?)", (chat_id, chat_title, company_id, chat_type))
                cursor.execute("INSERT INTO chats_limits (chat_tg_id, is_rest_message_registered, time_limit, message_link, last_message_id) VALUES (?, ?, ?, ?, ?)", (chat_id, None, None, None, None))
            return True

        except sqlt.IntegrityError:
            return self.update_chat(chat_id, chat_title, chat_type)

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
                silent_mode = True
            )
            return False


    def update_chat(self, chat_id : int, chat_title : str = None, chat_type : str = None) -> bool:
        """
        Updates chat in bot database.

        !!! ATTENTION: UNSECURED: access to chat is unchecked, be sure about matching of manager's and chat's company.

        Updates chat's info like chat title or chat type. Be sure, that at least one parameter to update is passed to method.

        Parameters:
        -----
        chat_id : int
            chat ID in Telegram
        chat_title : str [Optional]
            title of chat
        chat_type : str [Optional]
            type of chat ("customer" chat or "command" chat) 

        Returns:
        --------
        bool:
            True, if success. False, if error.
        None:
            if at least one parameter was not passed.
        """
        try:
            if (not chat_title) and (not chat_type):
                return None

            with self._get_connection() as cursor:
                if chat_title:
                    cursor.execute("UPDATE chats SET chat_title = (?) WHERE chat_tg_id = (?)", (chat_title, chat_id,))
                if chat_type:
                    cursor.execute("UPDATE chats SET chat_type = (?) WHERE chat_tg_id = (?)", (chat_type, chat_id,))
            return True

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
                silent_mode = True
            )
            return False


    def delete_chat(self, chat_id : int) -> bool:
        """
        Deletes chat with passed ID, if it exists.

        Parameters:
        -----
        chat_id : int
            chat's Telegram ID

        Returns:
        --------
        bool:
            True, if success. False, if error.
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute("DELETE FROM chats WHERE chat_tg_id = ?", (chat_id,))
            return True

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
                silent_mode = True
            )
            return False


    def get_manger_chats(self, user_id : int) -> list | list[int]:
        """
        Returns list of registered chats for company of concrete manager (only chats' IDs).
        
        Parameters:
        -----------
        user_id : int
            manager user ID in Telegram

        Returns:
        --------
        list[int]:
            list of chats' ids
        list (empty list []):
            happens in case of: 1) error; 2) 0 chats are registered for passed manager.
        """
        try:
            with self._get_connection() as cursor:
                company_retrieving_result = cursor.execute(
                    """SELECT company_id FROM managers WHERE user_tg_id = (?)""",
                    (user_id,)
                )
                company_row = company_retrieving_result.fetchone()
                if not company_row:
                    return []
                company_id = company_row[0]

                cursor.execute(
                    """
                    SELECT chat_tg_id FROM chats
                    WHERE company_id = (?)
                    """,
                    (company_id,)
                )
                chats = cursor.fetchall()
            return [chat[0] for chat in chats]

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return [] 
        

    def get_chat_info(self, chat_id : int) -> dict | None | bool:
        """
        Returns info about concrete chat from two tables, including information about delay.
        
        Parameters:
        -----------
        chat_id : int
            chat ID in Telegram

        Returns:
        --------
        dict:
            info about chat
        None:
            chat with passed ID is not registered
        bool:
            can be only False. Happens in case of error
        """
        try:
            with self._get_connection() as cursor:
                chat_row = cursor.execute("""
                    SELECT * FROM chats AS c
                    INNER JOIN chats_limits AS cl ON c.chat_tg_id = cl.chat_tg_id
                    WHERE c.chat_tg_id = (?)
                    """,
                    (chat_id,)   
                )
                chat_info = chat_row.fetchone()
                if not chat_info:
                    return None    
                return dict(chat_info)
            
        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return False
        
    
    def update_chat_limits(self, chat_id : int, **kwargs) -> bool:
        """
        Updates chat limits in bot database.

        !!! ATTENTION: UNSECURED: access to chat is unchecked, be sure about matching of manager's and chat's company.

        Updates chat limits' info to passed field (check parameters). Be shure about existing of chat.

        Parameters:
        -----
        chat_id : int
            chat ID in Telegram
        **kwargs
            new values of limits. May include:
                is_rest_message_registered : bool
                time_limit : str (unix time) | None
                message_link : str | None
                last_message_id : int
                was_first_message : bool        
        Returns:
        --------
        bool:
            True, if success. False, if error.
        """
        try:
            with self._get_connection() as cursor:
                for key in kwargs:
                    cursor.execute(f"UPDATE chats_limits SET {key} = (?) WHERE chat_tg_id = (?)", (kwargs.get(key), chat_id,))
            return True

        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
                silent_mode = True
            )
            return False


    def get_full_chats_list(self) -> list[dict] | list:
        """
        Returns info about all chats from two tables, including information about limit.
        
        Returns:
        --------
        list[dict]:
            list of chats with information for each chat
        list:
            no registered chats or some error was happened 
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute("""
                    SELECT * FROM chats AS c
                    INNER JOIN chats_limits AS cl ON c.chat_tg_id = cl.chat_tg_id
                    """,
                )
                chats_rows = cursor.fetchall()
                return [dict(chat) for chat in chats_rows]
            
        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return False
        
    
    def get_last_task_id(self, company_id : int) -> int | None:
        """
        Returns INTEGER value of last task ID.
        
        Parameters:
        -----------
        company_id : int

        Returns:
        --------
        int:
            last task ID.
        None:
            company is not registered or some error was happened 
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute("""
                    SELECT task_number FROM tasks_counter
                    WHERE company_id = (?)
                    """,
                    (company_id,)
                )
                last_task_id_row = cursor.fetchone()
                if not last_task_id_row:
                    return None
                return last_task_id_row[0]
            
        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return None


    def increase_last_task_id(self, company_id : int) -> bool:
        """
        Increases task number for passed company.
        
        Parameters:
        -----------
        company_id : int

        Returns:
        --------
        bool:
            result of implementation 
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute("""
                    UPDATE tasks_counter SET task_number = task_number + 1
                    WHERE company_id = (?)
                    """,
                    (company_id,)
                )
                last_task_id_row = cursor.fetchone()
                if not last_task_id_row:
                    return None
                return last_task_id_row[0]
            
        except Exception as db_error:
            regist_error(
                error_description = f"Database error: {db_error}",
                error_type = type(db_error),
            )
            return None




def _convert_to_json(data : dict | None) -> str | None:
    if data is None:
        return None
    try:
        return json.dumps(data)
    except Exception as converting_error:
        regist_error(
            error_description = f"Converting data to json error: {converting_error}. Passed data: {data}",
            error_type = type(converting_error),    
        )
        return None


def _load_from_json(data : str | None) -> dict | list:
    if data is None:
        return None
    try:
        return json.loads(data)
    except Exception as loading_error:
        regist_error(
            error_description = f"Loading json data error: {loading_error}. Passed data: {data}",
            error_type = type(loading_error),    
        )
        return None