from dataclasses import dataclass

from aiogram.types import User as TelegramUser
from loguru import logger
from sqlalchemy.orm.attributes import flag_modified

from vkusvill_green_labels.models.db import Location, User, UserSettings
from vkusvill_green_labels.models.vkusvill import AddressInfo
from vkusvill_green_labels.repositories.user import UserRepository


@dataclass
class UserService:
    user_repository: UserRepository

    async def get_or_create_user(self, telegram_user: TelegramUser) -> User:
        user = await self.user_repository.get_user_by_telegram_id(telegram_user.id)
        if not user:
            user = User(
                tg_id=telegram_user.id,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                username=telegram_user.username,
                settings=UserSettings(locations=[]),
            )
            await self.user_repository.add_user(user)
            logger.info("Created new user: {}", user.tg_id)
        return user

    async def get_user_location(self, telegram_user: TelegramUser) -> Location | None:
        user = await self.get_or_create_user(telegram_user)
        if not user.settings.locations:
            return None
        return user.settings.locations[0]

    async def get_user_notifications_settings(self, telegram_user: TelegramUser) -> bool:
        user = await self.get_or_create_user(telegram_user)
        return user.settings.enable_notifications

    async def update_user_notifications_settings(
        self, telegram_user: TelegramUser, enable: bool
    ) -> None:
        user = await self.get_or_create_user(telegram_user)
        user.settings.enable_notifications = enable
        await self.user_repository.update_user(user)

    async def save_location_for_user(
        self, telegram_user: TelegramUser, address_info: AddressInfo
    ) -> None:
        logger.info("Saving location for user {}: {}", telegram_user.id, address_info)
        user = await self.get_or_create_user(telegram_user)
        user.settings.locations = [
            Location(
                latitude=address_info.latitude,
                longitude=address_info.longitude,
                address=address_info.address,
            )
        ]
        # After changing address we should create new Vkusvill account and set new address
        user.settings.vkusvill_settings = None
        flag_modified(user.settings, "vkusvill_settings")
        await self.user_repository.update_user(user)
        logger.info("Saved location for user {}: {}", telegram_user.id, user.settings.locations[0])
