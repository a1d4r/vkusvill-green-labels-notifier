from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Адрес доставки", callback_data="address")],
        [InlineKeyboardButton(text="🔔 Уведомления", callback_data="notifications")],
    ],
    resize_keyboard=True,
)

back_to_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="↩️Назад в меню", callback_data="back_to_menu")]]
)
