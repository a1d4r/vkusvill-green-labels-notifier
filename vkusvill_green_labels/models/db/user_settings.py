from uuid import uuid4

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vkusvill_green_labels.models.db.address import Location
from vkusvill_green_labels.models.db.base import Base
from vkusvill_green_labels.models.db.filter import Filter
from vkusvill_green_labels.models.db.utils.pydantic_type import PydanticType
from vkusvill_green_labels.models.types import UserSettingsID
from vkusvill_green_labels.models.vkusvill import NotificationType, VkusvillUserSettings


class UserSettings(Base):
    """Настройки пользователя."""

    __tablename__ = "user_settings"

    id: Mapped[UserSettingsID] = mapped_column(UUID, default=uuid4, primary_key=True)
    enable_notifications: Mapped[bool] = mapped_column(default=True)
    notification_type: Mapped[NotificationType] = mapped_column(default=NotificationType.detailed)
    vkusvill_settings: Mapped[VkusvillUserSettings | None] = mapped_column(
        PydanticType(VkusvillUserSettings), nullable=True
    )
    locations: Mapped[list[Location]] = relationship(
        secondary="user_settings_locations", lazy="selectin"
    )
    filters: Mapped[list[Filter]] = relationship(secondary="user_settings_filters", lazy="selectin")
