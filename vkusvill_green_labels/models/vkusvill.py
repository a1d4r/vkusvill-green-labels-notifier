from datetime import UTC, datetime
from decimal import Decimal
from functools import partial

from pydantic import BaseModel, Field

from vkusvill_green_labels.models.types import Latitude, Longitude


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
    rating: str
    price: Decimal
    discount_price: Decimal


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
    res: int
