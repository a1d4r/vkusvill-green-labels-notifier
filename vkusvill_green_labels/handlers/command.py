from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from vkusvill_green_labels.keyboards.menu import main_menu_kb

router = Router(name="command_router")


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text="Привет, я бот, который уведомляет о появлении новых товаров с зелеными ценниками.\n\n"
        "Для начала работы задайте адрес доставки в меню.",
        reply_markup=main_menu_kb,
    )


@router.message(Command("menu"))
async def menu_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(text="Выберите пункт в меню.", reply_markup=main_menu_kb)


@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        text="Действие отменено. Для вызова меню напишите /menu", reply_markup=ReplyKeyboardRemove()
    )
