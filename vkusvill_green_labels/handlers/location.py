from decimal import Decimal

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from vkusvill_green_labels.keyboards.client import address_verify_kb, request_location_kb
from vkusvill_green_labels.services.vkusvill_api import VkusvillApi

router = Router(name="location_router")


@router.message(F.location)
async def location_handler(
    message: Message, state: FSMContext, vkusvill_api: FromDishka[VkusvillApi]
) -> None:
    if message.location is None:
        return
    latitude, longitude = Decimal(message.location.latitude), Decimal(message.location.longitude)
    await vkusvill_api.authorize()
    address_info = await vkusvill_api.get_address_info(latitude, longitude)
    if address_info is None:
        await message.answer(
            text="Адрес не найден. Скорее всего ВкусВилл не доставляет по указанному вами адресу. Попробуйте еще раз",
            reply_markup=request_location_kb,
        )
        return
    await state.update_data(latitude=latitude, longitude=longitude, address=address_info.address)
    await message.answer(text=f"Ваш адрес: {address_info.address}", reply_markup=address_verify_kb)


locations = {}  # key: telegram_id; values: latitude, longitude


@router.callback_query(F.data == "save_address")
async def save_address_handler(call: CallbackQuery, state: FSMContext) -> None:
    location = await state.get_data()
    await state.clear()
    latitude, longitude = location["latitude"], location["longitude"]
    locations[call.from_user.id] = {"latitude": latitude, "longitude": longitude}
    if not isinstance(call.message, Message):
        return
    await call.message.edit_text(text=f"Адрес {location['address']} сохранен!")


@router.callback_query(F.data == "change_address")
async def change_address_handler(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if not isinstance(call.message, Message):
        return
    await call.message.delete()
    await call.message.answer(
        text="Отправь свои координаты по новой", reply_markup=request_location_kb
    )
