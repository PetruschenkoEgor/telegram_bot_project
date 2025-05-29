from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from admin_panel.app.models import Cart
from bot.src.services.utils import get_categories_page, get_subcategories_page


def get_menu_keyboard():
    """Клавиатура Каталог, Корзина, FAQ."""

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Каталог", callback_data="catalog"))
    builder.add(InlineKeyboardButton(text="Корзина", callback_data="show_cart"))
    builder.add(InlineKeyboardButton(text="FAQ", callback_data="faq"))
    builder.adjust(1)

    return builder.as_markup()


async def get_categories_keyboard(page: int = 1):
    """Клавиатура Категории."""

    categories_data = await get_categories_page(page=page)
    page_obj = categories_data['page_obj']
    categories = categories_data['object_list']

    builder = InlineKeyboardBuilder()

    for category in categories:
        builder.add(InlineKeyboardButton(
            text=category['title'],
            callback_data=f"select_category_{category['id']}"
        ))

    if page_obj.has_previous():
        builder.add(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"categories_{page_obj.previous_page_number()}"
        ))

    if page_obj.has_next():
        builder.add(InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data=f"categories_{page_obj.next_page_number()}"
        ))

    main_menu = InlineKeyboardButton(
        text="↩️ На главную",
        callback_data="main_menu"
    )

    builder.adjust(1)
    builder.row(main_menu)

    return builder.as_markup()


async def get_subcategories_keyboard(category_id: int, page: int = 1):
    """Клавиатура подкатегорий."""

    subcategories_data = await get_subcategories_page(category_id, page=page)
    page_obj = subcategories_data['page_obj']
    subcategories = subcategories_data['object_list']

    builder = InlineKeyboardBuilder()

    for subcategory in subcategories:
        builder.add(InlineKeyboardButton(
            text=subcategory['title'],
            callback_data=f"select_subcategory_{subcategory['id']}"
        ))

    if page_obj.has_previous():
        builder.add(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"subcategories_{category_id}_{page_obj.previous_page_number()}"
        ))

    if page_obj.has_next():
        builder.add(InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data=f"subcategories_{category_id}_{page_obj.next_page_number()}"
        ))

    builder.add(InlineKeyboardButton(
        text="↩️ Назад к категориям",
        callback_data="catalog"
    ))

    builder.adjust(1)

    return builder.as_markup()


async def get_buttons_for_products(product_id: int, quantity: int = 1):
    """Клавиатура товаров."""

    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="➖", callback_data=f"decrease_{product_id}_{quantity}"))
    builder.add(InlineKeyboardButton(text=f"{quantity} шт.", callback_data=f"show_quantity_{product_id}"))
    builder.add(InlineKeyboardButton(text="➕", callback_data=f"increase_{product_id}_{quantity}"))

    builder.add(InlineKeyboardButton(
        text="🛒 Добавить в корзину",
        callback_data=f"add_to_cart_{product_id}_{quantity}"
    ))

    builder.adjust(3, 1)

    return builder.as_markup()


async def get_button_for_cart_item():
    """Клавиатура для содержимого корзины."""

    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="🛒 Корзина", callback_data="show_cart"))

    builder.adjust(1)
    return builder.as_markup()


async def get_buttons_for_cart_item_delete(card_id: int):
    """Клавиатура для удаления товаров из корзины."""

    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="Удалить", callback_data=f"delete_product_{card_id}"))

    builder.adjust(1)

    return builder.as_markup()


async def get_checkout_keyboard(cart_id: int, total_price: float):
    """Клавиатура для оформления заказа."""

    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="Очистить корзину", callback_data=f"delete_all_cart_{cart_id}"))
    builder.add(
        InlineKeyboardButton(
            text="💳 Оформить заказ",
            callback_data=f"checkout_{total_price}"
        )
    )

    builder.adjust(1)

    return builder.as_markup()


async def confirm_keyboard():
    """Клавиатура подтверждения заказа."""

    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="✅ Подтвердить заказ", callback_data="confirm_order"))

    builder.adjust(1)

    return builder.as_markup()


async def pay_order(order_id: int, total_price: float):
    """Клавиатура для перехода оплаты заказа."""

    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="💵 Оплатить заказ", callback_data=f"order_{order_id}_{total_price}"))

    builder.adjust(1)

    return builder.as_markup()
