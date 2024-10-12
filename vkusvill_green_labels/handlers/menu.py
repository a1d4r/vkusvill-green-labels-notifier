from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from vkusvill_green_labels.keyboards.menu import main_menu_kb

router = Router(name="menu_router")


@router.callback_query(F.data == "menu")
async def back_to_menu_handler(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    if not isinstance(callback.message, Message):
        return
    await callback.message.edit_text(text="Выберите пункт в меню.", reply_markup=main_menu_kb)
    await callback.answer()
