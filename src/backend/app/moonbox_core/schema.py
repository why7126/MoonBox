"""Additive workspace tables, shared by SQLite and MySQL migrations."""
from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text, UniqueConstraint, Index
from app.chat.schema import metadata, identity

workspaces = Table('moonbox_workspaces', metadata, *identity(),
    Column('space_id', String(64), nullable=False),
    Column('repository_id', String(64), nullable=False),
    Column('git_identity', String(64), nullable=False),
    Column('purpose', String(16), nullable=False),
    Column('root_locator', Text, nullable=False),
    Column('base_commit', String(64), nullable=False),
    Column('lifecycle', String(24), nullable=False),
    Column('revision', Integer, nullable=False, default=1))
Index('ix_moonbox_workspace_scope', workspaces.c.space_id, workspaces.c.repository_id)
main_bindings = Table('moonbox_main_bindings', metadata,
    Column('git_identity', String(64), primary_key=True),
    Column('space_id', String(64), nullable=False),
    Column('repository_id', String(64), nullable=False),
    Column('workspace_id', String(64), ForeignKey('moonbox_workspaces.id'), nullable=False),
    UniqueConstraint('space_id', 'repository_id', name='uq_moonbox_repository_main'))
claims = Table('moonbox_delivery_claims', metadata,
    Column('space_id', String(64), primary_key=True),
    Column('repository_id', String(64), primary_key=True),
    Column('delivery_root', String(128), primary_key=True),
    Column('workspace_id', String(64), ForeignKey('moonbox_workspaces.id'), nullable=False))
write_locks = Table('moonbox_workspace_write_locks', metadata,
    Column('workspace_id', String(64), ForeignKey('moonbox_workspaces.id'), primary_key=True),
    Column('operation_id', String(64), nullable=False),
    Column('generation', Integer, nullable=False),
    Column('created_at', String(32), nullable=False))
session_bindings = Table('moonbox_workspace_sessions', metadata,
    Column('conversation_id', String(64), ForeignKey('chat_conversations.id'), primary_key=True),
    Column('workspace_id', String(64), ForeignKey('moonbox_workspaces.id'), nullable=False))
migrations = Table('moonbox_workspace_migrations', metadata,
    Column('conversation_id', String(64), ForeignKey('chat_conversations.id'), primary_key=True),
    Column('schema_version', Integer, nullable=False),
    Column('previous_workspace_id', String(64)),
    Column('workspace_id', String(64), ForeignKey('moonbox_workspaces.id'), nullable=False),
    Column('baseline_digest', String(64), nullable=False),
    Column('created_at', String(32), nullable=False))
delivery_sessions = Table('moonbox_delivery_sessions', metadata,
    Column('conversation_id', String(64), ForeignKey('chat_conversations.id'), primary_key=True),
    Column('change_id', String(128), nullable=False),
    Column('delivery_root', String(128), nullable=False),
    Column('predecessor_id', String(64)))
runtime_bindings = Table('moonbox_runtime_bindings', metadata,
    Column('turn_id', String(64), ForeignKey('chat_turns.id'), primary_key=True),
    Column('workspace_id', String(64), ForeignKey('moonbox_workspaces.id'), nullable=False),
    Column('image_digest', String(80), nullable=False),
    Column('tool_version', String(128), nullable=False),
    Column('policy_digest', String(64), nullable=False),
    Column('created_at', String(32), nullable=False))
assignments = Table('moonbox_workspace_assignments', metadata,
    Column('workspace_id', String(64), ForeignKey('moonbox_workspaces.id'), primary_key=True),
    Column('change_id', String(128), nullable=False),
    Column('delivery_root', String(128), nullable=False),
    Column('state', String(24), nullable=False))
execution_receipts = Table('moonbox_execution_receipts', metadata,
    Column('turn_id', String(64), ForeignKey('chat_turns.id'), primary_key=True),
    Column('executor_id', String(128)),
    Column('scope_json', Text),
    Column('last_checked_at', String(32)),
    Column('executor_closed', Integer, nullable=False, default=0),
    Column('files_collected', Integer, nullable=False, default=0))
TABLES = [workspaces, main_bindings, claims, write_locks, session_bindings, migrations, delivery_sessions, runtime_bindings, assignments, execution_receipts]
from .integration_schema import TABLES as INTEGRATION_TABLES
TABLES.extend(INTEGRATION_TABLES)
