import pytz

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import get_dev_tg_id

from communication import Communicator 

from database import BotDBClient

from token_ import TOKEN

UTC_TZ = pytz.utc

communicator = Communicator()
bot_db_client = BotDBClient()

DEV_ID = get_dev_tg_id()


bot = Bot(
    token = TOKEN, 
    default = DefaultBotProperties(
        parse_mode=ParseMode.HTML,
        link_preview_is_disabled = True
    )
)

bot_tag = None