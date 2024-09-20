from typing import TYPE_CHECKING

from uuid import uuid4

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vkusvill_green_labels.models.base import Base
from vkusvill_green_labels.models.identifiers import UserID, UserSettingsID

if TYPE_CHECKING:
    from vkusvill_green_labels.models import UserSettings


class User(Base):
    __tablename__ = "users"

    id: Mapped[UserID] = mapped_column(UUID, default=uuid4, primary_key=True)
    tg_id: Mapped[int] = mapped_column(index=True, unique=True)
    first_name: Mapped[str | None] = mapped_column()
    last_name: Mapped[str | None] = mapped_column()
    username: Mapped[str | None] = mapped_column()

    user_settings_id: Mapped[UserSettingsID] = mapped_column(ForeignKey("user_settings.id"))
    settings: Mapped["UserSettings"] = relationship(lazy="selectin")
