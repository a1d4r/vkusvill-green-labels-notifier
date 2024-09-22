from decimal import Decimal
from uuid import uuid4

from sqlalchemy import UUID, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from vkusvill_green_labels.models.base import Base
from vkusvill_green_labels.models.types import UserSettingsID
from vkusvill_green_labels.models.utils.pydantic_type import PydanticType
from vkusvill_green_labels.services.vkusvill_api import VkusvillUserSettings


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[UserSettingsID] = mapped_column(UUID, default=uuid4, primary_key=True)
    address_latitude: Mapped[Decimal] = mapped_column(Numeric)
    address_longitude: Mapped[Decimal] = mapped_column(Numeric)
    address: Mapped[str]
    enable_notifications: Mapped[bool] = mapped_column(default=True)
    vkusvill_settings: Mapped[VkusvillUserSettings | None] = mapped_column(
        PydanticType(VkusvillUserSettings)
    )
