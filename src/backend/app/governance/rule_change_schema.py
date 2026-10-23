"""New content-bound product confirmations; legacy replacement rows remain readable."""
from sqlalchemy import Column, Integer, String, Table, UniqueConstraint
from app.chat.schema import metadata, identity, LargeText

confirmations = Table('governance_rule_change_confirmations', metadata, *identity(),
    Column('scope_key', String(64), nullable=False),
    Column('space_id', String(64), nullable=False),
    Column('repository_id', String(64), nullable=False),
    Column('binding_revision', String(64), nullable=False),
    Column('change_id', String(128), nullable=False),
    Column('content_digest', String(64), nullable=False),
    Column('body', LargeText, nullable=False),
    Column('state', String(24), nullable=False),
    Column('revision', Integer, nullable=False),
    Column('actor_id', String(64), nullable=False),
    Column('reason', String(500), nullable=False, default=''),
    UniqueConstraint('scope_key', 'change_id', 'content_digest', name='uq_rule_change_exact_content'))
events = Table('governance_rule_change_events', metadata, *identity(),
    Column('scope_key', String(64), nullable=False),
    Column('change_id', String(128), nullable=False),
    Column('content_digest', String(64), nullable=False),
    Column('actor_id', String(64), nullable=False),
    Column('action', String(24), nullable=False),
    Column('request_key', String(64), nullable=False),
    Column('reason', String(500), nullable=False, default=''),
    UniqueConstraint('scope_key', 'request_key', name='uq_rule_change_event_request'))
TABLES = (confirmations, events)
