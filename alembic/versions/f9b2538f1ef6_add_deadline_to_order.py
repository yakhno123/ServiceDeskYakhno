"""Add deadline to Order

Revision ID: f9b2538f1ef6
Revises: edf44fce0572
Create Date: 2026-11-21 15:59:10.432229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9b2538f1ef6'
down_revision: Union[str, Sequence[str], None] = 'edf44fce0572'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
