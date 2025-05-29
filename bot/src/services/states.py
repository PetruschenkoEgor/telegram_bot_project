from aiogram.fsm.state import State, StatesGroup


class DeliveryState(StatesGroup):
    """Класс установки состояния для Доставки."""

    waiting_for_address = State()
    waiting_for_phone = State()
    waiting_for_comment = State()
    waiting_for_delivery_date = State()
