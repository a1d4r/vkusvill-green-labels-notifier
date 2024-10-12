from typing import Annotated, Literal, override

from abc import abstractmethod
from enum import StrEnum

import pydantic

from pydantic import BaseModel, field_validator

from vkusvill_green_labels.models.vkusvill import GreenLabelItem


class FilterType(StrEnum):
    title_whitelist = "title_whitelist"
    title_blacklist = "title_blacklist"


class BaseFilter(BaseModel):
    filter_type: FilterType

    @abstractmethod
    def satisfies(self, green_label_item: GreenLabelItem) -> bool: ...

    @abstractmethod
    def generate_name(self) -> str: ...


class TitleWhiteListFilter(BaseFilter):
    """
    Как минимум одно слово из белого списка должно быть в наименовании товара с зелённым ценником.
    """

    filter_type: Literal[FilterType.title_whitelist] = FilterType.title_whitelist
    whitelist: list[str]

    @field_validator("whitelist")
    @classmethod
    def make_whitelist_lowercase(cls, v: list[str]) -> list[str]:
        """Привести все слова в нижний регистр."""
        return [word.strip().lower() for word in v]

    @override
    def satisfies(self, green_label_item: GreenLabelItem) -> bool:
        title = green_label_item.title.lower()
        return any(word in title for word in self.whitelist)

    def generate_name(self) -> str:
        return f"Белый список ({','.join(self.whitelist)})"


class TitleBlackListFilter(BaseFilter):
    """
    Ни одно из слов из черного списка не должно быть в наименовании товара с зелённым ценником.
    """

    filter_type: Literal[FilterType.title_blacklist] = FilterType.title_blacklist
    blacklist: list[str]

    @field_validator("blacklist")
    @classmethod
    def make_blacklist_lowercase(cls, v: list[str]) -> list[str]:
        """Привести все слова в нижний регистр."""
        return [word.strip().lower() for word in v]

    @override
    def satisfies(self, green_label_item: GreenLabelItem) -> bool:
        title = green_label_item.title.lower()
        return not any(word in title for word in self.blacklist)

    def generate_name(self) -> str:
        return f"Черный список ({','.join(self.blacklist)})"


GreenLabelsFilter = Annotated[
    TitleWhiteListFilter | TitleBlackListFilter, pydantic.Field(discriminator="filter_type")
]
