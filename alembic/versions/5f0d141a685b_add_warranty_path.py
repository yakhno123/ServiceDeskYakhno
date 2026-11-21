"""Add warranty_path

Revision ID: 5f0d141a685b
Revises: f9b2538f1ef6
Create Date: 2026-11-21 16:06:08.212154

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f0d141a685b'
down_revision: Union[str, Sequence[str], None] = 'f9b2538f1ef6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
