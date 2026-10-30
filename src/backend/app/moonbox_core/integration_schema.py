"""Candidate, validation and confirmation records are durable authorization facts."""
from sqlalchemy import Column, ForeignKey, String, Text, Table, UniqueConstraint
from app.chat.schema import metadata, identity

candidates = Table('moonbox_merge_candidates', metadata, *identity(),
    Column('space_id', String(64), nullable=False), Column('repository_id', String(64), nullable=False),
    Column('workspace_id', String(64), ForeignKey('moonbox_workspaces.id'), nullable=False),
    Column('main_workspace_id', String(64), ForeignKey('moonbox_workspaces.id'), nullable=False),
    Column('integration_workspace_id', String(64), ForeignKey('moonbox_workspaces.id')),
    Column('actor_id', String(64), nullable=False), Column('request_id', String(64), nullable=False),
    Column('change_id', String(128), nullable=False), Column('delivery_root', String(128), nullable=False),
    Column('sprint_id', String(64), nullable=False), Column('source_commit', String(64), nullable=False),
    Column('target_commit', String(64), nullable=False), Column('candidate_commit', String(64)),
    Column('target_ref', String(256), nullable=False), Column('governance_digest', String(64), nullable=False),
    Column('binding_revision', String(64), nullable=False), Column('runtime_digest', String(80)),
    Column('evidence_digest', String(64)), Column('fingerprint', String(64)),
    Column('state', String(32), nullable=False), Column('error_code', String(64)),
    Column('validation_result', Text, nullable=False),
    UniqueConstraint('workspace_id','actor_id','request_id',name='uq_moonbox_merge_candidate_request'))
operations = Table('moonbox_merge_operations', metadata, *identity(),
    Column('candidate_id', String(64), ForeignKey('moonbox_merge_candidates.id'), nullable=False, unique=True),
    Column('actor_id', String(64), nullable=False), Column('request_id', String(64), nullable=False),
    Column('confirmed_fingerprint', String(64), nullable=False),
    Column('capability_revision', String(64), nullable=False), Column('confirmed_at', String(32), nullable=False),
    Column('state', String(32), nullable=False), Column('actual_target', String(64)),
    Column('governance_state', String(24), nullable=False, default='pending'),
    Column('governance_plan', Text),
    Column('error_code', String(64)),
    UniqueConstraint('actor_id','request_id',name='uq_moonbox_merge_confirmation_request'))
TABLES = [candidates, operations]
