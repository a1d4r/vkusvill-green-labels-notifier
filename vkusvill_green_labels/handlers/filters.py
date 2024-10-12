from typing import assert_never

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.utils import formatting as fmt
from dishka import FromDishka

from vkusvill_green_labels.keyboards.filters import (
    DeleteFilterCD,
    SelectFilterCD,
    SelectFilterTypeCD,
    back_to_filters_kb,
    confirm_filter_creation_kb,
    filters_kb_builder,
    select_filter_type_kb_builder,
    view_filter_kb_builder,
)
from vkusvill_green_labels.models.filters import (
    FilterType,
    TitleBlackListFilter,
    TitleWhiteListFilter,
)
from vkusvill_green_labels.services.filter_service import FilterService
from vkusvill_green_labels.services.user_service import UserService

router = Router(name="filters_router")


class CreateFilter(StatesGroup):
    select_filter_type = State()
    enter_word_list = State()
    enter_filter_name = State()
    confirm = State()


def get_filter_type_text(filter_type: FilterType) -> str:
    match filter_type:
        case FilterType.title_whitelist:
            return "⚪ белый список"
        case FilterType.title_blacklist:
            return "⚫ чёрный список"
        case _:
            assert_never(filter_type)


@router.callback_query(F.data == "filters")
async def filters_handler(
    callback: CallbackQuery, state: FSMContext, user_service: FromDishka[FilterService]
) -> None:
    if not isinstance(callback.message, Message):
        return
    await state.clear()
    filters = await user_service.get_filters_by_telegram_user(callback.from_user)
    text = "У вас нет созданных фильтров." if not filters else "Ваши активные фильтры:"
    await callback.message.edit_text(text=text, reply_markup=filters_kb_builder(filters))
    await callback.answer()


@router.callback_query(F.data == "add_filter")
async def add_filter_handler(callback: CallbackQuery, state: FSMContext) -> None:
    if not isinstance(callback.message, Message):
        return
    text = fmt.as_marked_section(
        "Выберите тип фильтра:",
        fmt.as_key_value(
            "Белый список", "пропускает все товары, в наименовании которых есть указанные слова."
        ),
        fmt.as_key_value(
            "Чёрный список", "исключает все товары, в наименовании которых есть указанные слова."
        ),
    )
    await callback.message.edit_text(
        **text.as_kwargs(), reply_markup=select_filter_type_kb_builder()
    )
    await state.set_state(CreateFilter.enter_word_list)
    await callback.answer()


@router.callback_query(SelectFilterTypeCD.filter())
async def select_filter_type_handler(
    callback: CallbackQuery, callback_data: SelectFilterTypeCD, state: FSMContext
) -> None:
    if not isinstance(callback.message, Message):
        return
    await state.update_data(filter_type=callback_data.filter_type)
    await state.set_state(CreateFilter.enter_word_list)
    match callback_data.filter_type:
        case FilterType.title_whitelist:
            text = "Введите список слов для белого списка, через запятую:"
        case FilterType.title_blacklist:
            text = "Введите список слов для чёрного списка, через запятую:"
        case _:
            assert_never(callback_data.filter_type)
    await callback.message.edit_text(text, reply_markup=back_to_filters_kb)
    await callback.answer()


@router.message(StateFilter(CreateFilter.enter_word_list))
async def enter_word_list_handler(message: Message, state: FSMContext) -> None:
    if not message.text:
        return
    await state.update_data(word_list=message.text)
    await state.set_state(CreateFilter.enter_filter_name)
    await message.answer("Введите название фильтра:", reply_markup=back_to_filters_kb)


@router.message(StateFilter(CreateFilter.enter_filter_name))
async def confirm_handler(message: Message, state: FSMContext) -> None:
    if not message.text:
        return
    await state.update_data(filter_name=message.text)
    await state.set_state(CreateFilter.confirm)
    state_data = await state.get_data()
    text = fmt.as_list(
        "Подтвердите создание фильтра:",
        fmt.as_key_value("Тип", get_filter_type_text(state_data["filter_type"])),
        fmt.as_key_value("Список слов", state_data["word_list"]),
        fmt.as_key_value("Название", state_data["filter_name"]),
    )
    await message.answer(**text.as_kwargs(), reply_markup=confirm_filter_creation_kb)


@router.callback_query(StateFilter(CreateFilter.confirm), F.data == "save_filter")
async def save_filter_handler(
    callback: CallbackQuery, state: FSMContext, user_service: FromDishka[UserService]
) -> None:
    if not isinstance(callback.message, Message):
        return
    state_data = await state.get_data()
    await user_service.create_filter_for_user(
        telegram_user=callback.from_user,
        filter_type=state_data["filter_type"],
        word_list=state_data["word_list"].split(","),
        filter_name=state_data["filter_name"],
    )
    await state.clear()
    await callback.message.edit_text("Фильтр успешно создан.", reply_markup=back_to_filters_kb)
    await callback.answer()


@router.callback_query(SelectFilterCD.filter())
async def show_filter_info_handler(
    callback: CallbackQuery,
    callback_data: SelectFilterCD,
    filter_service: FromDishka[FilterService],
) -> None:
    if not isinstance(callback.message, Message):
        return
    filter_ = await filter_service.get_filter_by_telegram_user_and_id(
        callback.from_user, callback_data.filter_id
    )
    if not filter_:
        await callback.message.edit_text("Фильтр не найден.")
    else:
        match filter_.definition:
            case TitleWhiteListFilter():
                filter_details = [
                    fmt.as_key_value("Список слов", ", ".join(filter_.definition.whitelist))
                ]
            case TitleBlackListFilter():
                filter_details = [
                    fmt.as_key_value("Список слов", ", ".join(filter_.definition.blacklist))
                ]
            case _:
                assert_never(filter_.definition.filter_type)
        text = fmt.as_list(
            "Информация о фильтре:\n",
            fmt.as_key_value("Название", filter_.name or "Без названия"),
            fmt.as_key_value("Тип", get_filter_type_text(filter_.definition.filter_type)),
            *filter_details,
        )
        await callback.message.edit_text(
            **text.as_kwargs(), reply_markup=view_filter_kb_builder(filter_)
        )
    await callback.answer()


@router.callback_query(DeleteFilterCD.filter())
async def delete_filter_handler(
    callback: CallbackQuery,
    callback_data: DeleteFilterCD,
    filter_service: FromDishka[FilterService],
) -> None:
    if not isinstance(callback.message, Message):
        return
    await filter_service.delete_filter_by_telegram_user_and_id(
        callback.from_user, callback_data.filter_id
    )
    await callback.message.edit_text("Фильтр успешно удален.", reply_markup=back_to_filters_kb)
    await callback.answer()
