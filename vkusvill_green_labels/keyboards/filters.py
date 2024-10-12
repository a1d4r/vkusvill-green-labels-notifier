from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from vkusvill_green_labels.models.db import Filter
from vkusvill_green_labels.models.filters import FilterType
from vkusvill_green_labels.models.types import FilterID


class SelectFilterTypeCD(CallbackData, prefix="select_filter_type"):
    filter_type: FilterType


class SelectFilterCD(CallbackData, prefix="select_filter"):
    filter_id: FilterID


class DeleteFilterCD(CallbackData, prefix="delete_filter"):
    filter_id: FilterID


back_to_filters_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="↩️ Назад к фильтрам", callback_data="filters")]]
)

enter_filter_name_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⏩ Пропустить", callback_data="skip_filter_name")],
        [InlineKeyboardButton(text="↩️ Назад к фильтрам", callback_data="filters")],
    ]
)

confirm_filter_creation_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Сохранить", callback_data="save_filter"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="filters"),
        ]
    ]
)


def view_filter_kb_builder(filter_: Filter) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Удалить", callback_data=DeleteFilterCD(filter_id=filter_.id))
    builder.button(text="↩️ Назад к фильтрам", callback_data="filters")
    builder.adjust(1, repeat=True)
    return builder.as_markup()


def filters_kb_builder(filters: list[Filter]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for filter_ in filters:
        filter_name = filter_.name
        if not filter_name:
            filter_name = filter_.definition.generate_name()
        if len(filter_name) > 20:
            filter_name = filter_name[:20] + "..."
        builder.button(text=filter_name, callback_data=SelectFilterCD(filter_id=filter_.id))
    builder.button(text="➕ Создать новый фильтр", callback_data="add_filter")  # noqa: RUF001
    builder.button(text="↩️ Назад в меню", callback_data="menu")
    builder.adjust(1, repeat=True)
    return builder.as_markup()


def select_filter_type_kb_builder() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⚪ Белый список",
        callback_data=SelectFilterTypeCD(filter_type=FilterType.title_whitelist),
    )
    builder.button(
        text="⚫ Чёрный список",
        callback_data=SelectFilterTypeCD(filter_type=FilterType.title_blacklist),
    )
    builder.button(text="↩️ Назад к фильтрам", callback_data="filters")
    builder.adjust(1)
    return builder.as_markup()
