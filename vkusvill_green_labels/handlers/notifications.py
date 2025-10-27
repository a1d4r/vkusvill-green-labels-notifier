from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from vkusvill_green_labels.keyboards.menu import back_to_menu_kb
from vkusvill_green_labels.keyboards.notifications import (
    ToggleNotificationCD,
    ToggleNotificationTypeCD,
    toggle_notification_kb_builder,
    toggle_notification_type_kb_builder,
)
from vkusvill_green_labels.models.vkusvill import NotificationType
from vkusvill_green_labels.services.user_service import UserService

router = Router(name="notification_router")


@router.callback_query(F.data == "notifications")
async def notifications_handler(
    callback: CallbackQuery, state: FSMContext, user_service: FromDishka[UserService]
) -> None:
    if not isinstance(callback.message, Message):
        return
    await state.clear()
    is_enabled = await user_service.get_user_notifications_settings(callback.from_user)
    text = "Уведомления включены 🟢" if is_enabled else "Уведомления отключены 🔴"
    await callback.message.edit_text(
        text=text, reply_markup=toggle_notification_kb_builder(is_enabled)
    )
    await callback.answer()


@router.callback_query(ToggleNotificationCD.filter())
async def toggle_notifications_handler(
    callback: CallbackQuery,
    callback_data: ToggleNotificationCD,
    user_service: FromDishka[UserService],
) -> None:
    if not isinstance(callback.message, Message):
        return
    await user_service.update_user_notifications_settings(callback.from_user, callback_data.enabled)
    if callback_data.enabled:
        text = "Уведомления включены 🟢. \n\nТеперь вы будете получать уведомления о появлении новых товаров."
    else:
        text = "Уведомления отключены 🔴. \n\nТеперь вы не будете получаете уведомления о появлении новых товаров."
    await callback.message.edit_text(text=text, reply_markup=back_to_menu_kb)
    await callback.answer()


@router.callback_query(F.data == "notification_type")
async def notification_type_handler(
    callback: CallbackQuery, state: FSMContext, user_service: FromDishka[UserService]
) -> None:
    if not isinstance(callback.message, Message):
        return
    await state.clear()
    current_type = await user_service.get_user_notification_type(callback.from_user)
    text = "Выберите тип уведомлений:\n\n"
    text += "📋 Подробные - с описанием товаров и ценами\n"
    text += "🔢 Только количество - уведомления об изменении количества товаров\n"
    text += "📈 Только добавление - уведомления приходят только при увеличении количества товаров"
    await callback.message.edit_text(
        text=text, reply_markup=toggle_notification_type_kb_builder(current_type)
    )
    await callback.answer()


@router.callback_query(ToggleNotificationTypeCD.filter())
async def toggle_notification_type_handler(
    callback: CallbackQuery,
    callback_data: ToggleNotificationTypeCD,
    user_service: FromDishka[UserService],
) -> None:
    if not isinstance(callback.message, Message):
        return
    await user_service.update_user_notification_type(
        callback.from_user, callback_data.notification_type
    )
    text = "Тип уведомлений изменен на "
    if callback_data.notification_type == NotificationType.detailed:
        text += "📋 Подробные"
    elif callback_data.notification_type == NotificationType.only_quantity:
        text += "🔢 Только количество"
    else:
        text += "📈 Только добавление"
    await callback.message.edit_text(text=text, reply_markup=back_to_menu_kb)
    await callback.answer()
