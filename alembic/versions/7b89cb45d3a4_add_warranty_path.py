"""Add warranty_path

Revision ID: 7b89cb45d3a4
Revises: 5f0d141a685b
Create Date: 2026-11-21 16:06:56.000401

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b89cb45d3a4'
down_revision: Union[str, Sequence[str], None] = '5f0d141a685b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
