"""Separate location tables

Revision ID: d2dc412bc35e
Revises: 3ee3d973f8d0
Create Date: 2024-10-11 19:29:41.719856

"""

from collections.abc import Sequence

import advanced_alchemy.types
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d2dc412bc35e"
down_revision: str | None = "3ee3d973f8d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "locations",
        sa.Column("latitude", sa.Numeric(), nullable=False),
        sa.Column("longitude", sa.Numeric(), nullable=False),
        sa.Column("address", sa.String(), nullable=False),
        sa.Column("id", advanced_alchemy.types.guid.GUID(length=16), nullable=False),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.Column(
            "updated_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_locations")),
    )
    op.create_table(
        "user_settings_locations",
        sa.Column("user_settings_id", sa.UUID(), nullable=False),
        sa.Column("location_id", advanced_alchemy.types.guid.GUID(length=16), nullable=False),
        sa.Column("id", advanced_alchemy.types.guid.GUID(length=16), nullable=False),
        sa.Column("sa_orm_sentinel", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.Column(
            "updated_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["locations.id"],
            name=op.f("fk_user_settings_locations_location_id_locations"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_settings_id"],
            ["user_settings.id"],
            name=op.f("fk_user_settings_locations_user_settings_id_user_settings"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "user_settings_id", "location_id", "id", name=op.f("pk_user_settings_locations")
        ),
    )


def downgrade() -> None:
    op.drop_table("user_settings_locations")
    op.drop_table("locations")
