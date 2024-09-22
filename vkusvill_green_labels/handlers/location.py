from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from vkusvill_green_labels.keyboards.client import address_verify_kb, request_location_kb
from vkusvill_green_labels.services.user_service import UserService
from vkusvill_green_labels.services.vkusvill_service import VkusvillService

router = Router(name="location_router")


@router.message(F.location)
async def location_handler(
    message: Message, state: FSMContext, vkusvill_service: FromDishka[VkusvillService]
) -> None:
    if message.location is None:
        return
    address_info = await vkusvill_service.get_address_info_by_location(
        latitude=message.location.latitude, longitude=message.location.longitude
    )
    if address_info is None:
        await message.answer(
            text="Адрес не найден. Скорее всего ВкусВилл не доставляет по указанному вами адресу. Попробуйте еще раз",
            reply_markup=request_location_kb,
        )
        return
    await state.update_data(
        latitude=address_info.latitude,
        longitude=address_info.longitude,
        address=address_info.address,
    )
    await message.answer(
        text=f"Ваш адрес: {address_info.address} ({address_info.latitude}, {address_info.longitude})",
        reply_markup=address_verify_kb,
    )


@router.callback_query(F.data == "save_address")
async def save_address_handler(
    call: CallbackQuery, state: FSMContext, user_service: FromDishka[UserService]
) -> None:
    location = await state.get_data()
    await state.clear()
    latitude, longitude, address = location["latitude"], location["longitude"], location["address"]
    await user_service.save_address_for_user(call.from_user, address, latitude, longitude)
    if not isinstance(call.message, Message):
        return
    await call.message.edit_text(text=f"Адрес {address} ({latitude}, {longitude}) сохранен!")


@router.callback_query(F.data == "change_address")
async def change_address_handler(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if not isinstance(call.message, Message):
        return
    await call.message.delete()
    await call.message.answer(text="Отправьте новый адрес", reply_markup=request_location_kb)
