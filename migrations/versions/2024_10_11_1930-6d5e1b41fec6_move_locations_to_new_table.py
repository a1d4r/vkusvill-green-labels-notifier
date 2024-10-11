"""Move locations to new table

Revision ID: 6d5e1b41fec6
Revises: d2dc412bc35e
Create Date: 2024-10-11 19:30:49.354344

"""

from collections.abc import Sequence
from decimal import Decimal

from alembic import op
from sqlalchemy import delete, orm, select

from vkusvill_green_labels.models.db import Location, User

# revision identifiers, used by Alembic.
revision: str = "6d5e1b41fec6"
down_revision: str | None = "d2dc412bc35e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    users = session.scalars(select(User))
    for user in users:
        location = Location(
            latitude=user.settings.address_latitude.quantize(Decimal("0.000001")),
            longitude=user.settings.address_longitude.quantize(Decimal("0.000001")),
            address=user.settings.address,
        )
        user.settings.locations.append(location)
        session.add(location)

    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    session.execute(delete(Location))
