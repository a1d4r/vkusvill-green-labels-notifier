"""Add filters

Revision ID: 272acf3925ed
Revises: f30b71eff838
Create Date: 2024-10-12 16:15:32.549606

"""

from collections.abc import Sequence  # noqa: I001

import advanced_alchemy.types
import sqlalchemy as sa

from alembic import op

import vkusvill_green_labels.models.db.utils.pydantic_type
from vkusvill_green_labels.models.filters import GreenLabelsFilter

# revision identifiers, used by Alembic.
revision: str = "272acf3925ed"
down_revision: str | None = "f30b71eff838"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "filters",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "definition",
            vkusvill_green_labels.models.db.utils.pydantic_type.PydanticType(GreenLabelsFilter),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.Column(
            "updated_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_filters")),
    )
    op.create_table(
        "user_settings_filters",
        sa.Column("user_settings_id", sa.UUID(), nullable=False),
        sa.Column("filter_id", sa.UUID(), nullable=False),
        sa.Column("id", advanced_alchemy.types.guid.GUID(length=16), nullable=False),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.Column(
            "updated_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["filter_id"],
            ["filters.id"],
            name=op.f("fk_user_settings_filters_filter_id_filters"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_settings_id"],
            ["user_settings.id"],
            name=op.f("fk_user_settings_filters_user_settings_id_user_settings"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "user_settings_id", "filter_id", "id", name=op.f("pk_user_settings_filters")
        ),
    )


def downgrade() -> None:
    op.drop_table("user_settings_filters")
    op.drop_table("filters")
