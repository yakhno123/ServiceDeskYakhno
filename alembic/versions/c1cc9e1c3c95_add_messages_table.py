"""Add messages table

Revision ID: c1cc9e1c3c95
Revises: 7b89cb45d3a4
Create Date: 2026-11-21 16:20:11.556359

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1cc9e1c3c95'
down_revision: Union[str, Sequence[str], None] = '7b89cb45d3a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
