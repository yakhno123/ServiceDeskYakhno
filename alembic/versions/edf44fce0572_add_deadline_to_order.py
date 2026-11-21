"""Add deadline to Order

Revision ID: edf44fce0572
Revises: f79f35032953
Create Date: 2026-11-21 15:57:37.004706

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'edf44fce0572'
down_revision: Union[str, Sequence[str], None] = 'f79f35032953'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
