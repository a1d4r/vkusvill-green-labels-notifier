from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from vkusvill_green_labels.keyboards.client import address_verify_kb, request_location_kb

router = Router(name="location_router")


@router.message(F.location)
async def location_handler(message: Message, state: FSMContext) -> None:
    if message.location is None:
        return
    latitude, longitude = message.location.latitude, message.location.longitude
    await state.update_data(latitude=latitude, longitude=longitude)
    await message.answer(text="Ваш адрес: Ул. Вкусвилл, дом 7", reply_markup=address_verify_kb)


locations = {}  # key: telegram_id; values: latitude, longitude


@router.callback_query(F.data == "save_address")
async def save_address_handler(call: CallbackQuery, state: FSMContext) -> None:
    location = await state.get_data()
    await state.clear()
    latitude, longitude = location["latitude"], location["longitude"]
    locations[call.from_user.id] = {"latitude": latitude, "longitude": longitude}
    if not isinstance(call.message, Message):
        return
    await call.message.edit_text(
        text=f"Адрес по координатам <code>{latitude}, {longitude}</code> сохранен!"
    )


@router.callback_query(F.data == "change_address")
async def change_address_handler(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if not isinstance(call.message, Message):
        return
    await call.message.delete()
    await call.message.answer(
        text="Отправь свои координаты по новой", reply_markup=request_location_kb
    )
