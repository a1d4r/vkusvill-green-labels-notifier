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

    async def get_user_address(self, telegram_user: TelegramUser) -> AddressInfo | None:
        user = await self.user_repository.get_user_by_telegram_id(telegram_user.id)
        if not user:
            return None
        return AddressInfo(
            address=user.settings.address,
            latitude=user.settings.address_latitude,
            longitude=user.settings.address_longitude,
        )

    async def get_user_notifications_settings(self, telegram_user: TelegramUser) -> bool:
        user = await self.user_repository.get_user_by_telegram_id(telegram_user.id)
        if not user:
            return False
        return user.settings.enable_notifications

    async def update_user_notifications_settings(
        self, telegram_user: TelegramUser, enable: bool
    ) -> None:
        user = await self.user_repository.get_user_by_telegram_id(telegram_user.id)
        if not user:
            return
        user.settings.enable_notifications = enable
        await self.user_repository.update_user(user)

    async def save_address_for_user(
        self, telegram_user: TelegramUser, address_info: AddressInfo
    ) -> None:
        logger.info("Saving address for user {}: {}", telegram_user.id, address_info)
        user = await self.user_repository.get_user_by_telegram_id(telegram_user.id)
        if not user:
            logger.info("Creating new user {}", telegram_user.id)
            user_settings = UserSettings(
                address_latitude=address_info.latitude,
                address_longitude=address_info.longitude,
                address=address_info.address,
            )
            location = Location(
                latitude=address_info.latitude,
                longitude=address_info.longitude,
                address=address_info.address,
            )
            user_settings.locations.append(location)
            user = User(
                tg_id=telegram_user.id,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                username=telegram_user.username,
                settings=user_settings,
            )
            await self.user_repository.add_user(user)
            logger.info("Created new user {}", telegram_user.id)
        else:
            user.settings.address = address_info.address
            user.settings.address_latitude = address_info.latitude
            user.settings.address_longitude = address_info.longitude
            user.settings.vkusvill_settings = None
            flag_modified(user.settings, "vkusvill_settings")
            if user.settings.locations:
                location = user.settings.locations[0]
                location.latitude = address_info.latitude
                location.longitude = address_info.longitude
                location.address = address_info.address
                flag_modified(user.settings, "locations")
            await self.user_repository.update_user(user)
            logger.info("Updated address for user {}", telegram_user.id)
        logger.info("Saved address for user {}", telegram_user.id)
        logger.debug(
            "User coordinates in DB: ({}, {})",
            user.settings.address_latitude,
            user.settings.address_longitude,
        )
