"""Durable, execution-fenced user questions; additive SQLite/MySQL migration."""
from sqlalchemy import Column, ForeignKey, Integer, String, Table, UniqueConstraint, Index
from app.chat.schema import metadata, identity, LargeText

questions = Table('chat_questions', metadata, *identity(),
    Column('turn_id', String(64), ForeignKey('chat_turns.id'), nullable=False),
    Column('worker_id', String(64), nullable=False),
    Column('generation', Integer, nullable=False),
    Column('request_key', String(64), nullable=False),
    Column('executor_turn_id', String(128), nullable=False),
    Column('status', String(24), nullable=False),
    Column('version', Integer, nullable=False, default=1),
    Column('questions_json', LargeText, nullable=False),
    Column('answer_json', LargeText),
    Column('idempotency_key', String(64)),
    Column('expires_at', String(32), nullable=False),
    UniqueConstraint('turn_id', 'generation', 'request_key', name='uq_chat_question_request'))
Index('ix_chat_questions_turn', questions.c.turn_id, questions.c.created_at)
TABLES = [questions]
