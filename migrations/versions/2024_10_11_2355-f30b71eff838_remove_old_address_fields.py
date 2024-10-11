"""Remove old address fields

Revision ID: f30b71eff838
Revises: 8ea5724558d1
Create Date: 2024-10-11 23:55:09.773526

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f30b71eff838"
down_revision: str | None = "8ea5724558d1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("user_settings", "address_longitude")
    op.drop_column("user_settings", "address_latitude")
    op.drop_column("user_settings", "address")


def downgrade() -> None:
    op.add_column(
        "user_settings", sa.Column("address", sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    op.add_column(
        "user_settings",
        sa.Column("address_latitude", sa.NUMERIC(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "user_settings",
        sa.Column("address_longitude", sa.NUMERIC(), autoincrement=False, nullable=True),
    )
