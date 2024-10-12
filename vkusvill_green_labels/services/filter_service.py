from dataclasses import dataclass

from aiogram.types import User as TelegramUser

from vkusvill_green_labels.models.db import Filter
from vkusvill_green_labels.models.types import FilterID
from vkusvill_green_labels.repositories.filter import FilterRepository
from vkusvill_green_labels.services.user_service import UserService


@dataclass
class FilterService:
    user_service: UserService
    filter_repository: FilterRepository

    async def get_filter_by_telegram_user_and_id(
        self, telegram_user: TelegramUser, filter_id: FilterID
    ) -> Filter | None:
        user = await self.user_service.get_or_create_user(telegram_user)
        return await self.filter_repository.get_filter_by_user_and_id(user, filter_id)

    async def get_filters_by_telegram_user(self, telegram_user: TelegramUser) -> list[Filter]:
        user = await self.user_service.get_or_create_user(telegram_user)
        return user.settings.filters

    async def delete_filter_by_telegram_user_and_id(
        self, telegram_user: TelegramUser, filter_id: FilterID
    ) -> None:
        user = await self.user_service.get_or_create_user(telegram_user)
        await self.filter_repository.delete_filter_by_user_and_id(user, filter_id)
