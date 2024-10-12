import pytest

from aiogram.types import User as TelegramUser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import TelegramUserFactory, UserFactory
from vkusvill_green_labels.models.db import Filter, User
from vkusvill_green_labels.models.filters import TitleWhiteListFilter
from vkusvill_green_labels.services.filter_service import FilterService


@pytest.fixture
async def filter_in_db(test_session: AsyncSession) -> Filter:
    filter_ = Filter(
        name="Жирные вздохи радости и сожаления",
        definition=TitleWhiteListFilter(whitelist=["торт", "чизкейк"]),
    )
    test_session.add(filter_)
    await test_session.commit()
    return filter_


@pytest.fixture
async def user_with_filter_in_db(
    test_session: AsyncSession, telegram_user: TelegramUser, filter_in_db: Filter
) -> User:
    user = UserFactory.build(
        first_name=telegram_user.first_name,
        last_name=telegram_user.last_name,
        username=telegram_user.username,
        tg_id=telegram_user.id,
    )
    user.settings.filters = [filter_in_db]
    test_session.add(user)
    await test_session.commit()
    return user


@pytest.mark.usefixtures("user_with_filter_in_db")
async def test_get_filter_by_telegram_user_and_id(
    filter_service: FilterService, telegram_user: TelegramUser, filter_in_db: Filter
) -> None:
    # Act
    user_filter = await filter_service.get_filter_by_telegram_user_and_id(
        telegram_user, filter_in_db.id
    )

    # Assert
    assert user_filter is not None
    assert user_filter.to_dict() == filter_in_db.to_dict()


@pytest.mark.usefixtures("user_with_filter_in_db")
async def test_get_filter_by_other_telegram_user_and_id(
    filter_service: FilterService, telegram_user: TelegramUser, filter_in_db: Filter
) -> None:
    # Arrange
    other_telegram_user = TelegramUserFactory.build(id=telegram_user.id + 1)

    # Act
    user_filter = await filter_service.get_filter_by_telegram_user_and_id(
        other_telegram_user, filter_in_db.id
    )

    # Assert
    assert user_filter is None


@pytest.mark.usefixtures("user_with_filter_in_db")
async def test_get_filters_by_telegram_user(
    filter_service: FilterService, telegram_user: TelegramUser, filter_in_db: Filter
) -> None:
    # Act
    user_filters = await filter_service.get_filters_by_telegram_user(telegram_user)

    # Assert
    assert len(user_filters) == 1
    assert user_filters[0].to_dict() == filter_in_db.to_dict()


@pytest.mark.usefixtures("user_with_filter_in_db")
async def test_delete_filter_by_user_and_id(
    filter_service: FilterService,
    telegram_user: TelegramUser,
    filter_in_db: Filter,
    test_session: AsyncSession,
) -> None:
    # Act
    await filter_service.delete_filter_by_telegram_user_and_id(telegram_user, filter_in_db.id)

    # Assert
    assert await test_session.scalar(select(Filter).where(Filter.id == filter_in_db.id)) is None


@pytest.mark.usefixtures("user_with_filter_in_db")
async def test_delete_filter_by_other_telegram_user_and_id(
    filter_service: FilterService,
    telegram_user: TelegramUser,
    filter_in_db: Filter,
    test_session: AsyncSession,
) -> None:
    # Arrange
    other_telegram_user = TelegramUserFactory.build(id=telegram_user.id + 1)

    # Act
    await filter_service.delete_filter_by_telegram_user_and_id(other_telegram_user, filter_in_db.id)

    # Assert
    assert (
        await test_session.scalar(select(Filter).where(Filter.id == filter_in_db.id))
        == filter_in_db
    )
