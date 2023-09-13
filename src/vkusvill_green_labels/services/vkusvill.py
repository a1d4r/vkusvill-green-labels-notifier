import typing

import requests
from loguru import logger

from vkusvill_green_labels.settings import VkusvillSettings

SHOP_ID = 5266  # TODO: Move to settings
GREEN_LABELS_ENDPOINT = ""


class VkusvillApiError(Exception):
    pass


class VkusvillApi:
    BONUS_CARD_NUMBER = "&832893"

    def __init__(self, settings: VkusvillSettings) -> None:
        self.settings = settings

    def fetch_green_labels(self, shop_id: int) -> list[typing.Any]:
        params: dict[str, str | int] = {
            "shop_id": shop_id,
            "number": self.BONUS_CARD_NUMBER,
        }  # Идентификатор магазина
        response = requests.get(
            str(self.settings.green_labels_endpoint), params=params, headers=self.settings.headers
        )
        logger.debug(response.request.headers)
        logger.debug(response.request.url)

        assert (
            response.request.url
            == "https://mobile.vkusvill.ru/api/takeaway/getGreenLabelsShop?shop_id=5266&number=%26832893"
        )

        if response.status_code != 200:
            try:
                response_body = response.json()
            except requests.JSONDecodeError:
                response_body = response.text
            logger.error(
                "Vkusvill API bad response: status_code={}, response={}",
                response.status_code,
                response_body,
            )
            msg = f"Response with status_code={response.status_code}"
            raise VkusvillApiError(msg)

        return response.json()["payload"]


if __name__ == "__main__":
    from vkusvill_green_labels.settings import settings

    vkusvill = VkusvillApi(settings.vkusvill)
    logger.info(vkusvill.fetch_green_labels(SHOP_ID))
