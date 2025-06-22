import base64
import datetime
import os
import time
import uuid
from typing import Optional

import aiohttp
import requests
from aiogram import types
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.core.paginator import Paginator
from django.db import connection

from admin_panel.app.models import Cart, CartItem, Category, Delivery, Order, Product, Subcategory, TelegramUser
from bot.src.config.settings import bot, channel, channel_name, group_name, GIGACHAT_CLIENT_ID, GIGACHAT_CLIENT_SECRET
from bot.src.middlewares.logging_logs import logger

NOT_SUB_MESSAGE = f"""
⚠️ Для доступа к боту подпишитесь на:
- Канал: <a href="https://t.me/{channel_name}">Наш канал</a>
- Группу: <a href="https://t.me/{group_name}">Наша группа</a>
После подписки нажмите **«Проверить подписку»**.
"""

FAQ = {
    "доставка": "Доставка осуществляется в течение 2-3 рабочих дней.",
    "оплата": "Мы принимаем карты, электронные кошельки и наличные при самовывозе.",
    "возврат": "Возврат возможен в течение 14 дней с момента покупки.",
    "гарантия": "Гарантия на все товары составляет 1 год.",
    "контакты": "Наши контакты: +7 (123) 456-78-90, email@example.com",
}

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL")


class AddTaskState(StatesGroup):
    """Состояние ожидания."""

    waiting_for_task = State()


def check_sub_kb():
    """Кнопка проверить подписку."""

    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="✅ Проверить подписку", callback_data="check_subscription"))
    return builder.as_markup()


async def is_subscribe(user_id: int):
    """Проверяет подписку пользователя на группу и канал."""

    try:
        channel_subscribe = await bot.get_chat_member(channel, user_id)
        # group_subscribe = await bot.get_chat_member(group, user_id)
        return channel_subscribe.status in ["member", "administrator", "creator"]
        # group_subscribe.status in ["member", "administrator", "creator"])
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
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
    categories = Category.objects.filter(is_active=True).order_by("id")
    paginator = Paginator(categories, per_page)
    page_obj = paginator.get_page(page)

    return {"page_obj": page_obj, "object_list": list(page_obj.object_list.values("id", "title"))}


@sync_to_async
def get_subcategories_page(category_id: int, page: int = 1, per_page: int = 5):
    """Получение подкатегорий с пагинацией."""

    connection.close()
    subcategories = Subcategory.objects.filter(is_active=True, category_id=category_id).order_by("id")
    paginator = Paginator(subcategories, per_page)
    page_obj = paginator.get_page(page)

    return {"page_obj": page_obj, "object_list": list(page_obj.object_list.values("id", "title"))}


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
    products = Product.objects.filter(subcategory_id=subcategory_id, is_active=True)
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
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": quantity})
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

    return Order.objects.create(user=user, status="new", total_price=total_price)


@sync_to_async
def save_order_delivery(order_id: int, address: str, phone: str, comment: str, delivery_date: datetime):
    """Сохранение доставки."""

    connection.close()

    order = Order.objects.get(id=order_id)

    return Delivery.objects.create(
        order=order, address=address, phone=phone, comment=comment, delivery_date=delivery_date
    )


@sync_to_async
def update_order_status(order_id: int, status: str):
    """Обновление статуса заказа."""

    connection.close()

    order = Order.objects.get(id=order_id)
    order.status = status
    order.save()

    return order


@sync_to_async
def get_cart_items_for_user(user_id: int):
    """Получить содержимое корзины по ид пользователя."""

    connection.close()

    user = TelegramUser.objects.get(user_id=user_id)
    items = list(CartItem.objects.filter(cart__user=user).select_related("product"))

    result = {
        "items": (
            [
                {
                    "product_id": item.product.id,
                    "title": item.product.title,
                    "price": item.product.price,
                    "quantity": item.quantity,
                }
                for item in items
            ]
            if items
            else []
        )
    }

    return result


@sync_to_async
def update_product(cart_items: list):
    """Обновляем количество товаров на остатке."""

    connection.close()

    for product in cart_items.get("items"):
        prod = Product.objects.get(id=product.get("product_id"))
        prod.stock -= product.get("quantity")
        prod.save()


@sync_to_async
def delete_cart_item(user_id: int):
    """Удаляем содержимое корзины по ид пользователя."""

    user = TelegramUser.objects.get(user_id=user_id)
    cart = Cart.objects.get(user=user)
    CartItem.objects.filter(cart=cart).delete()


@sync_to_async
def update_order_status_payment(order_id: int):
    """Обновление статуса оплаты заказа."""

    order = Order.objects.get(id=order_id)
    order.status_payment = "paid"
    order.save()


@sync_to_async
def get_order_status_payment(order_id: int):
    """Получение статуса оплаты заказа."""

    order = Order.objects.get(id=order_id)

    return order.status_payment


async def call_deepseek_api(prompt: str, message_id: int = None) -> str:
    """Callback-функция для запроса к DeepSeek API"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 2000
    }

    if message_id:
        payload["message_id"] = str(message_id)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(DEEPSEEK_API_URL, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                error = await response.text()
                logger.error(f"DeepSeek API error: {error}")
                return "⚠️ Произошла ошибка API. Пожалуйста, попробуйте позже."
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка соединения: {e}")
        return "⚠️ Проблемы с соединением. Пожалуйста, попробуйте позже."
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        return "⚠️ Произошла непредвиденная ошибка."


class GigaChatAPI:
    def __init__(self):
        self.client_id = os.getenv('GIGACHAT_CLIENT_ID')
        self.client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')
        self.access_token = None
        self.token_expires = 0
        self.verify_ssl = False  # В продакшене должно быть True

        if not self.client_id or not self.client_secret:
            raise ValueError("GIGACHAT_CLIENT_ID и GIGACHAT_CLIENT_SECRET должны быть установлены в .env")

    def _get_auth_header(self) -> str:
        """Формирование Basic Auth заголовка"""
        auth_str = f"{self.client_id}:{self.client_secret}"
        return base64.b64encode(auth_str.encode()).decode()

    async def _get_access_token(self) -> str:
        """Получение нового токена доступа"""
        try:
            auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': str(uuid.uuid4()),
                'Authorization': f'Basic {self._get_auth_header()}',
            }

            data = {'scope': 'GIGACHAT_API_PERS'}

            response = requests.post(
                auth_url,
                headers=headers,
                data=data
            )

            response.raise_for_status()
            token_data = response.json()

            self.access_token = token_data.get('access_token')
            if not self.access_token:
                raise ValueError("Не удалось получить access_token")

            expires_in = token_data.get('expires_in', 3600)
            self.token_expires = time.time() + expires_in - 300  # 5 минут запаса

            return self.access_token

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при получении токена: {str(e)}")
            if e.response is not None:
                logger.error(f"Статус код: {e.response.status_code}")
                logger.error(f"Ответ сервера: {e.response.text}")
            raise

    async def send_message(self, prompt: str) -> Optional[str]:
        """Отправка запроса к GigaChat API"""
        try:
            if not self.access_token or time.time() >= self.token_expires:
                await self._get_access_token()

            url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.access_token}'
            }

            data = {
                "model": "GigaChat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 1000
            }

            response = requests.post(
                url,
                headers=headers,
                json=data
            )

            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']

        except Exception as e:
            logger.error(f"Ошибка при запросе к GigaChat: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Статус код: {e.response.status_code}")
                logger.error(f"Ответ сервера: {e.response.text}")
            return None
