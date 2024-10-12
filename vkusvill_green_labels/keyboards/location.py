from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

confirm_location_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Сохранить", callback_data="save_address"),
            InlineKeyboardButton(text="🔄 Поменять", callback_data="change_address"),
        ]
    ],
    resize_keyboard=True,
)
