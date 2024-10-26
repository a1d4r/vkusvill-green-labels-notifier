"""Make telegram id int64

Revision ID: 249977e15076
Revises: 272acf3925ed
Create Date: 2024-10-26 12:57:00.043010

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "249977e15076"
down_revision: str | None = "272acf3925ed"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "users", "tg_id", existing_type=sa.INTEGER(), type_=sa.BigInteger(), existing_nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        "users", "tg_id", existing_type=sa.BigInteger(), type_=sa.INTEGER(), existing_nullable=False
    )
