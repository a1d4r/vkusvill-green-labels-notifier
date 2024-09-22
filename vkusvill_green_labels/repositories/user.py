from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from vkusvill_green_labels.models import User, UserSettings


@dataclass
class UserRepository:
    session: AsyncSession

    async def add_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        return user

    async def get_user_by_telegram_id(self, tg_id: int) -> User | None:
        result = await self.session.execute(select(User, User.tg_id == tg_id))
        return result.scalar_one_or_none()

    async def update_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        return user

    async def get_users_for_notifications(self) -> list[User]:
        return list(
            await self.session.scalars(
                select(User).join(UserSettings).where(UserSettings.enable_notifications.is_(True))
            )
        )
