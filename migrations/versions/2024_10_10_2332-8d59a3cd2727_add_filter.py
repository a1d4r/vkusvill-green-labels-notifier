"""Add filter

Revision ID: 8d59a3cd2727
Revises: 3ee3d973f8d0
Create Date: 2024-10-10 23:32:54.731000

"""

from typing import Union

from collections.abc import Sequence

import advanced_alchemy.types
import sqlalchemy as sa

from alembic import op

import vkusvill_green_labels.models.db.utils.pydantic_type

from vkusvill_green_labels.models.vkusvill import VkusvillUserSettings

# revision identifiers, used by Alembic.
revision: str = "8d59a3cd2727"
down_revision: str | None = "3ee3d973f8d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "green_label_filters",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "definition",
            vkusvill_green_labels.models.db.utils.pydantic_type.PydanticType(VkusvillUserSettings),
            nullable=False,
        ),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.Column(
            "updated_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_green_label_filters")),
    )
    op.add_column("user_settings", sa.Column("green_labels_filter_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        op.f("fk_user_settings_green_labels_filter_id_green_label_filters"),
        "user_settings",
        "green_label_filters",
        ["green_labels_filter_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_user_settings_green_labels_filter_id_green_label_filters"),
        "user_settings",
        type_="foreignkey",
    )
    op.drop_column("user_settings", "green_labels_filter_id")
    op.drop_table("green_label_filters")
