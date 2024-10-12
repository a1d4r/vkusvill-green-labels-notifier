import pytest

from aiogram.types import User as TelegramUser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import LocationFactory, UserFactory
from vkusvill_green_labels.models.db import User
from vkusvill_green_labels.models.vkusvill import AddressInfo
from vkusvill_green_labels.services.user_service import UserService


@pytest.fixture
async def user_with_location_in_db(test_session: AsyncSession, telegram_user: TelegramUser) -> User:
    user = UserFactory.build(
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name,
        username=telegram_user.username,
        tg_id=telegram_user.id,
    )
    user.settings.locations = [LocationFactory.build()]
    test_session.add(user)
    await test_session.commit()
    return user


async def test_get_user_location(
    user_service: UserService, telegram_user: TelegramUser, user_with_location_in_db: User
):
    # Act
    location = await user_service.get_user_location(telegram_user)

    # Assert
    assert location is not None
    assert location.to_dict() == user_with_location_in_db.settings.locations[0].to_dict()


async def test_save_location_for_new_user(
    user_service: UserService,
    telegram_user: TelegramUser,
    address_info: AddressInfo,
    test_session: AsyncSession,
):
    # Act
    await user_service.save_location_for_user(telegram_user, address_info)

    # Assert
    user = await test_session.scalar(select(User, User.tg_id == telegram_user.id))
    assert user.first_name == telegram_user.first_name
    assert user.last_name == telegram_user.last_name
    assert user.username == telegram_user.username
    assert len(user.settings.locations) == 1
    assert user.settings.locations[0].address == address_info.address
    assert user.settings.locations[0].latitude == address_info.latitude
    assert user.settings.locations[0].longitude == address_info.longitude


async def test_save_new_location_for_existing_user(
    user_service: UserService,
    test_session: AsyncSession,
    telegram_user: TelegramUser,
    address_info: AddressInfo,
    user_with_location_in_db: User,
):
    # Act
    await user_service.save_location_for_user(telegram_user, address_info)

    # Assert
    await test_session.refresh(user_with_location_in_db)
    assert len(user_with_location_in_db.settings.locations) == 1
    assert user_with_location_in_db.settings.locations[0].address == address_info.address
    assert user_with_location_in_db.settings.locations[0].latitude == address_info.latitude
    assert user_with_location_in_db.settings.locations[0].longitude == address_info.longitude
