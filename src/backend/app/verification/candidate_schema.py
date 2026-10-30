"""Durable candidate environment facts; no connection strings or credentials."""
from sqlalchemy import Table, Column, String, Text, Integer
from app.chat.schema import metadata, identity

environments = Table('verification_candidate_environments', metadata, *identity(),
    Column('candidate_id', String(64), nullable=False, unique=True),
    Column('space_id', String(64), nullable=False),
    Column('repository_id', String(64), nullable=False),
    Column('candidate_commit', String(64), nullable=False),
    Column('template_digest', String(64), nullable=False),
    Column('daemon_id', String(128), nullable=False),
    Column('state', String(32), nullable=False),
    Column('expires_at', Integer, nullable=False),
    Column('error_code', String(64)),
    Column('result_json', Text, nullable=False),
    Column('cleanup_state', String(24), nullable=False))
TABLES = [environments]
