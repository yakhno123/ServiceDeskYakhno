"""Add Note table

Revision ID: f79f35032953
Revises: 2ea84c7396cc
Create Date: 2026-11-21 15:45:26.993491

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f79f35032953'
down_revision: Union[str, Sequence[str], None] = '2ea84c7396cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
