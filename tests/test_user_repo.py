from decimal import Decimal

import pytest

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from vkusvill_green_labels.models.db import User, UserSettings
from vkusvill_green_labels.models.vkusvill import VkusvillUserSettings
from vkusvill_green_labels.repositories.user import UserRepository


@pytest.fixture
async def user_repo(session: AsyncSession) -> UserRepository:
    return UserRepository(session)


@pytest.fixture
async def user(session: AsyncSession) -> User:
    user = User(tg_id=1)
    session.add(user)
    await session.commit()
    return user


@pytest.fixture
async def user_with_settings(session: AsyncSession) -> User:
    user = User(tg_id=1)
    vkusvill_user_settings = VkusvillUserSettings(
        device_id="device_id", user_number="1", token="token"
    )
    user_settings = UserSettings(
        address_latitude=Decimal("11.11"),
        address_longitude=Decimal("22.22"),
        address="г. Москва, ул. Ленина, д. 1",
        vkusvill_settings=vkusvill_user_settings,
    )
    user.settings = user_settings
    session.add(user)
    await session.commit()
    return user


async def test_create_users_with_settings(test_session: AsyncSession, user_repo: UserRepository):
    # Arrange
    tg_id = 1
    vkusvill_user_settings = VkusvillUserSettings(
        device_id="device_id", user_number="1", token="token"
    )
    user_settings = UserSettings(
        address_latitude=Decimal("11.11"),
        address_longitude=Decimal("22.22"),
        address="г. Москва, ул. Ленина, д. 1",
        vkusvill_settings=vkusvill_user_settings,
    )
    user = User(tg_id=tg_id, settings=user_settings)

    # Act
    await user_repo.add_user(user)

    # Assert
    created_user = await test_session.scalar(select(User, User.tg_id == tg_id))
    assert created_user is not None
    assert created_user.settings.address_latitude == user_settings.address_latitude
    assert created_user.settings.address_longitude == user_settings.address_longitude
    assert created_user.settings.vkusvill_settings == vkusvill_user_settings


async def test_update_user_settings(
    test_session: AsyncSession, user_with_settings: User, user_repo: UserRepository
):
    # Arrange
    new_token = "new_token"
    user_with_settings.settings.vkusvill_settings.token = new_token  # type: ignore[union-attr]

    # Act
    # We have to manually flag the user settings as modified to trigger the flush
    flag_modified(user_with_settings.settings, "vkusvill_settings")
    await user_repo.update_user(user_with_settings)

    # Assert
    updated_user = await test_session.scalar(select(User, User.tg_id == user_with_settings.tg_id))
    assert updated_user is not None
    assert updated_user.settings.vkusvill_settings.token == new_token


async def test_get_user_for_notifications(
    user_with_settings: User, user_repo: UserRepository
) -> None:
    # Act
    users = await user_repo.get_users_for_notifications()

    # Assert
    assert len(users) == 1
    assert users[0].tg_id == user_with_settings.tg_id
