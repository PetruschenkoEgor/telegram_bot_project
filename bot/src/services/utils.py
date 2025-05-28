import asyncio
import os

import httpx

from aiogram import types
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import ClientConnectionError
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.paginator import Paginator
from django.db import connection

from admin_panel.app.models import TelegramUser, Category, Subcategory, Product, Cart, CartItem, Order
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
    user, _ = TelegramUser.objects.get_or_create(user_id=user_id)
    return user


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


@sync_to_async
def get_subcategories_page(category_id: int, page: int = 1, per_page: int = 5):
    """Получение подкатегорий с пагинацией."""

    connection.close()
    subcategories = Subcategory.objects.filter(
        is_active=True,
        category_id=category_id
    ).order_by('id')
    paginator = Paginator(subcategories, per_page)
    page_obj = paginator.get_page(page)

    return {
        'page_obj': page_obj,
        'object_list': list(page_obj.object_list.values('id', 'title'))
    }


@sync_to_async
def get_subcategory(subcategory_id: int):
    """Получение подкатегории"""

    connection.close()
    subcategory = Subcategory.objects.get(id=subcategory_id)

    return subcategory


@sync_to_async
def get_products_subcategory(subcategory_id: int):
    """Получение товаров с изображениями"""

    connection.close()
    products = Product.objects.filter(
        subcategory_id=subcategory_id,
        is_active=True
    )
    return list(products)


@sync_to_async
def get_or_create_cart(user_id: int):
    """Получить или создать корзину."""

    connection.close()
    user = TelegramUser.objects.get(user_id=user_id)
    cart, _ = Cart.objects.get_or_create(user=user)

    return cart


@sync_to_async
def get_or_create_cart_item(cart: Cart, product: Product, quantity: int):
    """Получить или создать содержимое корзины."""

    connection.close()
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
    if not created:
        cart_item.quantity = quantity
        cart_item.save()

    return cart_item


@sync_to_async
def get_product(product_id: int):
    """Получение товара."""

    connection.close()

    return Product.objects.get(id=product_id)


@sync_to_async
def get_user_telegram(user_id: int):
    """Получаем пользователя."""

    connection.close()

    return TelegramUser.objects.get(user_id=user_id)


@sync_to_async
def get_cart_items(cart: Cart):
    """Получить содержимое корзины."""

    connection.close()

    return list(CartItem.objects.filter(cart=cart))


@sync_to_async
def delete_product_cart_item(cart_item_id: int):
    """Удаление товара из содержимого корзины."""

    connection.close()

    cart_item = CartItem.objects.get(id=cart_item_id)
    cart_item.delete()


@sync_to_async
def delete_all_cart_item(cart_id: int):
    """Удалить все товары из корзины."""

    connection.close()
    cart = Cart.objects.get(id=cart_id)
    CartItem.objects.filter(cart=cart).delete()


@sync_to_async
def create_an_order(user_id: int, total_price: float):
    """Создать заказ."""

    connection.close()

    user = TelegramUser.objects.get(user_id=user_id)

    return Order.objects.create(user=user, status="Новый", total_price=total_price)
