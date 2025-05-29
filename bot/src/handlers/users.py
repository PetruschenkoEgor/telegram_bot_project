import os
from datetime import datetime

import pandas as pd
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
    ReplyKeyboardRemove,
)
from asgiref.sync import sync_to_async

from admin_panel.config import settings
from bot.src.keyboards.main_menu import (
    confirm_keyboard,
    get_button_for_cart_item,
    get_buttons_for_cart_item_delete,
    get_buttons_for_products,
    get_categories_keyboard,
    get_checkout_keyboard,
    get_faq_keyboard,
    get_menu_keyboard,
    get_subcategories_keyboard,
    pay_order,
)
from bot.src.middlewares.logging_logs import logger
from bot.src.payment_yookassa.payment_handler import create_yookassa_payment
from bot.src.services.states import DeliveryState
from bot.src.services.utils import (
    FAQ,
    AddTaskState,
    create_an_order,
    delete_all_cart_item,
    delete_cart_item,
    delete_product_cart_item,
    get_cart_items,
    get_cart_items_for_user,
    get_or_create_cart,
    get_or_create_cart_item,
    get_product,
    get_products_subcategory,
    get_subcategory,
    save_order_delivery,
    update_order_status,
    update_product,
)

router = Router()


@router.callback_query(F.data == "catalog")
async def show_categories(callback: CallbackQuery):
    """Обработчик каталога."""

    try:
        keyboard = await get_categories_keyboard(page=1)
        await callback.message.edit_text(
            "📚 <b>Категории товаров:</b>\n\nВыберите категорию:", reply_markup=keyboard, parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка обработчика каталога: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data.startswith("categories_"))
async def show_categories_page(callback: CallbackQuery):
    """Обработчик категорий с пагинацией."""

    try:
        page = int(callback.data.split("_")[1])
        keyboard = await get_categories_keyboard(page=page)
        await callback.message.edit_text(
            "📚 <b>Категории товаров:</b>\n\nВыберите категорию:", reply_markup=keyboard, parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка обработчика категорий: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "main_menu")
