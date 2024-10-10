from uuid import uuid4

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, mapped_column

from vkusvill_green_labels.models.db import Base
from vkusvill_green_labels.models.db.utils.pydantic_type import PydanticType
from vkusvill_green_labels.models.filter_operators import GreenLabelsFilterOperator
from vkusvill_green_labels.models.types import GreenLabelFilterID


class GreenLabelFilter(Base):
    __tablename__ = "green_label_filters"

    id: Mapped[GreenLabelFilterID] = mapped_column(UUID, default=uuid4, primary_key=True)
    definition: Mapped[GreenLabelsFilterOperator] = mapped_column(
        PydanticType(GreenLabelsFilterOperator)  # type: ignore[arg-type]
    )
