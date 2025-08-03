"""
Migration script: Add session_id column to Message table
"""
from sqlalchemy import Column, String, text
from sqlalchemy import create_engine, MetaData, Table

# SQLite migration example
DATABASE_URL = "sqlite:///./chat.db"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

messages = Table('messages', metadata, autoload_with=engine)

# Only add if not exists
if 'session_id' not in messages.c:
    with engine.connect() as conn:
        conn.execute(text('ALTER TABLE messages ADD COLUMN session_id VARCHAR'))
        print('session_id column added.')
else:
    print('session_id already exists.')