async def return_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Обработчик возврата в главное меню."""

    try:
        await callback.answer()
        keyboard = get_menu_keyboard()
        await callback.message.edit_text("Выберите раздел:", reply_markup=keyboard)
        await state.set_state(AddTaskState.waiting_for_task)
    except Exception as e:
        logger.error(f"Ошибка возврата в главное меню: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data.startswith("select_category_"))
async def select_category(callback: CallbackQuery):
    """Обработчик выбора подкатегории."""

    try:
        category_id = int(callback.data.split("_")[2])
        keyboard = await get_subcategories_keyboard(category_id=category_id, page=1)
        await callback.message.edit_text(
            "📚 <b>Подкатегории:</b>\n\nВыберите подкатегорию:", reply_markup=keyboard, parse_mode="HTML"
        )

        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка обработчика выбора подкатегории: {e}")
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)


@router.callback_query(F.data.startswith("subcategories_"))
async def show_subcategories_page(callback: CallbackQuery):
    """Обработчик подкатегории с пагинацией."""

    try:
        _, category_id, page = callback.data.split("_")
        keyboard = await get_subcategories_keyboard(category_id=int(category_id), page=int(page))

        await callback.message.edit_text(
            "📚 <b>Подкатегории:</b>\n\nВыберите подкатегорию:", reply_markup=keyboard, parse_mode="HTML"
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка обработчика выбора подкатегории с пагинацией: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data.startswith("select_subcategory_"))
async def select_subcategory(callback: CallbackQuery):
    """Обработчик подкатегории с выводом товаров и изображений."""

    try:
        subcategory_id = int(callback.data.split("_")[2])
        subcategory = await get_subcategory(subcategory_id)

        if not subcategory:
            await callback.answer("Подкатегория не найдена", show_alert=True)
            return

        products = await get_products_subcategory(subcategory_id)

        if not products:
            await callback.message.edit_text(f"<b>{subcategory.title}</b>\n\nТовары отсутствуют", parse_mode="HTML")
            return

        await callback.message.edit_text(f"<b>📋 {subcategory.title}</b>", parse_mode="HTML")

        for product in products:
            keyboard = await get_buttons_for_products(product_id=product.id)
            product_text = (
                f"<b>🛒 {product.title}</b>\n"
                f"📝 Описание: {product.description}\n"
                f"💰 Цена: {product.price} руб.\n"
            )

            if product.image:
                try:
                    # Полный путь к изображению
                    image_path = os.path.join(settings.MEDIA_ROOT, str(product.image))

                    if os.path.exists(image_path):
                        # Отправляем изображение с подписью
                        await callback.message.answer_photo(
                            photo=FSInputFile(image_path),
                            caption=product_text,
                            parse_mode="HTML",
                            reply_markup=keyboard,
                        )
                    else:
                        await callback.message.answer(
                            f"{product_text}\nИзображение отсутствует на сервере",
                            parse_mode="HTML",
                            reply_markup=keyboard,
                        )
                except Exception as e:
                    logger.error(f"Ошибка отправки изображения: {e}")
                    await callback.message.answer(
                        f"{product_text}\nОшибка загрузки изображения", parse_mode="HTML", reply_markup=keyboard
                    )
            else:
                await callback.message.answer(product_text, reply_markup=keyboard, parse_mode="HTML")
        keyboard_cart = await get_button_for_cart_item()
        await callback.message.answer("Переход в корзину", reply_markup=keyboard_cart)
        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка в обработчике подкатегории: {e}")
        await callback.answer("Произошла ошибка при загрузке товаров", show_alert=True)


@router.callback_query(F.data.startswith("decrease_"))
async def decrease_product_in_cart(callback: CallbackQuery):
    """Обработчик уменьшения товаров в корзине."""

    try:
        data = callback.data.split("_")

        product_id = int(data[1])
        quantity = int(data[2]) if len(data) > 2 else 1

        new_quantity = max(1, quantity - 1)

        new_keyboard = await get_buttons_for_products(product_id=product_id, quantity=new_quantity)

        if str(quantity) != str(new_quantity):
            await callback.message.edit_reply_markup(reply_markup=new_keyboard)
            await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка уменьшения количества товара: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data.startswith("increase_"))
async def increase_product_in_cart(callback: CallbackQuery):
    """Обработчик увеличения товаров в корзине."""

    try:
        data = callback.data.split("_")

        product_id = int(data[1])
        quantity = int(data[2])

        product = await get_product(product_id)
        if (quantity + 1) <= product.stock:
            new_quantity = quantity + 1
            new_keyboard = await get_buttons_for_products(product_id=product_id, quantity=new_quantity)
            if str(quantity) != str(new_quantity):
                await callback.message.edit_reply_markup(reply_markup=new_keyboard)
                await callback.answer()
        else:
            await callback.answer(f"Количество данного товара на складе {product.stock} шт.")

    except Exception as e:
        logger.error(f"Ошибка увеличения товаров в корзине: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_product_to_cart_item(callback: CallbackQuery):
    """Добавление товара в содержимое корзины."""

    try:
        data = callback.data.split("_")
        product_id = int(data[3])
        quantity = int(data[4])

        product = await get_product(product_id)

        try:
            cart = await get_or_create_cart(callback.from_user.id)
            try:
                await get_or_create_cart_item(cart=cart, product=product, quantity=quantity)
                await callback.answer(f"{product.title} в количестве {quantity} шт. добавлен в корзину.")
            except Exception as ec:
                logger.error(f"Ошибка получения или создания содержимого корзины: {ec}")
        except Exception as eu:
            logger.error(f"Ошибка создания или получения корзины: {eu}")
    except Exception as ex:
        logger.error(f"Ошибка получения пользователя: {ex}")
        await callback.answer("Произошла ошибка добавления товаров", show_alert=True)


@router.callback_query(F.data == "show_cart")
async def get_cart_item(callback: CallbackQuery):
    """Обработчик перехода в корзину."""

    try:
        user_id = callback.from_user.id
        try:
            cart = await get_or_create_cart(user_id)

            cart_items = await get_cart_items(cart)

            if not cart_items:
                await callback.message.answer("🛒 Ваша корзина пуста")
                await callback.answer()
                return

            await callback.message.answer("🛒 Ваша корзина:", parse_mode="HTML")

            for item in cart_items:
                product = await sync_to_async(lambda: item.product)()
                keyboard = await get_buttons_for_cart_item_delete(item.id)
                product_text = (
                    f"<b>{product.title}</b>\n"
                    f"Описание: {product.description}\n"
                    f"Цена: {product.price} руб.\n"
                    f"Количество: {item.quantity}\n"
                    f"Итого: {item.quantity * product.price} руб."
                )

                if product.image:
                    try:
                        image_path = os.path.join(settings.MEDIA_ROOT, str(product.image))
                        if os.path.exists(image_path):
                            await callback.message.answer_photo(
                                photo=FSInputFile(image_path),
                                caption=product_text,
                                parse_mode="HTML",
                                reply_markup=keyboard,
                            )
                        else:
                            await callback.message.answer(
                                f"{product_text}\nИзображение отсутствует на сервере",
                                parse_mode="HTML",
                                reply_markup=keyboard,
                            )
                    except Exception as e:
                        print(f"Ошибка отправки изображения: {e}")
                        await callback.message.answer(
                            f"{product_text}\nОшибка загрузки изображения", parse_mode="HTML", reply_markup=keyboard
                        )
                else:
                    await callback.message.answer(product_text, reply_markup=keyboard, parse_mode="HTML")

            total = sum(item.product.price * item.quantity for item in cart_items)
            await callback.message.answer(
                f"💳 <b>Итого к оплате: {total} руб.</b>",
                parse_mode="HTML",
                reply_markup=await get_checkout_keyboard(cart.id, total),
            )

            await callback.answer()

        except Exception as e:
            logger.error(f"Ошибка при работе с корзиной: {e}")
            await callback.answer("Произошла ошибка при загрузке корзины", show_alert=True)
    except Exception as e:
        logger.error(f"Общая ошибка в обработчике корзины: {e}")
        await callback.answer("Произошла ошибка при загрузке корзины", show_alert=True)


@router.callback_query(F.data.startswith("delete_product_"))
async def delete_product_from_cart_item(callback: CallbackQuery):
    """Обработчик удаления товара из корзины."""

    try:
        data = callback.data.split("_")
        # id содержимого корзины
        cart_item_id = int(data[2])

        await delete_product_cart_item(cart_item_id)
        await callback.answer("Товар удален из корзины", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка в обработчике удаления товара из корзины: {e}")
        await callback.answer("Произошла ошибка при удалении товаров", show_alert=True)


@router.callback_query(F.data.startswith("delete_all_cart_"))
async def delete_all_from_cart_item(callback: CallbackQuery):
    """Обработчик очистки корзины."""

    try:
        data = callback.data.split("_")
        cart_id = int(data[-1])
        await delete_all_cart_item(cart_id)
        await callback.answer("Все товары из вашей корзины удалены", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка в обработчике очистки корзины: {e}")
        await callback.answer("Произошла ошибка при удалении товаров", show_alert=True)


@router.callback_query(F.data.startswith("checkout_"))
async def get_place_on_order(callback: CallbackQuery, state: FSMContext):
    """Обработчик оформления заказа."""

    try:
        data = callback.data.split("_")
        total_price = float(data[-1])
        user_id = callback.from_user.id

        order = await create_an_order(user_id, total_price)

        await state.set_state(DeliveryState.waiting_for_address)
        await state.update_data(order_id=order.id, total_price=total_price)

        await callback.message.answer(
            "Оформление доставки\n\n"
            "Пожалуйста, введите адрес доставки в формате:\n"
            "Город\n"
            "Улица, дом, квартира\n"
            "Пример:\n"
            "Омск\n"
            "ул. Ленина, д. 10, кв. 25\n",
            reply_markup=ReplyKeyboardRemove(),
        )

        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в обработчике оформления заказа: {e}")
        await callback.answer("Произошла ошибка при оформлении заказа", show_alert=True)


@router.message(DeliveryState.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    """Обработка адреса доставки."""

    try:
        await state.update_data(delivery_address=message.text)
        await state.set_state(DeliveryState.waiting_for_phone)

        await message.answer("Введите ваш контактный телефон для связи:\n\n" "Пример: +79161234567")
    except Exception as e:
        logger.error(f"Ошибка при обработке адреса: {e}")
        await message.answer("Неверный формат адреса, попробуйте еще раз")


@router.message(DeliveryState.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Обработка номера телефона."""

    try:
        phone = message.text.strip()
        if not phone.replace("+", "").isdigit():
            raise ValueError("Неверный формат телефона")

        await state.update_data(phone=phone)
        await state.set_state(DeliveryState.waiting_for_comment)

        await message.answer("Комментарий к заказу")
    except Exception as e:
        logger.error(f"Ошибка при обработке телефона: {e}")
        await message.answer("Неверный формат телефона, попробуйте еще раз")


