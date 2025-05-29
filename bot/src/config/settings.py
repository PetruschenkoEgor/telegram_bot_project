import logging
import os

import django
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from asyncpg_lite import DatabaseManager
from dotenv import load_dotenv
from yookassa import Configuration

# Указываем путь к settings.py Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin_panel.config.settings")
django.setup()

load_dotenv()


TELEGRAM_TOKEN = os.getenv("TOKEN")
# список администраторов из .env
admins = [int(admin_id) for admin_id in os.getenv("ADMINS").split(",")]

# канал и группа, на которые должен быть подписан пользователь
channel = os.getenv("CHANNEL_ID")
group = os.getenv("GROUP_ID")
channel_name = os.getenv("CHANNEL_NAME")
group_name = os.getenv("GROUP_NAME")

# настраиваем логирование и выводим в переменную для отдельного использования в нужных местах
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# инициируем объект, который будет отвечать за взаимодействие с базой данных
db_manager = DatabaseManager(db_url=os.getenv("PG_LINK"), deletion_password=os.getenv("ROOT_PASS"))

# бот по умолчанию будет считывать HTML теги с сообщений
bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

# Настройка ЮКассы
Configuration.account_id = os.getenv("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.getenv("YOOKASSA_SECRET_KEY")
