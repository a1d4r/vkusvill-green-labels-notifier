from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from vkusvill_green_labels.models.vkusvill import NotificationType


class ToggleNotificationCD(CallbackData, prefix="toggle_notification"):
    enabled: bool


class ToggleNotificationTypeCD(CallbackData, prefix="toggle_notification_type"):
    notification_type: NotificationType


def toggle_notification_kb_builder(is_enabled: bool) -> InlineKeyboardMarkup:
    """Создать клавиатуру для переключения уведомлений."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔔 Тип уведомлений", callback_data="notification_type")],
            [
                InlineKeyboardButton(
                    text="✅ Включить" if not is_enabled else "❌ Отключить",
                    callback_data=ToggleNotificationCD(enabled=not is_enabled).pack(),
                )
            ],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu")],
        ]
    )


def toggle_notification_type_kb_builder(current_type: NotificationType) -> InlineKeyboardMarkup:
    """Создать клавиатуру для переключения типа уведомлений."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Подробные"
                    if current_type != NotificationType.detailed
                    else "📋 Подробные (выбрано)",
                    callback_data=ToggleNotificationTypeCD(
                        notification_type=NotificationType.detailed
                    ).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔢 Только количество"
                    if current_type != NotificationType.only_quantity
                    else "🔢 Только количество (выбрано)",
                    callback_data=ToggleNotificationTypeCD(
                        notification_type=NotificationType.only_quantity
                    ).pack(),
                )
            ],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="notifications")],
        ]
    )
