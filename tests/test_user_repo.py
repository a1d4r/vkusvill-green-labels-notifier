import pytest

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from tests.factories import LocationFactory
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
    user = User(
        tg_id=1,
        settings=UserSettings(
            vkusvill_settings=VkusvillUserSettings(
                device_id="device_id", user_number="1", token="token_1"
            ),
            locations=[LocationFactory.build()],
        ),
    )
    session.add(user)
    await session.commit()
    return user


@pytest.fixture
async def user_with_disabled_notifications(session: AsyncSession) -> User:
    user = User(
        tg_id=2,
        settings=UserSettings(
            vkusvill_settings=VkusvillUserSettings(
                device_id="device_id", user_number="2", token="token_2"
            ),
            locations=[LocationFactory.build()],
            enable_notifications=False,
        ),
    )
    session.add(user)
    await session.commit()
    return user


@pytest.fixture
async def user_without_locations(session: AsyncSession) -> User:
    user = User(
        tg_id=3,
        settings=UserSettings(
            vkusvill_settings=VkusvillUserSettings(
                device_id="device_id", user_number="3", token="token_3"
            )
        ),
    )
    session.add(user)
    await session.commit()
    return user


async def test_create_users_with_settings(test_session: AsyncSession, user_repo: UserRepository):
    # Arrange
    tg_id = 1
    user = User(
        tg_id=tg_id,
        settings=UserSettings(
            vkusvill_settings=VkusvillUserSettings(
                device_id="device_id", user_number="1", token="token"
            ),
            locations=[LocationFactory.build()],
        ),
    )

    # Act
    await user_repo.add_user(user)

    # Assert
    user_in_db = await test_session.scalar(select(User, User.tg_id == tg_id))
    assert user_in_db is not None
    assert user_in_db.settings.locations[0].to_dict() == user.settings.locations[0].to_dict()
    assert user_in_db.settings.vkusvill_settings == user.settings.vkusvill_settings


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


async def test_get_users_for_notifications(
    user_with_settings: User, user_repo: UserRepository
) -> None:
    # Act
    users = await user_repo.get_users_for_notifications()

    # Assert
    assert len(users) == 1
    assert users[0].tg_id == user_with_settings.tg_id


@pytest.mark.usefixtures("user_with_disabled_notifications")
@pytest.mark.usefixtures("user_without_locations")
async def test_get_users_for_notifications_no_candidates(user_repo: UserRepository) -> None:
    # Act
    users = await user_repo.get_users_for_notifications()

    # Assert
    assert users == []
