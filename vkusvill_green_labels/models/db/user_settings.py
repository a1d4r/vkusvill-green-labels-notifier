from uuid import uuid4

from sqlalchemy import UUID, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from vkusvill_green_labels.models.db.address import Location
from vkusvill_green_labels.models.db.base import Base
from vkusvill_green_labels.models.db.utils.pydantic_type import PydanticType
from vkusvill_green_labels.models.types import Latitude, Longitude, UserSettingsID
from vkusvill_green_labels.models.vkusvill import VkusvillUserSettings


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[UserSettingsID] = mapped_column(UUID, default=uuid4, primary_key=True)
    address_latitude: Mapped[Latitude | None] = mapped_column(Numeric, nullable=True)
    address_longitude: Mapped[Longitude | None] = mapped_column(Numeric, nullable=True)
    address: Mapped[str | None]
    enable_notifications: Mapped[bool] = mapped_column(default=True)
    vkusvill_settings: Mapped[VkusvillUserSettings | None] = mapped_column(
        PydanticType(VkusvillUserSettings)
    )
    locations: Mapped[list[Location]] = relationship(
        secondary="user_settings_locations", lazy="selectin"
    )
