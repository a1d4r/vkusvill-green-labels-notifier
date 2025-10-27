"""Add increase notification type

Revision ID: 69cd8b2f1bac
Revises: f45bb3ceb277
Create Date: 2025-10-27 21:15:02.834854

"""

from collections.abc import Sequence

from alembic import op
from alembic_postgresql_enum import TableReference

# revision identifiers, used by Alembic.
revision: str = "69cd8b2f1bac"
down_revision: str | None = "f45bb3ceb277"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.sync_enum_values(
        enum_schema="public",
        enum_name="notificationtype",
        new_values=["detailed", "only_quantity", "only_increase"],
        affected_columns=[
            TableReference(
                table_schema="public",
                table_name="user_settings",
                column_name="notification_type",
                existing_server_default="'detailed'::notificationtype",
            )
        ],
        enum_values_to_rename=[],
    )


def downgrade() -> None:
    op.sync_enum_values(
        enum_schema="public",
        enum_name="notificationtype",
        new_values=["detailed", "only_quantity"],
        affected_columns=[
            TableReference(
                table_schema="public",
                table_name="user_settings",
                column_name="notification_type",
                existing_server_default="'detailed'::notificationtype",
            )
        ],
        enum_values_to_rename=[],
    )
