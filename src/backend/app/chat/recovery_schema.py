"""Additive, cross-database recovery ledger; business turn state is independent."""
from sqlalchemy import Column, ForeignKey, Index, Integer, String, Table, Text
from app.chat.schema import metadata

recoveries = Table('chat_turn_recoveries', metadata,
    Column('turn_id', String(64), ForeignKey('chat_turns.id'), primary_key=True),
    Column('state', String(24), nullable=False),
    Column('generation', Integer, nullable=False),
    Column('attempt_count', Integer, nullable=False),
    Column('first_attempt_at', String(32)), Column('next_retry_at', String(32)),
    Column('last_result', String(64)), Column('lease_token', String(64)),
    Column('lease_expires_at', String(32)), Column('updated_at', String(32), nullable=False))
Index('ix_chat_recovery_due', recoveries.c.state, recoveries.c.next_retry_at)
resumes = Table('chat_recovery_resumes', metadata,
    Column('request_id', String(64), primary_key=True),
    Column('turn_id', String(64), ForeignKey('chat_turns.id'), nullable=False),
    Column('generation', Integer, nullable=False),
    Column('actor_hash', String(64), nullable=False), Column('reason', String(64), nullable=False),
    Column('previous', Text, nullable=False), Column('created_at', String(32), nullable=False))
TABLES = [recoveries, resumes]
