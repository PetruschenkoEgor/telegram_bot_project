from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.src.keyboards.main_menu import get_categories_keyboard

router = Router()


@router.callback_query(F.data == "catalog")
async def show_catalog_page(callback: CallbackQuery):
    """Показывает первую страницу каталога."""

    keyboard = await get_categories_keyboard()
    await callback.message.edit_text(
        "📚 <b>Каталог товаров:</b>\n\nВыберите категорию:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("catalog_"))
async def show_catalog_page_paginated(callback: CallbackQuery):
    """Обработчик пагинации каталога."""

    page = int(callback.data.split("_")[1])
    keyboard = await get_categories_keyboard(page=page)
    await callback.message.edit_text(
        "📚 <b>Каталог товаров:</b>\n\nВыберите категорию:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()
