import sys
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
admin_panel_path = BASE_DIR / 'admin_panel'
app_path = BASE_DIR / 'admin_panel' / 'app'

sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / 'admin_panel'))

from django_setup import setup_django
setup_django()

import asyncio

from aiogram.types import BotCommand, BotCommandScopeDefault

from bot.src.config.settings import bot, admins, dp
from bot.src.handlers.start import router


async def set_commands():
    """Настраивает командное меню(дефолтное для всех пользователей)."""

    commands = [
        BotCommand(command='start', description='Старт')
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def start_bot():
    """Выполнится когда бот запустится."""

    await set_commands()

    try:
        for admin_id in admins:
            await bot.send_message(admin_id, 'Я запущен!')
    except:
        pass


async def stop_bot():
    """Выполнится когда бот завершит свою работу."""

    try:
        for admin_id in admins:
            await bot.send_message(admin_id, 'Бот остановлен!')
    except:
        pass


async def main():
    # регистрация роутеров
    dp.include_router(router)

    # регистрация функций при старте и завершении работы бота
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    # запуск бота в режиме long polling при запуске бот очищает все обновления, которые были за его моменты бездействия
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    # setup_logger()
    asyncio.run(main())
