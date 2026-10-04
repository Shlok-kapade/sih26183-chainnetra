"""Add addon tables

Revision ID: 6fed10eab0f4
Revises: 1e23f1bf772e
Create Date: 2026-10-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6fed10eab0f4'
down_revision: Union[str, None] = '1e23f1bf772e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass

def downgrade() -> None:
    pass
