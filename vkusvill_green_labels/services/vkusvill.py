# ruff: noqa: ERA001
import typing

import decimal

from datetime import UTC, datetime
from decimal import Decimal
from functools import partial
from time import time
from uuid import uuid4

import requests

from loguru import logger
from pydantic import BaseModel, Field, HttpUrl, TypeAdapter, ValidationError

from vkusvill_green_labels.settings import VkusvillSettings
from vkusvill_green_labels.validators import MoscowDatetime


class VkusvillError(Exception):
    pass


class VkusvillApiError(VkusvillError):
    pass


class VkusvillValidationError(VkusvillError):
    pass


class VkusvillUserSettings(BaseModel):
    device_id: str
    user_number: str
    token: str
    created_at: datetime = Field(default_factory=partial(datetime.now, UTC))


class GreenLabelItem(BaseModel):
    shop_id: int = Field(validation_alias="shop_no")
    item_id: int = Field(validation_alias="id_tov")
    name: str = Field(validation_alias="Name_tov")
    rating: str | None = None
    photo_url: HttpUrl | None = Field(default=None, validation_alias="mini_photo_url")
    timestamp: MoscowDatetime = Field(validation_alias="ex_date")
    unit_of_measurement: str = Field(validation_alias="ed_izm")
    weight: decimal.Decimal = Field(validation_alias="ves")
    discount_percents: decimal.Decimal = Field(validation_alias="discount")
    units_available: decimal.Decimal = Field(validation_alias="ost")
    price: decimal.Decimal
    price_discount: decimal.Decimal = Field(validation_alias="price_spec")


class TokenResponse(BaseModel):
    """Информация о токене и пользователе."""

    email: str
    fullname: str
    user_number: str = Field(validation_alias="number")
    phone: str
    token: str


class ShopInfo(BaseModel):
    """Информация о магазине."""

    shop_number: int = Field(validation_alias="ShopNo")


class AddressInfo(BaseModel):
    """Информация об адресе."""

    latitude: Decimal
    longitude: Decimal
    address: str
    res: int


class VkusvillApi:
    BONUS_CARD_NUMBER = "&832893"
    _TIMEOUT = 3

    def __init__(
        self, settings: VkusvillSettings, user_settings: VkusvillUserSettings | None = None
    ) -> None:
        self.settings = settings
        self.user_settings = user_settings

    def fetch_green_labels(self, shop_id: int) -> list[GreenLabelItem]:
        params: dict[str, typing.Any] = self.settings.green_labels.query
        params |= {"shop_id": shop_id, "number": self.BONUS_CARD_NUMBER}
        response = requests.get(
            str(self.settings.green_labels.url),
            params=params,
            headers=self.settings.green_labels.headers,
            timeout=self._TIMEOUT,
        )
        logger.debug(
            "{} {} - {} ", response.request.method, response.request.url, response.status_code
        )
        self._check_response_successful(response)

        try:
            return TypeAdapter(list[GreenLabelItem]).validate_python(response.json()["payload"])
        except (ValidationError, KeyError) as exc:
            msg = f"Could not validate payload: {exc}"
            logger.exception(msg)
            raise VkusvillApiError(msg) from exc

    def create_new_user_token(self, device_id: str | None = None) -> TokenResponse:
        if device_id is None:
            device_id = str(uuid4())

        str_params = self.settings.create_token.str_params
        str_params["ts"] = str(int(time()))
        str_params["device_id"] = str(device_id)
        formatted_str_params = "".join(
            ["{[" + key + "]}" + "{[" + value + "]}" for key, value in str_params.items()]
        )

        params: dict[str, typing.Any] = self.settings.create_token.query
        params |= {"device_id": str(device_id), "str_param": formatted_str_params}

        response = requests.post(
            str(self.settings.create_token.url),
            params=self.settings.create_token.query,
            headers=self.settings.create_token.headers,
            timeout=self._TIMEOUT,
        )
        logger.debug(
            "{} {} - {} ", response.request.method, response.request.url, response.status_code
        )
        self._check_response_successful(response)

        try:
            return TokenResponse.model_validate(response.json())
        except (ValidationError, KeyError) as exc:
            msg = f"Could not validate payload: {exc}"
            logger.exception(msg)
            raise VkusvillApiError(msg) from exc

    def authorize(self) -> None:
        device_id = str(uuid4())
        user_token = self.create_new_user_token(device_id)
        self.user_settings = VkusvillUserSettings(
            device_id=device_id, user_number=user_token.user_number, token=user_token.token
        )

    def get_shop_info(
        self, latitude: decimal.Decimal, longitude: decimal.Decimal
    ) -> ShopInfo | None:
        params: dict[str, typing.Any] = self.settings.shop_info.query
        params |= {"latitude": str(latitude), "longitude": str(longitude)}
        response = requests.get(
            str(self.settings.shop_info.url),
            params=self.settings.shop_info.query,
            headers=self.settings.shop_info.headers,
            timeout=self._TIMEOUT,
        )
        logger.debug(
            "{} {} - {} ", response.request.method, response.request.url, response.status_code
        )
        self._check_response_successful(response)

        try:
            shop_info_list = TypeAdapter(list[ShopInfo]).validate_python(response.json())
            if not shop_info_list:
                return None
            return shop_info_list[0]
        except (ValidationError, KeyError) as exc:
            msg = f"Could not validate payload: {exc}"
            logger.exception(msg)
            raise VkusvillApiError(msg) from exc

    def get_address_info(
        self, latitude: decimal.Decimal, longitude: decimal.Decimal
    ) -> AddressInfo | None:
        params: dict[str, typing.Any] = self.settings.address_info.query
        params |= {"latitude": str(latitude), "longitude": str(longitude)}
        response = requests.get(
            str(self.settings.address_info.url),
            params=self.settings.address_info.query,
            headers=self.settings.address_info.headers,
            timeout=self._TIMEOUT,
        )
        logger.debug(
            "{} {} - {} ", response.request.method, response.request.url, response.status_code
        )
        self._check_response_successful(response)

        try:
            address_info = AddressInfo.model_validate(response.json())
            if address_info.res < 0:
                return None
        except (ValidationError, KeyError) as exc:
            msg = f"Could not validate payload: {exc}"
            logger.exception(msg)
            raise VkusvillApiError(msg) from exc
        else:
            return address_info

    def _check_response_successful(self, response: requests.Response) -> None:
        if response.status_code != 200:
            try:
                response_body = response.json()
            except requests.JSONDecodeError:
                response_body = response.text
            msg = f"Vkusvill API bad response: status_code={response.status_code}, response={response_body}"
            logger.exception(msg)
            raise VkusvillApiError(msg)


if __name__ == "__main__":
    from vkusvill_green_labels.settings import settings

    vkusvill = VkusvillApi(settings.vkusvill)
    # logger.info(vkusvill.create_new_user_token())
    vkusvill.authorize()
    logger.info(vkusvill.user_settings)
    # logger.info(vkusvill.fetch_green_labels(5266))
    # logger.info(vkusvill.get_shop_info(Decimal("55.7267300"), Decimal("37.6221450")))
    # logger.info(vkusvill.get_address_info(Decimal("55.7267300"), Decimal("37.6221450")))
