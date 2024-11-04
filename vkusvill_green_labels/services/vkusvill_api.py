# ruff: noqa: ERA001
import typing

import asyncio
import decimal

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from json import JSONDecodeError
from time import time
from uuid import uuid4

import httpx

from loguru import logger
from pydantic import AliasPath, BaseModel, Field, HttpUrl, TypeAdapter, ValidationError
from pyrate_limiter import Limiter

from vkusvill_green_labels.core.settings import VkusvillSettings, settings
from vkusvill_green_labels.models.vkusvill import (
    AddressInfo,
    GreenLabelItem,
    TokenInfo,
    VkusvillUserSettings,
)


class VkusvillError(Exception):
    pass


class VkusvillApiError(VkusvillError):
    pass


class VkusvillValidationError(VkusvillError):
    pass


class VkusvillUnauthorizedError(VkusvillError):
    pass


class GreenLabelItemResponse(GreenLabelItem):
    item_id: int = Field(..., validation_alias="id")
    rating: str = Field(..., validation_alias=AliasPath("rating", "all"))
    price: Decimal = Field(..., validation_alias=AliasPath("price", "price"))
    discount_price: Decimal = Field(..., validation_alias=AliasPath("price", "discount_price"))
    weight_unit: str = Field(..., validation_alias="unit")


class ShopInfo(BaseModel):
    """Информация о магазине."""

    shop_number: int = Field(validation_alias="ShopNo")


class AddressInfoResponse(AddressInfo):
    res: int


class CartInfoResponse(BaseModel):
    """Информация о корзине."""

    cart_id: int
    message: str
    res: int


@dataclass
class VkusvillApi:
    client: httpx.AsyncClient
    settings: VkusvillSettings
    rate_limiter: Limiter | None = None
    user_settings: VkusvillUserSettings | None = None

    async def create_new_user_token(self, device_id: str | None = None) -> TokenInfo:
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

        response = await self._request(
            method="POST",
            url=self.settings.create_token.url,
            params=params,
            headers=self.settings.create_token.headers,
            timeout=self.settings.create_token.timeout,
        )

        try:
            return TokenInfo.model_validate(response.json())
        except (ValidationError, KeyError) as exc:
            raise VkusvillApiError("Could not validate response") from exc

    async def authorize(self) -> None:
        device_id = str(uuid4())
        user_token = await self.create_new_user_token(device_id)
        self.user_settings = VkusvillUserSettings(
            device_id=device_id, user_number=user_token.user_number, token=user_token.token
        )

    async def get_shop_info(
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

        response = await self._request(
            method="GET",
            url=self.settings.shop_info.url,
            params=params,
            headers=headers,
            timeout=self.settings.shop_info.timeout,
        )

        try:
            shop_info_list = TypeAdapter(list[ShopInfo]).validate_python(response.json())
            if not shop_info_list:
                return None
            return shop_info_list[0]
        except (ValidationError, KeyError) as exc:
            raise VkusvillApiError("Could not validate response") from exc

    async def get_address_info(
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

        response = await self._request(
            method="GET",
            url=self.settings.address_info.url,
            params=params,
            headers=headers,
            timeout=self.settings.address_info.timeout,
        )

        try:
            response_address_info = AddressInfoResponse.model_validate(response.json())
            if response_address_info.res < 0:
                return None
            address_info = AddressInfo.model_validate(response_address_info, from_attributes=True)
        except (ValidationError, KeyError) as exc:
            raise VkusvillApiError("Could not validate response") from exc
        else:
            return address_info

    async def update_cart(
        self, latitude: decimal.Decimal, longitude: decimal.Decimal
    ) -> CartInfoResponse | None:
        if self.user_settings is None:
            raise VkusvillUnauthorizedError("User settings are not provided")

        headers = self.settings.update_cart.headers.copy()
        headers["x-vkusvill-token"] = self.user_settings.token

        data: dict[str, typing.Any] = self.settings.update_cart.query.copy()
        data["number"] = self.user_settings.user_number
        data["DateSupply"] = datetime.now(UTC).strftime("%Y%m%d")
        data["coordinates"] = f"{latitude},{longitude}"

        response = await self._request(
            method="POST",
            url=self.settings.update_cart.url,
            data=data,
            headers=headers,
            timeout=self.settings.update_cart.timeout,
        )

        try:
            cart_info = CartInfoResponse.model_validate(response.json())
            if cart_info.res < 0:
                raise VkusvillApiError(f"Could not update cart: {cart_info.message}")
        except (ValidationError, KeyError) as exc:
            raise VkusvillApiError("Could not validate response") from exc
        else:
            return cart_info

    async def fetch_green_labels(self) -> list[GreenLabelItem]:
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
            response = await self._request(
                "GET",
                self.settings.green_labels.url,
                params=params,
                headers=headers,
                timeout=self.settings.green_labels.timeout,
            )

            try:
                response_items = TypeAdapter(list[GreenLabelItemResponse]).validate_python(
                    response.json()
                )
                items = TypeAdapter(list[GreenLabelItem]).validate_python(response_items)
            except (ValidationError, KeyError) as exc:
                raise VkusvillApiError("Could not validate response") from exc
            else:
                all_items.extend(items)
                if len(items) < limit:
                    break
                offset += limit
        return all_items

    async def _request(
        self,
        method: str,
        url: HttpUrl,
        params: dict[str, typing.Any] | None = None,
        data: dict[str, typing.Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 30,  # noqa: ASYNC109
    ) -> httpx.Response:
        if self.rate_limiter is not None:
            try:
                await self.rate_limiter.try_acquire(str(url))  # type: ignore[misc]
            except TypeError:
                logger.exception("Rate bucket expected to be async")
        response = await self.client.request(
            method=method, url=str(url), params=params, data=data, headers=headers, timeout=timeout
        )
        logger.debug(
            "{} {} - {} ", response.request.method, response.request.url, response.status_code
        )
        self._check_response_successful(response)
        return response

    def _check_response_successful(self, response: httpx.Response) -> None:
        if response.status_code != 200:
            try:
                response_body = response.json()
            except (JSONDecodeError, UnicodeDecodeError):
                response_body = response.text
            msg = f"Vkusvill API bad response: status_code={response.status_code}, response={response_body}"
            logger.exception(msg)
            raise VkusvillApiError(msg)


async def main() -> None:
    async with httpx.AsyncClient() as client:
        vkusvill_api = VkusvillApi(client, settings.vkusvill)
        await vkusvill_api.authorize()
        logger.info(vkusvill_api.user_settings)
        lat, lon = Decimal("55.7381250"), Decimal("37.6287290")
        shop_info = await vkusvill_api.get_shop_info(lat, lon)
        logger.info(shop_info)
        address_info = await vkusvill_api.get_address_info(lat, lon)
        logger.info(address_info)
        logger.info(await vkusvill_api.update_cart(lat, lon))
        green_labels_items = await vkusvill_api.fetch_green_labels()
        logger.info(len(green_labels_items))
        if green_labels_items:
            logger.info(green_labels_items[0])


if __name__ == "__main__":
    asyncio.run(main())
