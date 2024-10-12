from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vkusvill_green_labels.models.db import Filter, User, UserSettings
from vkusvill_green_labels.models.types import FilterID


@dataclass
class FilterRepository:
    session: AsyncSession

    async def get_filter_by_user_and_id(self, user: User, filter_id: FilterID) -> Filter | None:
        result = await self.session.execute(
            select(Filter)
            .join(UserSettings.filters)
            .where(Filter.id == filter_id, UserSettings.id == user.settings.id)
        )
        return result.scalar_one_or_none()

    async def delete_filter_by_user_and_id(self, user: User, filter_id: FilterID) -> None:
        filter_ = await self.get_filter_by_user_and_id(user, filter_id)
        if filter_ is None:
            return
        user.settings.filters.remove(filter_)
        await self.session.delete(filter_)
        await self.session.commit()
