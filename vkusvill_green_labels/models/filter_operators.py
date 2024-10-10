from typing import Annotated, Literal, override

from abc import abstractmethod

import pydantic

from pydantic import BaseModel, Field, TypeAdapter, field_validator

from vkusvill_green_labels.models.vkusvill import GreenLabelItem


class FilterOperatorBase(BaseModel):
    operator: str

    @abstractmethod
    def satisfies(self, green_label_item: GreenLabelItem) -> bool: ...


class AndOperator(FilterOperatorBase):
    operator: Literal["and"] = "and"
    operands: list[FilterOperatorBase] = Field(..., min_length=1)

    @override
    def satisfies(self, green_label_item: GreenLabelItem) -> bool:
        return all(operand.satisfies(green_label_item) for operand in self.operands)


class TitleWhiteListOperator(FilterOperatorBase):
    """
    At least one word from `whitelist` must be in `green_label_item.title`.
    """

    operator: Literal["name_whitelist"] = "name_whitelist"
    whitelist: list[str]

    @field_validator("whitelist")
    @classmethod
    def make_whitelist_lowercase(cls, v: list[str]) -> list[str]:
        """Convert all words to lowercase."""
        return [word.lower() for word in v]

    @override
    def satisfies(self, green_label_item: GreenLabelItem) -> bool:
        title = green_label_item.title.lower()
        return any(word in title for word in self.whitelist)


class TitleBlackListOperator(FilterOperatorBase):
    """
    None of the words from `blacklist` must be in `green_label_item.title`.
    """

    operator: Literal["name_blacklist"] = "name_blacklist"
    blacklist: list[str]

    @field_validator("blacklist")
    @classmethod
    def make_blacklist_lowercase(cls, v: list[str]) -> list[str]:
        """Convert all words to lowercase."""
        return [word.lower() for word in v]

    @override
    def satisfies(self, green_label_item: GreenLabelItem) -> bool:
        title = green_label_item.title.lower()
        return not any(word in title for word in self.blacklist)


GreenLabelsFilterOperator = Annotated[
    AndOperator | TitleWhiteListOperator | TitleBlackListOperator,
    pydantic.Field(discriminator="operator"),
]
green_labels_filter_adapter: TypeAdapter[GreenLabelsFilterOperator] = TypeAdapter(
    GreenLabelsFilterOperator
)
