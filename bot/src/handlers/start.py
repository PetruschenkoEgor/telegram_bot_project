from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.src.config.settings import bot, channel, group, channel_name, group_name

router = Router()

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
        group_subscribe = await bot.get_chat_member(group, user_id)
        return (channel_subscribe.status in ["member", "administrator", "creator"] and
                group_subscribe.status in ["member", "administrator", "creator"])
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False


@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    """Реагирует на команду /start."""

    if await is_subscribe(message.from_user.id):
        await state.set_state(AddTaskState.waiting_for_task)  # Устанавливаем состояние
    else:
        await message.answer(
            NOT_SUB_MESSAGE,
            reply_markup=check_sub_kb(),
            parse_mode="HTML"
        )


@router.callback_query(lambda c: c.data == "check_subscription")
async def check_subscription(callback: types.CallbackQuery):
    """Обработка нажатия кнопки 'Проверить подписку'."""

    if await is_subscribe(callback.from_user.id):
        await callback.message.edit_text("✅ Спасибо за подписку! Теперь вам доступен бот.")
    else:
        await callback.answer("Вы ещё не подписались на все каналы!", show_alert=True)
