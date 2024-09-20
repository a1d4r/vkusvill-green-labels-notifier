"""Add user and settings

Revision ID: 145ea4bda68a
Revises:
Create Date: 2024-09-21 02:50:13.796875

"""

from collections.abc import Sequence

import advanced_alchemy.types
import sqlalchemy as sa

from alembic import op

import vkusvill_green_labels.models.utils.pydantic_type

from vkusvill_green_labels.services.vkusvill import VkusvillUserSettings

# revision identifiers, used by Alembic.
revision: str = "145ea4bda68a"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_settings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("address_latitude", sa.Numeric(), nullable=False),
        sa.Column("address_longitude", sa.Numeric(), nullable=False),
        sa.Column("enable_notifications", sa.Boolean(), nullable=False),
        sa.Column(
            "vkusvill_settings",
            vkusvill_green_labels.models.utils.pydantic_type.PydanticType(VkusvillUserSettings),
            nullable=True,
        ),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.Column(
            "updated_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_settings")),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tg_id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("user_settings_id", sa.UUID(), nullable=False),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.Column(
            "updated_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["user_settings_id"],
            ["user_settings.id"],
            name=op.f("fk_users_user_settings_id_user_settings"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_tg_id"), "users", ["tg_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_tg_id"), table_name="users")
    op.drop_table("users")
    op.drop_table("user_settings")
