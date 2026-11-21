"""Remove unique from telegram_id

Revision ID: 2ea84c7396cc
Revises: cfa4497d3eef
Create Date: 2026-11-21 15:35:51.458790

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ea84c7396cc'
down_revision: Union[str, Sequence[str], None] = 'cfa4497d3eef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
