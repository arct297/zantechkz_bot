import asyncio
import logging

from aiogram import Dispatcher

from aiogram.fsm.storage.memory import MemoryStorage

from logger import record_log, regist_error

from vars import bot, DEV_ID

from bot_scripts import bot_subtasks


storage = MemoryStorage()
dp = Dispatcher(storage = storage)

# Routers including:
from bot_scripts import routers

for router in routers:
    try:
        dp.include_router(router)
    except Exception as error:
        regist_error(
            f"Unsuccessful including of router with name {router.name}, bot will be stopped",
            "router including error"
        )
        exit()


async def main() -> None:
    bot_me = await bot.get_me()
    await bot.send_message(
        DEV_ID, 
        f"Bot is launched!\n\n{bot_me}"
    )
    record_log("Bot is launched!", "main")
    
    _set_bot_tag(bot_me.username)
    record_log(f"Bot tag @{bot_me.username} was set", "main")

    record_log("Subtasks starting...", "main")
    bot_subtasks.start_subtasks()
    record_log("Subtasks have been started.", "main")

    await dp.start_polling(bot, skip_updates = False)


def _set_bot_tag(bot_tag : str):
    import vars
    vars.bot_tag = f"@{bot_tag}"


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot has been interrupted!")