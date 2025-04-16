"""Add notification type

Revision ID: f45bb3ceb277
Revises: 249977e15076
Create Date: 2025-04-16 01:42:44.398075

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f45bb3ceb277"
down_revision: str | None = "249977e15076"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    sa.Enum("detailed", "only_quantity", name="notificationtype").create(op.get_bind())
    op.add_column(
        "user_settings",
        sa.Column(
            "notification_type",
            postgresql.ENUM(
                "detailed", "only_quantity", name="notificationtype", create_type=False
            ),
            server_default="detailed",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("user_settings", "notification_type")
    sa.Enum("detailed", "only_quantity", name="notificationtype").drop(op.get_bind())
