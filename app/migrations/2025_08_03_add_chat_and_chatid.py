from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import Session
from datetime import datetime
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'chats',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('title', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow)
    )
    op.add_column('messages', sa.Column('chat_id', sa.Integer, sa.ForeignKey('chats.id'), nullable=True))

def downgrade():
    op.drop_column('messages', 'chat_id')
    op.drop_table('chats')
