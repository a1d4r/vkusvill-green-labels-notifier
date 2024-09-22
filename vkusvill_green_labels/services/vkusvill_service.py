from typing import ClassVar

from dataclasses import dataclass
from decimal import Decimal

from vkusvill_green_labels.services.vkusvill_api import (
    AddressInfo,
    VkusvillApi,
    VkusvillUserSettings,
)


@dataclass
class VkusvillService:
    vkusvill_api: VkusvillApi
    base_user_settings: ClassVar[VkusvillUserSettings | None] = None

    async def authorize_with_base_user(self) -> None:
        if self.base_user_settings is None:
            await self.vkusvill_api.authorize()
            VkusvillService.base_user_settings = self.vkusvill_api.user_settings
        else:
            self.vkusvill_api.user_settings = self.base_user_settings

    async def get_address_info_by_location(
        self, latitude: float, longitude: float
    ) -> AddressInfo | None:
        decimal_latitude = Decimal(latitude).quantize(Decimal("0.0000001"))
        decimal_longitude = Decimal(longitude).quantize(Decimal("0.0000001"))
        return await self.vkusvill_api.get_address_info(decimal_latitude, decimal_longitude)
