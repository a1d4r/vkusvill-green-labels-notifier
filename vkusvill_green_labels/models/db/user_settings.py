from uuid import uuid4

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from vkusvill_green_labels.models.db.address import Location

from vkusvill_green_labels.models.db.base import Base
from vkusvill_green_labels.models.db.filter import GreenLabelFilter
from vkusvill_green_labels.models.db.utils.pydantic_type import PydanticType
from vkusvill_green_labels.models.types import (
    GreenLabelFilterID,
    UserSettingsID,
)
from vkusvill_green_labels.models.vkusvill import VkusvillUserSettings


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[UserSettingsID] = mapped_column(UUID, default=uuid4, primary_key=True)
    enable_notifications: Mapped[bool] = mapped_column(default=True)
    vkusvill_settings: Mapped[VkusvillUserSettings | None] = mapped_column(
        PydanticType(VkusvillUserSettings), nullable=True
    )
    locations: Mapped[list[Location]] = relationship(
        secondary="user_settings_locations", lazy="selectin"
    )
    green_labels_filter_id: Mapped[GreenLabelFilterID | None] = mapped_column(
        ForeignKey("green_label_filters.id")
    )
    green_labels_filter: Mapped[GreenLabelFilter | None] = relationship(lazy="selectin")
