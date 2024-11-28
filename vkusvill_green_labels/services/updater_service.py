from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import httpx

from aiogram.exceptions import TelegramForbiddenError
from loguru import logger
from sqlalchemy.orm.attributes import flag_modified

from vkusvill_green_labels.core.settings import settings
from vkusvill_green_labels.models.db import User
from vkusvill_green_labels.models.vkusvill import GreenLabelItem
from vkusvill_green_labels.repositories.green_labels import GreenLabelsRepository
from vkusvill_green_labels.repositories.user import UserRepository
from vkusvill_green_labels.services.notification_service import NotificationService
from vkusvill_green_labels.services.vkusvill_api import VkusvillApi


@dataclass
class UpdaterService:
    green_labels_repo: GreenLabelsRepository
    user_repo: UserRepository
    notification_service: NotificationService

    async def update_green_labels(self) -> None:
        """Обновить товары с зелёными ценниками для активных пользователей."""
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
            except TelegramForbiddenError:
                logger.info("User {} has blocked the bot. Disabling notifications.", user.tg_id)
                user.settings.enable_notifications = False
                await self.user_repo.update_user(user)
            except Exception:  # noqa: BLE001
                logger.exception("Failed to send notification to user {}", user.tg_id)

    async def fetch_new_green_labels_for_user(self, user: User) -> list[GreenLabelItem]:
        """Получить новые товары с зелеными ценники для заданного пользователя."""
        logger.info("Fetching new green labels for user {}", user.tg_id)
        if not user.settings.locations:
            logger.warning("No locations found for user {}", user.tg_id)
            return []
        location = user.settings.locations[0]
        if self._need_to_authorize(user):
            async with httpx.AsyncClient() as client:
                vkusvill_api = VkusvillApi(client, settings.vkusvill)
                await vkusvill_api.authorize()
                await vkusvill_api.update_cart(
                    latitude=location.latitude, longitude=location.longitude
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
        filtered_green_labels = [
            green_label
            for green_label in new_green_labels
            if all(filter_.definition.satisfies(green_label) for filter_ in user.settings.filters)
        ]
        logger.info(
            "Filtered {} new green labels for user {}", len(filtered_green_labels), user.tg_id
        )
        return filtered_green_labels

    def _need_to_authorize(self, user: User) -> bool:
        """Проверяет необходимость авторизации пользователя."""
        if not user.settings.vkusvill_settings:
            return True
        # Если токен протух, то нужно также переавторизовать пользователя
        # поскольку API не выдаёт ошибку в этом случае
        token_expiration_date = user.settings.vkusvill_settings.created_at + timedelta(
            seconds=settings.vkusvill.token_lifetime_seconds
        )
        return token_expiration_date < datetime.now(UTC)

    @staticmethod
    def _get_items_difference(
        new_items: list[GreenLabelItem], old_items: list[GreenLabelItem]
    ) -> list[GreenLabelItem]:
        """Return green label items which only appears in `new_items` list."""
        old_item_ids = {item.item_id for item in old_items}
        return [item for item in new_items if item.item_id not in old_item_ids]
