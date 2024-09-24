from typing import ClassVar

from dataclasses import dataclass

from pydantic import TypeAdapter
from redis.asyncio import Redis

from vkusvill_green_labels.models.types import UserID
from vkusvill_green_labels.models.vkusvill import GreenLabelItem


@dataclass
class GreenLabelsRepository:
    redis: Redis
    prefix: ClassVar[str] = "green_labels:"
    adapter: ClassVar[TypeAdapter[list[GreenLabelItem]]] = TypeAdapter(list[GreenLabelItem])

    async def get_items(self, user_id: UserID) -> list[GreenLabelItem]:
        value = await self.redis.get(self.prefix + str(user_id))
        if value is None:
            return []
        return self.adapter.validate_json(value)

    async def set_items(self, user_id: UserID, items: list[GreenLabelItem]) -> None:
        value = self.adapter.dump_json(items)
        await self.redis.set(self.prefix + str(user_id), value)
