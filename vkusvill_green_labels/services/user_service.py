from dataclasses import dataclass
from decimal import Decimal

from aiogram.types import User as TelegramUser
from loguru import logger
from sqlalchemy.orm.attributes import flag_modified

from vkusvill_green_labels.models import User, UserSettings
from vkusvill_green_labels.repositories.user import UserRepository


@dataclass
class UserService:
    user_repository: UserRepository

    async def save_address_for_user(
        self, telegram_user: TelegramUser, address: str, latitude: Decimal, longitude: Decimal
    ) -> None:
        logger.info("Saving address for user {}", telegram_user.id)
        user = await self.user_repository.get_user_by_telegram_id(telegram_user.id)
        if not user:
            logger.info("Creating new user {}", telegram_user.id)
            user_settings = UserSettings(
                address_latitude=latitude, address_longitude=longitude, address=address
            )
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
            user.settings.address = address
            user.settings.address_latitude = latitude
            user.settings.address_longitude = longitude
            user.settings.vkusvill_settings = None
            flag_modified(user.settings, "vkusvill_settings")
            await self.user_repository.update_user(user)
            logger.info("Updated address for user {}", telegram_user.id)
        logger.info("Saved address for user {}", telegram_user.id)
