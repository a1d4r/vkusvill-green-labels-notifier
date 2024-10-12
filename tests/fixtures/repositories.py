import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from vkusvill_green_labels.repositories.filter import FilterRepository
from vkusvill_green_labels.repositories.user import UserRepository


@pytest.fixture
async def user_repository(session: AsyncSession) -> UserRepository:
    return UserRepository(session)


@pytest.fixture
async def filter_repository(session: AsyncSession) -> FilterRepository:
    return FilterRepository(session)
