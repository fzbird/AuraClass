"""change_processing_time_to_float

Revision ID: 3a7b0f6be782
Revises: b37dbd38e7c2
Create Date: 2025-05-01 22:52:37.641549

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '3a7b0f6be782'
down_revision: Union[str, None] = 'b37dbd38e7c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ai_messages', 'processing_time',
               existing_type=mysql.INTEGER(),
               type_=sa.Float(),
               comment='处理时间（秒）（仅适用于assistant消息）',
               existing_comment='处理时间（仅适用于assistant消息）',
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('ai_messages', 'processing_time',
               existing_type=sa.Float(),
               type_=mysql.INTEGER(),
               comment='处理时间（仅适用于assistant消息）',
               existing_comment='处理时间（秒）（仅适用于assistant消息）',
               existing_nullable=True)
    # ### end Alembic commands ###
