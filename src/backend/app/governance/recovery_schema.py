"""Additive SQLite/MySQL durable recovery metadata; artifacts stay in private journals."""
from sqlalchemy import Column, Index, Integer, String, Table, UniqueConstraint
from app.chat.schema import metadata, identity
from sqlalchemy.dialects.mysql import VARCHAR

# MySQL 8 NO PAD binary collation preserves the same key identity as SQLite.
REQUEST_KEY = String(64).with_variant(VARCHAR(64, collation="utf8mb4_0900_bin"), "mysql")

operations = Table('governance_operations', metadata, *identity(),
    Column('actor_id', String(64), nullable=False), Column('scope_key', String(64), nullable=False),
    Column('space_id', String(64), nullable=False), Column('repository_id', String(64), nullable=False),
    Column('conversation_id', String(64), nullable=False), Column('origin_turn_id', String(64), unique=True),
    Column('candidate_id', String(64), unique=True), Column('application_id', String(64)),
    Column('object_id', String(128), nullable=False), Column('action', String(32), nullable=False),
    Column('request_key', REQUEST_KEY, nullable=False), Column('request_hash', String(64), nullable=False),
    Column('binding_revision', String(64), nullable=False), Column('source_hash', String(64), nullable=False),
    Column('manifest_hash', String(64)), Column('parent_operation_id', String(64)),
    Column('schema_version', Integer, nullable=False, default=1),
    Column('version', Integer, nullable=False, default=1),
    Column('stage', String(24), nullable=False, default='prepare'),
    Column('state', String(24), nullable=False, default='active'),
    Column('execution_terminal', String(24)), Column('reason_code', String(64)),
    Column('auto_retry_count', Integer, nullable=False, default=0),
    Column('manual_count', Integer, nullable=False, default=0),
    Column('next_retry_at', String(32)), Column('recovery_expires_at', String(32)),
    Column('retention_state', String(24), nullable=False, default='retained'),
    Column('artifacts_released_at', String(32)), Column('retention_until', String(32)),
    Column('lease_owner', String(64)), Column('lease_until', String(32)),
    Column('fencing_token', Integer, nullable=False, default=0),
    UniqueConstraint('actor_id', 'scope_key', 'action', 'request_key', name='uq_governance_recovery_request'))
Index('ix_governance_recovery_queue', operations.c.state, operations.c.next_retry_at)
Index('ix_governance_recovery_object', operations.c.scope_key, operations.c.object_id, operations.c.state)
Index('ix_governance_recovery_expiry', operations.c.recovery_expires_at, operations.c.state)
attempts = Table('governance_recovery_attempts', metadata, *identity(),
    Column('operation_id', String(64), nullable=False), Column('request_key', REQUEST_KEY, nullable=False),
    Column('request_hash', String(64), nullable=False), Column('kind', String(16), nullable=False),
    Column('fencing_token', Integer, nullable=False), Column('state', String(24), nullable=False),
    Column('request_id', String(64)), Column('reason_code', String(64)),
    UniqueConstraint('operation_id', 'request_key', name='uq_governance_recovery_attempt'))
TABLES = (operations, attempts)
