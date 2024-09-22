from typing import ClassVar

from dataclasses import dataclass
from decimal import Decimal

from vkusvill_green_labels.services.vkusvill_api import VkusvillApi, VkusvillUserSettings


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

    async def get_address_by_location(self, latitude: Decimal, longitude: Decimal) -> str | None:
        address_info = await self.vkusvill_api.get_address_info(latitude, longitude)
        if not address_info:
            return None
        return address_info.address
