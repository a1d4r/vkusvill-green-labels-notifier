from typing import NewType

from decimal import Decimal
from uuid import UUID

UserID = NewType("UserID", UUID)
UserSettingsID = NewType("UserSettingsID", UUID)
Latitude = NewType("Latitude", Decimal)
Longitude = NewType("Longitude", Decimal)
