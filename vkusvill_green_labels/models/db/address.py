from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from vkusvill_green_labels.models.db.base import Base
from vkusvill_green_labels.models.types import Latitude, Longitude, UserSettingsID


class Location(Base):
    __tablename__ = "locations"

    latitude: Mapped[Latitude] = mapped_column(Numeric)
    longitude: Mapped[Longitude] = mapped_column(Numeric)
    address: Mapped[str]


class UserSettingsLocation(Base):
    __tablename__ = "user_settings_locations"

    user_settings_id: Mapped[UserSettingsID] = mapped_column(
        ForeignKey("user_settings.id", ondelete="CASCADE"), primary_key=True
    )
    location_id: Mapped[Location] = mapped_column(
        ForeignKey("locations.id", ondelete="CASCADE"), primary_key=True
    )
