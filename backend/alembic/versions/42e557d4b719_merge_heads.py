"""merge heads

Revision ID: 42e557d4b719
Revises: 25df4feaa9a7, remove_ai_file_attachment
Create Date: 2025-04-21 11:15:48.224237

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42e557d4b719'
down_revision: Union[str, None] = ('25df4feaa9a7', 'remove_ai_file_attachment')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
