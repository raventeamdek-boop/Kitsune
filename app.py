from aiogram import executor
import asyncio
import sys
from loader import dp
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.db_api.create_db import*
from utils.db_api.baza import*

if sys.version_info >= (3, 10):
    asyncio.get_event_loop = asyncio.new_event_loop


async def on_startup(dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)

    # Уведомляет про запуск
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    create_db()
    admins_setting_info()
    executor.start_polling(dp, on_startup=on_startup)
from aiogram import executor
import asyncio
import sys
from loader import dp
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.db_api.create_db import*
from utils.db_api.baza import*

if sys.version_info >= (3, 10):
    asyncio.get_event_loop = asyncio.new_event_loop


async def on_startup(dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)

    # Уведомляет про запуск
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    create_db()
    admins_setting_info()
    executor.start_polling(dp, on_startup=on_startup)
