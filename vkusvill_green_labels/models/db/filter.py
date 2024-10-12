from uuid import uuid4

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from vkusvill_green_labels.models.db.base import Base
from vkusvill_green_labels.models.db.utils.pydantic_type import PydanticType
from vkusvill_green_labels.models.filter_operators import GreenLabelsFilterOperator
from vkusvill_green_labels.models.types import GreenLabelFilterID, UserSettingsID


class Filter(Base):
    """Фильтр для товаров с зелёнными ценниками."""

    __tablename__ = "filters"

    id: Mapped[GreenLabelFilterID] = mapped_column(UUID, default=uuid4, primary_key=True)
    definition: Mapped[GreenLabelsFilterOperator] = mapped_column(
        PydanticType(GreenLabelsFilterOperator)  # type: ignore[arg-type]
    )
    name: Mapped[str | None]
    is_active: Mapped[bool] = mapped_column(default=True)


class UserSettingsFilter(Base):
    __tablename__ = "user_settings_filters"

    user_settings_id: Mapped[UserSettingsID] = mapped_column(
        ForeignKey("user_settings.id", ondelete="CASCADE"), primary_key=True
    )
    green_label_filter_id: Mapped[GreenLabelFilterID] = mapped_column(
        ForeignKey("filters.id", ondelete="CASCADE"), primary_key=True
    )
