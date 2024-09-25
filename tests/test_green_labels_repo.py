from decimal import Decimal
from uuid import uuid4

import pytest

from redis.asyncio import Redis

from vkusvill_green_labels.models.types import UserID
from vkusvill_green_labels.models.vkusvill import GreenLabelItem
from vkusvill_green_labels.repositories.green_labels import GreenLabelsRepository


@pytest.fixture
async def green_labels_repo(redis_client: Redis) -> GreenLabelsRepository:
    return GreenLabelsRepository(redis_client)


async def test_set_get_items(green_labels_repo: GreenLabelsRepository) -> None:
    # Arrange
    user_id = UserID(uuid4())
    item = GreenLabelItem(
        item_id=1,
        title="test",
        amount=Decimal(1),
        weight_str="1",
        rating="4.9",
        price=Decimal("100"),
        discount_price=Decimal("40"),
    )

    # Act
    await green_labels_repo.set_items(user_id, [item])
    items = await green_labels_repo.get_items(user_id)

    # Assert
    assert items == [item]


async def test_get_items_non_existent(green_labels_repo: GreenLabelsRepository) -> None:
    # Arrange
    non_existent_user_id = UserID(uuid4())

    # Act
    items = await green_labels_repo.get_items(non_existent_user_id)

    # Assert
    assert items == []
