from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils import formatting as fmt
from dishka import FromDishka

from vkusvill_green_labels.keyboards.location import confirm_location_kb
from vkusvill_green_labels.keyboards.menu import back_to_menu_kb, main_menu_kb
from vkusvill_green_labels.models.vkusvill import AddressInfo
from vkusvill_green_labels.services.user_service import UserService
from vkusvill_green_labels.services.vkusvill_service import VkusvillService

router = Router(name="location_router")


class SelectAddress(StatesGroup):
    verify_address = State()
    confirm_address = State()


@router.callback_query(F.data == "address")
async def request_location_handler(
    callback: CallbackQuery, state: FSMContext, user_service: FromDishka[UserService]
) -> None:
    if not isinstance(callback.message, Message):
        return
    await state.clear()
    address_info = await user_service.get_user_address(callback.from_user)
    instruction = fmt.as_marked_list(
        "Нажмите на иконку скрепки 📎",
        "Переключитесь на вкладку «Геопозиция»",
        "Выберите месторасположение",
    )
    if address_info:
        content = fmt.as_list(
            fmt.Text("Текущий адрес доставки: ", fmt.Bold(address_info.address)),
            "",
            "Для смены адреса отправьте новую геопозицию:",
            instruction,
        )
        await callback.message.edit_text(**content.as_kwargs(), reply_markup=back_to_menu_kb)
        await callback.answer()
    else:
        content = fmt.as_marked_list("Отправьте геопозицию по адресу доставки:", instruction)
        await callback.message.edit_text(**content.as_kwargs(), reply_markup=back_to_menu_kb)
        await callback.answer()
    await state.set_state(SelectAddress.verify_address)


@router.message(StateFilter(SelectAddress.verify_address), F.location)
async def get_location_address_handler(
    message: Message, state: FSMContext, vkusvill_service: FromDishka[VkusvillService]
) -> None:
    if message.location is None:
        return
    address_info = await vkusvill_service.get_address_info_by_location(
        latitude=message.location.latitude, longitude=message.location.longitude
    )
    if address_info is None:
        await message.answer(
            text=(
                "Адрес не найден. Скорее всего ВкусВилл не доставляет по указанному "
                "вами адресу. Попробуйте повторить попытку позже, либо отправьте другой адрес."
            ),
            reply_markup=back_to_menu_kb,
        )
        return
    await state.update_data(address_info=address_info.model_dump(mode="json"))
    await state.set_state(SelectAddress.confirm_address)
    await message.answer(
        text=f"Ваш адрес: {address_info.address}", reply_markup=confirm_location_kb
    )


@router.callback_query(StateFilter(SelectAddress.confirm_address), F.data == "save_address")
async def save_address_handler(
    callback: CallbackQuery, state: FSMContext, user_service: FromDishka[UserService]
) -> None:
    if not isinstance(callback.message, Message):
        return
    state_data = await state.get_data()
    address_info = AddressInfo.model_validate(state_data["address_info"])
    await user_service.save_address_for_user(callback.from_user, address_info)
    await callback.message.edit_text(
        text=f'Адрес "{address_info.address}" успешно сохранен!', reply_markup=back_to_menu_kb
    )
    await callback.answer()
    await state.clear()


@router.callback_query(StateFilter(SelectAddress.confirm_address), F.data == "change_address")
async def change_address_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback.message, Message):
        return
    await callback.message.edit_text(text="Отправьте новую геопозицию.")
    await callback.answer()
    await state.clear()
    await state.set_state(SelectAddress.verify_address)


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if not isinstance(callback.message, Message):
        return
    await callback.message.edit_text(text="Выберите пункт в меню.", reply_markup=main_menu_kb)
    await callback.answer()
