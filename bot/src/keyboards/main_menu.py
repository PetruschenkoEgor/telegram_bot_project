from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.src.services.utils import get_categories_page


def get_menu_keyboard():
    """Клавиатура Каталог, Корзина, FAQ."""

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Каталог", callback_data="catalog")
            ],
            [
                InlineKeyboardButton(text="Корзина", callback_data="cart")
            ],
            [
                InlineKeyboardButton(text="FAQ", callback_data="faq")
            ]
        ]
    )
    return keyboard


async def get_pagination_buttons_categories_keyboard(page_obj):
    """Клавиатура пагинации категорий."""

    pagination_buttons = []
    if page_obj.has_previous():
        pagination_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"catalog_{page_obj.previous_page_number()}"
        ))

    if page_obj.has_next():
        pagination_buttons.append(InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data=f"catalog_{page_obj.next_page_number()}"
        ))

    return pagination_buttons


async def get_categories_keyboard(page: int = 1):
    """Клавиатура Категории."""

    categories_data = await get_categories_page(page=page)
    page_obj = categories_data['page_obj']
    categories = categories_data['object_list']

    pagination_buttons = await get_pagination_buttons_categories_keyboard(page_obj)

    keyboard_rows = []

    for category in categories:
        keyboard_rows.append([
            InlineKeyboardButton(
                text=category['title'],
                callback_data=f"category_{category['id']}"
            )
        ])

    if pagination_buttons:
        keyboard_rows.append(pagination_buttons)

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

    return keyboard
