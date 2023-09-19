import decimal

import pydantic
import requests
from loguru import logger

from vkusvill_green_labels.settings import VkusvillSettings
from vkusvill_green_labels.validators import MoscowDatetime

SHOP_ID = 5266  # TODO: Move to settings


class VkusvillError(Exception):
    pass


class VkusvillApiError(VkusvillError):
    pass


class VkusvillValidationError(VkusvillError):
    pass


class GreenLabelItem(pydantic.BaseModel):
    shop_id: int = pydantic.Field(validation_alias="shop_no")
    item_id: int = pydantic.Field(validation_alias="id_tov")
    name: str = pydantic.Field(validation_alias="Name_tov")
    rating: str | None = None
    photo_url: pydantic.HttpUrl | None = pydantic.Field(
        default=None,
        validation_alias="mini_photo_url",
    )
    timestamp: MoscowDatetime = pydantic.Field(validation_alias="ex_date")
    unit_of_measurement: str = pydantic.Field(validation_alias="ed_izm")
    weight: decimal.Decimal = pydantic.Field(validation_alias="ves")
    discount_percents: decimal.Decimal = pydantic.Field(validation_alias="discount")
    units_available: decimal.Decimal = pydantic.Field(validation_alias="ost")
    price: decimal.Decimal
    price_discount: decimal.Decimal = pydantic.Field(validation_alias="price_spec")


class VkusvillApi:
    BONUS_CARD_NUMBER = "&832893"
    _TIMEOUT = 3

    def __init__(self, settings: VkusvillSettings) -> None:
        self.settings = settings

    def fetch_green_labels(self, shop_id: int) -> list[GreenLabelItem]:
        params: dict[str, str | int] = {
            "shop_id": shop_id,
            "number": self.BONUS_CARD_NUMBER,
        }
        response = requests.get(
            str(self.settings.green_labels_endpoint),
            params=params,
            headers=self.settings.headers,
            timeout=self._TIMEOUT,
        )
        logger.debug(response.request.headers)
        logger.debug(response.request.url)

        if response.status_code != 200:
            try:
                response_body = response.json()
            except requests.JSONDecodeError:
                response_body = response.text
            msg = f"Vkusvill API bad response: status_code={response.status_code}, response={response_body}"
            logger.exception(msg)
            raise VkusvillApiError(msg)

        try:
            return pydantic.TypeAdapter(list[GreenLabelItem]).validate_python(
                response.json()["payload"],
            )
        except (pydantic.ValidationError, KeyError) as exc:
            msg = f"Could not validate payload: {exc}"
            logger.exception(msg)
            raise VkusvillApiError(msg) from exc


if __name__ == "__main__":
    from vkusvill_green_labels.settings import settings

    vkusvill = VkusvillApi(settings.vkusvill)
    logger.info(vkusvill.fetch_green_labels(SHOP_ID))
