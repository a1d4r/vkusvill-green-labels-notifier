from dataclasses import dataclass

import httpx

from loguru import logger
from sqlalchemy.orm.attributes import flag_modified

from vkusvill_green_labels.core.settings import settings
from vkusvill_green_labels.models import User
from vkusvill_green_labels.repositories.green_labels import GreenLabelsRepository
from vkusvill_green_labels.repositories.user import UserRepository
from vkusvill_green_labels.services.notification_service import NotificationService
from vkusvill_green_labels.services.vkusvill_api import GreenLabelItem, VkusvillApi


@dataclass
class UpdaterService:
    green_labels_repo: GreenLabelsRepository
    user_repo: UserRepository
    notification_service: NotificationService

    async def update_green_labels(self) -> None:
        users = await self.user_repo.get_users_for_notifications()
        if not users:
            logger.info("No users found for notifications")
            return
        for user in users:
            new_green_labels = await self.fetch_new_green_labels_for_user(user)
            if not new_green_labels:
                continue
            try:
                await self.notification_service.notify_about_new_green_labels(
                    user, new_green_labels
                )
            except Exception:  # noqa: BLE001
                logger.exception("Failed to send notification to user {}", user.tg_id)

    async def fetch_new_green_labels_for_user(self, user: User) -> list[GreenLabelItem]:
        logger.info("Fetching new green labels for user {}", user.tg_id)
        if user.settings.vkusvill_settings is None:
            async with httpx.AsyncClient() as client:
                vkusvill_api = VkusvillApi(client, settings.vkusvill)
                await vkusvill_api.authorize()
                await vkusvill_api.update_cart(
                    user.settings.address_latitude, user.settings.address_longitude
                )
                user.settings.vkusvill_settings = vkusvill_api.user_settings
                flag_modified(user.settings, "vkusvill_settings")
                await self.user_repo.update_user(user)
        async with httpx.AsyncClient() as client:
            assert user.settings.vkusvill_settings is not None  # noqa: S101
            vkusvill_api = VkusvillApi(client, settings.vkusvill, user.settings.vkusvill_settings)
            current_green_labels = await vkusvill_api.fetch_green_labels()
        previous_green_labels = await self.green_labels_repo.get_items(user.id)
        new_green_labels = self._get_items_difference(current_green_labels, previous_green_labels)
        await self.green_labels_repo.set_items(user.id, current_green_labels)
        logger.info("Fetched {} new green labels for user {}", len(new_green_labels), user.tg_id)
        return new_green_labels

    @staticmethod
    def _get_items_difference(
        new_items: list[GreenLabelItem], old_items: list[GreenLabelItem]
    ) -> list[GreenLabelItem]:
        """Return green label items which only appears in `new_items` list."""
        old_item_ids = {item.item_id for item in old_items}
        return [item for item in new_items if item.item_id not in old_item_ids]
