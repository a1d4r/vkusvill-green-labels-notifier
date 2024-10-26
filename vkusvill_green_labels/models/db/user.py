from typing import TYPE_CHECKING

from uuid import uuid4

from sqlalchemy import UUID, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vkusvill_green_labels.models.db.base import Base
from vkusvill_green_labels.models.types import UserID, UserSettingsID

if TYPE_CHECKING:
    from vkusvill_green_labels.models.db import UserSettings


class User(Base):
    """Основная информация о пользователе."""

    __tablename__ = "users"

    id: Mapped[UserID] = mapped_column(UUID, default=uuid4, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, index=True, unique=True)
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    username: Mapped[str | None]

    user_settings_id: Mapped[UserSettingsID] = mapped_column(ForeignKey("user_settings.id"))
    settings: Mapped["UserSettings"] = relationship(lazy="selectin")
