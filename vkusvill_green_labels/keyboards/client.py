from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

request_location_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🌐 Поделиться координатами", request_location=True)]],
    resize_keyboard=True,
)

address_verify_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Сохранить", callback_data="save_address"),
            InlineKeyboardButton(text="🔄 Поменять", callback_data="change_address"),
        ]
    ]
)
