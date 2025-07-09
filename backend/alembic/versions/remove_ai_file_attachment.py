"""remove AIFileAttachment table

Revision ID: remove_ai_file_attachment
Revises: 
Create Date: 2023-10-10 10:10:10.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = 'remove_ai_file_attachment'
down_revision = None  # 请替换为您上一个迁移的ID
branch_labels = None
depends_on = None


def upgrade():
    # 检查表是否存在，如果存在则删除
    conn = op.get_bind()
    inspector = inspect(conn)
    if 'ai_file_attachments' in inspector.get_table_names():
        op.drop_table('ai_file_attachments')


def downgrade():
    # 检查表是否不存在，如果不存在则创建
    conn = op.get_bind()
    inspector = inspect(conn)
    if 'ai_file_attachments' not in inspector.get_table_names():
        # 创建AIFileAttachment表
        op.create_table(
            'ai_file_attachments',
            sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
            sa.Column('message_id', sa.Integer(), nullable=False),
            sa.Column('upload_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['message_id'], ['ai_messages.id'], name='fk_ai_file_attachments_message_id'),
            sa.ForeignKeyConstraint(['upload_id'], ['uploads.id'], name='fk_ai_file_attachments_upload_id'),
            sa.PrimaryKeyConstraint('id')
        )
        
        # 创建索引
        op.create_index('ix_ai_file_attachments_message_id', 'ai_file_attachments', ['message_id'])
        op.create_index('ix_ai_file_attachments_upload_id', 'ai_file_attachments', ['upload_id']) 