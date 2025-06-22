import os
import uuid

from dotenv import load_dotenv
from yookassa import Payment

load_dotenv()

# имя бота
YOUR_BOT = os.getenv("YOUR_BOT")
YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")


async def create_yookassa_payment(order_id: int, user_id: int, total_price: float):
    """Создание платежа в Юкасса."""

    idempotence_key = str(uuid.uuid4())  # Уникальный ключ идемпотентности

    payment = Payment.create(
        {
            "amount": {"value": f"{total_price:.2f}", "currency": "RUB"},
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://t.me/{YOUR_BOT}",  # Вернет пользователя в бота
            },
            "capture": True,
            "description": f"Оплата заказа №{order_id}",
            "metadata": {"order_id": order_id, "user_id": user_id},
        },
        idempotence_key,
    )

    return payment