@router.message(DeliveryState.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    """Обработка комментария к заказу."""

    try:
        await state.update_data(comment=message.text)

        await state.set_state(DeliveryState.waiting_for_delivery_date)

        await message.answer("Укажите желаемую дату доставки:\n\n" "Формат: ДД.ММ.ГГГГ\n" "Пример: 15.05.2023\n\n")
    except Exception as e:
        logger.error(f"Ошибка при обработке комментария: {e}")
        await message.answer("Произошла ошибка, попробуйте еще раз")


@router.message(DeliveryState.waiting_for_delivery_date)
async def process_delivery_date(message: Message, state: FSMContext):
    """Обработка даты доставки."""

    try:
        delivery_date = datetime.strptime(message.text, "%d.%m.%Y").date()
        await state.update_data(delivery_date=delivery_date)

        data = await state.get_data()

        order_summary = (
            "Данные заказа:\n\n"
            f"Адрес: {data['delivery_address']}\n"
            f"Телефон: {data.get('phone', 'не указан')}\n"
            f"Комментарий: {data.get('comment', 'нет')}\n"
            f"Дата доставки: {delivery_date.strftime('%d.%m.%Y')}\n"
            f"Сумма заказа: {data['total_price']} руб.\n\n"
            "Подтвердите оформление заказа:"
        )

        await message.answer(order_summary, reply_markup=await confirm_keyboard())
    except Exception as e:
        logger.error(f"Ошибка при обработке даты доставки: {e}")
        await message.answer("Произошла ошибка, попробуйте еще раз")


@router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    """Подтверждение заказа."""

    try:
        data = await state.get_data()
        user_id = callback.from_user.id
        order_id = data["order_id"]
        total_price = data["total_price"]

        await save_order_delivery(
            order_id=order_id,
            address=data["delivery_address"],
            phone=data.get("phone", ""),
            comment=data.get("comment", ""),
            delivery_date=data.get("delivery_date"),
        )

        # после подтверждения заказа, получаем содержимое корзины
        cart_items = await get_cart_items_for_user(user_id)

        payment = await create_yookassa_payment(order_id, user_id, total_price)

        await update_order_status(data["order_id"], "processing")

        # Формируем данные для Excel
        order_data = {
            "ID заказа": order_id,
            "Дата": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Пользователь": f"ID: {user_id}",
            "Телефон": data.get("phone", "не указан"),
            "Адрес": data["delivery_address"],
            "Комментарий": data.get("comment", "нет"),
            "Дата доставки": data.get("delivery_date", "не указана"),
            "Сумма": total_price,
            "Статус": "processing",
            "Товары": ", ".join(
                [
                    f"{item.get("product_id")}. {item.get('title')} x{item.get('quantity', 1)} x{item.get("price")} руб."
                    for item in cart_items["items"]
                ]
            ),
            "ID платежа": payment.id,
        }

        excel_file = "orders.xlsx"
        if os.path.exists(excel_file):
            df = pd.read_excel(excel_file)
            df = pd.concat([df, pd.DataFrame([order_data])], ignore_index=True)
        else:
            df = pd.DataFrame([order_data])

        df.to_excel(excel_file, index=False)

        await callback.message.answer(
            "Ваш заказ оформлен!\n\n"
            f"Номер заказа: {data['order_id']}\n"
            "Мы скоро свяжемся с вами для уточнения деталей.",
            reply_markup=await pay_order(payment.confirmation.confirmation_url, order_id),
        )

        await state.clear()
        try:
            # после подтверждения заказа, изменяем количество товаров на остатке
            await update_product(cart_items)
            try:
                # очищаем корзину
                await delete_cart_item(user_id)

                await callback.answer()
            except Exception as e:
                logger.error(f"Ошибка очистки корзины: {e}")
                await callback.answer("Произошла ошибка при подтверждении заказа", show_alert=True)
        except Exception as e:
            logger.error(f"Ошибка изменения количества товаров на остатке: {e}")
            await callback.answer("Произошла ошибка при подтверждении заказа", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка получения содержимого корзины: {e}")
        await callback.answer("Произошла ошибка при подтверждении заказа", show_alert=True)


@router.callback_query(F.data == "faq")
async def handler_faq(callback: CallbackQuery):
    """Обработчик кнопки FAQ."""

    try:
        await callback.message.edit_text("Выберите действие:", reply_markup=await get_faq_keyboard())
        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка FAQ: {e}")
        await callback.answer("Ошибка открытия FAQ", show_alert=True)


@router.inline_query()
async def inline_faq_handler(inline_query: InlineQuery):
    """Обработчик инлайн-запросов с автодополнением."""

    try:
        query = inline_query.query.lower().strip()
        results = []

        for question, answer in FAQ.items():
            # Показываем либо все вопросы при пустом запросе, либо совпадения
            if not query or query in question.lower() or query in answer.lower():
                result = InlineQueryResultArticle(
                    id=str(hash(question)),
                    title=question.capitalize(),
                    description=answer[:100],
                    input_message_content=InputTextMessageContent(
                        message_text=f"<b>{question.capitalize()}</b>\n\n{answer}", parse_mode="HTML"
                    ),
                    reply_markup=await get_faq_keyboard(),
                )
                results.append(result)

                if len(results) >= 50:
                    break

        await inline_query.answer(results, is_personal=True)
    except Exception as e:
        logger.error(f"Ошибка в inline_faq_handler: {e}")
        await inline_query.answer([])


@router.callback_query(F.data == "show_all_faq")
async def show_all_faq(callback: CallbackQuery):
    """Показывает все вопросы в одном сообщении."""

    try:
        faq_text = "\n\n".join(f"<b>{q.capitalize()}</b>\n{a}" for q, a in FAQ.items())
        await callback.message.edit_text(
            f"Часто задаваемые вопросы:\n\n{faq_text}", parse_mode="HTML", reply_markup=await get_faq_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка загрузки вопросов: {e}")
        await callback.answer("Ошибка при загрузке вопросов", show_alert=True)
