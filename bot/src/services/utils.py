from aiogram import types
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.core.paginator import Paginator
from django.db import connection

from admin_panel.app.models import TelegramUser, Category
from bot.src.config.settings import channel_name, group_name, bot, channel

NOT_SUB_MESSAGE = f"""
⚠️ Для доступа к боту подпишитесь на:
- Канал: <a href="https://t.me/{channel_name}">Наш канал</a>
- Группу: <a href="https://t.me/{group_name}">Наша группа</a>
После подписки нажмите **«Проверить подписку»**.
"""


class AddTaskState(StatesGroup):
    """Состояние ожидания."""
    waiting_for_task = State()


def check_sub_kb():
    """Кнопка проверить подписку."""

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="✅ Проверить подписку",
        callback_data="check_subscription")
    )
    return builder.as_markup()


async def is_subscribe(user_id: int):
    """Проверяет подписку пользователя на группу и канал."""

    try:
        channel_subscribe = await bot.get_chat_member(channel, user_id)
        # group_subscribe = await bot.get_chat_member(group, user_id)
        return channel_subscribe.status in ["member", "administrator", "creator"]
                # group_subscribe.status in ["member", "administrator", "creator"])
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False


@sync_to_async
def register_user(user_id: int):
    """Регистрирует пользователя."""

    connection.close()
    user, created = TelegramUser.objects.get_or_create(user_id=user_id)
    return created


# @sync_to_async
# def get_categories():
#     """Получаем все категории."""
#
#     connection.close()
#     return list(Category.objects.filter(is_active=True))


@sync_to_async
def get_categories_page(page: int = 1, per_page: int = 5):
    """Получение категорий с пагинацией."""

    connection.close()
    categories = Category.objects.filter(is_active=True).order_by('id')
    paginator = Paginator(categories, per_page)
    page_obj = paginator.get_page(page)

    return {
        'page_obj': page_obj,
        'object_list': list(page_obj.object_list.values('id', 'title'))
    }
