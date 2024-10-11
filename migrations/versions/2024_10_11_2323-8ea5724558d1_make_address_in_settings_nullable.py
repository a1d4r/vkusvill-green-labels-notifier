"""Make address in settings nullable

Revision ID: 8ea5724558d1
Revises: 6d5e1b41fec6
Create Date: 2024-10-11 23:23:15.455965

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8ea5724558d1"
down_revision: str | None = "6d5e1b41fec6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("user_settings", "address_latitude", existing_type=sa.NUMERIC(), nullable=True)
    op.alter_column("user_settings", "address_longitude", existing_type=sa.NUMERIC(), nullable=True)
    op.alter_column("user_settings", "address", existing_type=sa.VARCHAR(), nullable=True)


def downgrade() -> None:
    op.alter_column("user_settings", "address", existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column(
        "user_settings", "address_longitude", existing_type=sa.NUMERIC(), nullable=False
    )
    op.alter_column("user_settings", "address_latitude", existing_type=sa.NUMERIC(), nullable=False)
