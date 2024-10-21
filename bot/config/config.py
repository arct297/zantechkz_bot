"""Here will be documentation"""

from json import loads
from pathlib import Path

CONFIG_FILE_PATH = Path(__file__).parent / "config.json"


def _read_config_json() -> dict:
    """Here will be documentation"""

    with open(CONFIG_FILE_PATH, "r", encoding = "UTF-8") as config_file:
        return loads(config_file.read())


def get_bot_reporter_token() -> str:
    return _read_config_json().get("reporter_bot_token")


def get_report_chat_id() -> int:
    return _read_config_json().get("report_chat_id")


def get_dev_tg_id() -> int:
    return _read_config_json().get("dev_tg_id")