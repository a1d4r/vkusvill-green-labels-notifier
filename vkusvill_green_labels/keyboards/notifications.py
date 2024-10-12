from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class ToggleNotificationCD(CallbackData, prefix="toggle_notification"):
    enabled: bool


def toggle_notification_kb_builder(is_enabled: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="❌Отключить" if is_enabled else "✅Включить",
        callback_data=ToggleNotificationCD(enabled=not is_enabled),
    )
    builder.button(text="↩️Назад в меню", callback_data="menu")
    builder.adjust(1)
    return builder.as_markup()
