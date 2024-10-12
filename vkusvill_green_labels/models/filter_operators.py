from typing import Annotated, Literal, override

from abc import abstractmethod

import pydantic

from pydantic import BaseModel, TypeAdapter, field_validator

from vkusvill_green_labels.models.vkusvill import GreenLabelItem


class FilterOperatorBase(BaseModel):
    operator: str

    @abstractmethod
    def satisfies(self, green_label_item: GreenLabelItem) -> bool: ...


class TitleWhiteListOperator(FilterOperatorBase):
    """
    Как минимум одно слово из белого списка должно быть в наименовании товара с зелённым ценником.
    """

    operator: Literal["name_whitelist"] = "name_whitelist"
    whitelist: list[str]

    @field_validator("whitelist")
    @classmethod
    def make_whitelist_lowercase(cls, v: list[str]) -> list[str]:
        """Привести все слова в нижний регистр."""
        return [word.lower() for word in v]

    @override
    def satisfies(self, green_label_item: GreenLabelItem) -> bool:
        title = green_label_item.title.lower()
        return any(word in title for word in self.whitelist)


class TitleBlackListOperator(FilterOperatorBase):
    """
    Ни одно из слов из черного списка не должно быть в наименовании товара с зелённым ценником.
    """

    operator: Literal["name_blacklist"] = "name_blacklist"
    blacklist: list[str]

    @field_validator("blacklist")
    @classmethod
    def make_blacklist_lowercase(cls, v: list[str]) -> list[str]:
        """Привести все слова в нижний регистр."""
        return [word.lower() for word in v]

    @override
    def satisfies(self, green_label_item: GreenLabelItem) -> bool:
        title = green_label_item.title.lower()
        return not any(word in title for word in self.blacklist)


GreenLabelsFilterOperator = Annotated[
    TitleWhiteListOperator | TitleBlackListOperator, pydantic.Field(discriminator="operator")
]
green_labels_filter_adapter: TypeAdapter[GreenLabelsFilterOperator] = TypeAdapter(
    GreenLabelsFilterOperator
)
