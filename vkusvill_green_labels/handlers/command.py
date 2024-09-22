from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from vkusvill_green_labels.keyboards.client import request_location_kb

router = Router(name="command_router")


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        text="Привет, я бот, который уведомляет пользователя о появлении новых товаров с зелеными ценниками\n\n"
        "Отправь месторасположение для того, чтобы был подобран ближайший магазин!",
        reply_markup=request_location_kb,
    )
