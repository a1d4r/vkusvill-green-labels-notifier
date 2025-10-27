from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum, auto
from functools import partial

from pydantic import BaseModel, Field

from vkusvill_green_labels.models.types import Latitude, Longitude


class NotificationType(StrEnum):
    """Тип уведомлений."""

    detailed = auto()  # Подробные уведомления с описанием товаров
    only_quantity = auto()  # Только количество товаров
    only_increase = auto()  # Уведомления только об увеличении количества товаров


class VkusvillUserSettings(BaseModel):
    device_id: str
    user_number: str
    token: str
    created_at: datetime = Field(default_factory=partial(datetime.now, UTC))


class GreenLabelItem(BaseModel):
    """Информация о товаре с зеленым ценником."""

    item_id: int
    title: str
    amount: Decimal
    weight_str: str
    weight_type: str = ""
    weight_unit: str = ""
    rating: str
    price: Decimal
    discount_price: Decimal

    @property
    def available_display_string(self) -> str:
        """Отображаемое доступное количество товара."""
        return f"{self.amount} {self.weight_unit}"

    @property
    def title_display_string(self) -> str:
        """Отображаемое название."""
        return self.title.removesuffix(", " + self.weight_str)


class TokenInfo(BaseModel):
    """Информация о токене и пользователе."""

    email: str
    fullname: str
    user_number: str = Field(validation_alias="number")
    phone: str
    token: str


class AddressInfo(BaseModel):
    """Информация об адресе."""

    latitude: Latitude
    longitude: Longitude
    address: str
