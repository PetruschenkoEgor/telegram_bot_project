from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.src.keyboards.main_menu import get_menu_keyboard
from bot.src.services.utils import register_user, is_subscribe, AddTaskState, NOT_SUB_MESSAGE, check_sub_kb, \
    get_or_create_cart
from bot.src.handlers import users

router = Router()
router.include_router(users.router)


@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start."""

    await register_user(message.from_user.id)

    if await is_subscribe(message.from_user.id):
        try:
            keyboard = get_menu_keyboard()
            await message.answer("Выберете раздел:", reply_markup=keyboard)
        except Exception as e:
            print(f"Ошибка при создании клавиатуры: {e}")
            await message.answer("Произошла ошибка, попробуйте позже.")
        await state.set_state(AddTaskState.waiting_for_task)  # Устанавливаем состояние
    else:
        await message.answer(
            NOT_SUB_MESSAGE,
            reply_markup=check_sub_kb(),
            parse_mode="HTML"
        )


@router.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription(callback: types.CallbackQuery):
    """Обработчик нажатия кнопки 'Проверить подписку'."""

    if await is_subscribe(callback.from_user.id):
        await callback.message.edit_text("✅ Спасибо за подписку! Теперь вам доступен бот.")
    else:
        await callback.answer("Вы ещё не подписались на все каналы!", show_alert=True)
