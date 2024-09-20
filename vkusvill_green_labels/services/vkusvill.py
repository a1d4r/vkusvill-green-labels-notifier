# ruff: noqa: ERA001
import typing

import decimal

from datetime import UTC, datetime
from decimal import Decimal
from functools import partial
from json import JSONDecodeError
from time import time
from uuid import uuid4

import httpx

from loguru import logger
from pydantic import AliasPath, BaseModel, Field, TypeAdapter, ValidationError

from vkusvill_green_labels.settings import VkusvillSettings


class VkusvillError(Exception):
    pass


class VkusvillApiError(VkusvillError):
    pass


class VkusvillValidationError(VkusvillError):
    pass


class VkusvillUnauthorizedError(VkusvillError):
    pass


class VkusvillUserSettings(BaseModel):
    device_id: str
    user_number: str
    token: str
    created_at: datetime = Field(default_factory=partial(datetime.now, UTC))


class GreenLabelItem(BaseModel):
    item_id: int = Field(..., validation_alias="id")
    title: str
    amount: Decimal
    weight_str: str
    rating: str = Field(..., validation_alias=AliasPath("rating", "all"))
    price: Decimal = Field(..., validation_alias=AliasPath("price", "price"))
    discount_price: Decimal = Field(..., validation_alias=AliasPath("price", "discount_price"))


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


class CartInfo(BaseModel):
    """Информация о корзине."""

    cart_id: int
    message: str
    res: int


class VkusvillApi:
    _TIMEOUT = 3

    def __init__(
        self, settings: VkusvillSettings, user_settings: VkusvillUserSettings | None = None
    ) -> None:
        self.settings = settings
        self.user_settings = user_settings

    def create_new_user_token(self, device_id: str | None = None) -> TokenResponse:
        if device_id is None:
            device_id = str(uuid4())

        str_params = self.settings.create_token.str_params.copy()
        str_params["ts"] = str(int(time()))
        str_params["device_id"] = str(device_id)
        formatted_str_params = "".join(
            ["{[" + key + "]}" + "{[" + value + "]}" for key, value in str_params.items()]
        )

        params: dict[str, typing.Any] = self.settings.create_token.query.copy()
        params["device_id"] = device_id
        params["str_par"] = formatted_str_params

        response = httpx.post(
            str(self.settings.create_token.url),
            params=params,
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
            raise VkusvillApiError("Could not validate response") from exc

    def authorize(self) -> None:
        device_id = str(uuid4())
        user_token = self.create_new_user_token(device_id)
        self.user_settings = VkusvillUserSettings(
            device_id=device_id, user_number=user_token.user_number, token=user_token.token
        )

    def get_shop_info(
        self, latitude: decimal.Decimal, longitude: decimal.Decimal
    ) -> ShopInfo | None:
        if self.user_settings is None:
            raise VkusvillUnauthorizedError("User settings are not provided")

        headers = self.settings.shop_info.headers.copy()
        headers["x-vkusvill-token"] = self.user_settings.token

        params: dict[str, typing.Any] = self.settings.shop_info.query.copy()
        params["latitude"] = str(latitude)
        params["longitude"] = str(longitude)
        params["number"] = self.user_settings.user_number

        response = httpx.get(
            str(self.settings.shop_info.url), params=params, headers=headers, timeout=self._TIMEOUT
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
            raise VkusvillApiError("Could not validate response") from exc

    def get_address_info(
        self, latitude: decimal.Decimal, longitude: decimal.Decimal
    ) -> AddressInfo | None:
        if self.user_settings is None:
            raise VkusvillUnauthorizedError("User settings are not provided")

        headers = self.settings.address_info.headers.copy()
        headers["x-vkusvill-token"] = self.user_settings.token

        params: dict[str, typing.Any] = self.settings.address_info.query.copy()
        params["latitude"] = str(latitude)
        params["longitude"] = str(longitude)
        params["number"] = self.user_settings.user_number

        response = httpx.get(
            str(self.settings.address_info.url),
            params=params,
            headers=headers,
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
            raise VkusvillApiError("Could not validate response") from exc
        else:
            return address_info

    def update_cart(self, latitude: decimal.Decimal, longitude: decimal.Decimal) -> CartInfo | None:
        if self.user_settings is None:
            raise VkusvillUnauthorizedError("User settings are not provided")

        headers = self.settings.update_cart.headers.copy()
        headers["x-vkusvill-token"] = self.user_settings.token

        params: dict[str, typing.Any] = self.settings.update_cart.query.copy()
        params["number"] = self.user_settings.user_number
        params["DateSupply"] = datetime.now(UTC).strftime("%Y%m%d")
        params["coordinates"] = f"{latitude},{longitude}"

        response = httpx.post(
            str(self.settings.update_cart.url), data=params, headers=headers, timeout=self._TIMEOUT
        )
        logger.debug(
            "{} {} - {} ", response.request.method, response.request.url, response.status_code
        )
        self._check_response_successful(response)

        try:
            cart_info = CartInfo.model_validate(response.json())
            if cart_info.res < 0:
                raise VkusvillApiError(f"Could not update cart: {cart_info.message}")
        except (ValidationError, KeyError) as exc:
            raise VkusvillApiError("Could not validate response") from exc
        else:
            return cart_info

    def fetch_green_labels(self) -> list[GreenLabelItem]:
        if self.user_settings is None:
            raise VkusvillUnauthorizedError("User settings are not provided")

        headers = self.settings.green_labels.headers.copy()
        headers["x-vkusvill-token"] = self.user_settings.token

        params: dict[str, typing.Any] = self.settings.green_labels.query.copy()
        params["number"] = self.user_settings.user_number

        all_items = []
        offset = 0
        limit = 200
        while True:
            params["offset"] = offset
            params["limit"] = limit
            response = httpx.get(
                str(self.settings.green_labels.url),
                params=params,
                headers=headers,
                timeout=self._TIMEOUT,
            )
            logger.debug(
                "{} {} - {} ", response.request.method, response.request.url, response.status_code
            )
            self._check_response_successful(response)

            try:
                items = TypeAdapter(list[GreenLabelItem]).validate_python(response.json())
            except (ValidationError, KeyError) as exc:
                raise VkusvillApiError("Could not validate response") from exc
            else:
                all_items.extend(items)
                if len(items) < limit:
                    break
                offset += limit
        return all_items

    def _check_response_successful(self, response: httpx.Response) -> None:
        if response.status_code != 200:
            try:
                response_body = response.json()
            except (JSONDecodeError, UnicodeDecodeError):
                response_body = response.text
            msg = f"Vkusvill API bad response: status_code={response.status_code}, response={response_body}"
            logger.exception(msg)
            raise VkusvillApiError(msg)


if __name__ == "__main__":
    from vkusvill_green_labels.settings import settings

    vkusvill = VkusvillApi(settings.vkusvill)
    vkusvill.authorize()
    logger.info(vkusvill.user_settings)
    lat, lon = Decimal("55.7381250"), Decimal("37.6287290")
    shop_info = vkusvill.get_shop_info(lat, lon)
    logger.info(shop_info)
    address_info = vkusvill.get_address_info(lat, lon)
    logger.info(address_info)
    logger.info(vkusvill.update_cart(lat, lon))
    green_labels_items = vkusvill.fetch_green_labels()
    logger.info(len(green_labels_items))
    logger.info(green_labels_items[0])
