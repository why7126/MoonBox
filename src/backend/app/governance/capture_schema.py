"""Capture business drafts are separate from formal Issue and PRD candidates."""
from sqlalchemy import Column, Integer, BigInteger, String, Table, UniqueConstraint, Index
from app.chat.schema import metadata, identity, LargeText

drafts = Table('capture_drafts', metadata, *identity(),
    Column('actor_id', String(64), nullable=False), Column('space_id', String(64), nullable=False),
    Column('repository_id', String(64), nullable=False), Column('scope_key', String(64), nullable=False),
    Column('binding_revision', String(64), nullable=False), Column('revision', Integer, nullable=False),
    Column('state', String(24), nullable=False), Column('payload', LargeText, nullable=False),
    Column('confirmed_task_id', String(64)), Column('deleted_at', String(32)))
Index('ix_capture_draft_owner_project', drafts.c.actor_id, drafts.c.scope_key, drafts.c.state)
revisions = Table('capture_revisions', metadata, *identity(),
    Column('draft_id', String(64), nullable=False), Column('revision', Integer, nullable=False),
    Column('payload', LargeText, nullable=False),
    UniqueConstraint('draft_id', 'revision', name='uq_capture_revision'))
quotas = Table('capture_quotas', metadata,
    Column('actor_id', String(64), primary_key=True), Column('scope_key', String(64), primary_key=True),
    Column('draft_count', Integer, nullable=False), Column('material_bytes', BigInteger, nullable=False))
materials = Table('capture_materials', metadata, *identity(),
    Column('draft_id', String(64), nullable=False), Column('actor_id', String(64), nullable=False),
    Column('scope_key', String(64), nullable=False), Column('object_key', String(200), nullable=False),
    Column('mime_type', String(64), nullable=False), Column('size', BigInteger, nullable=False),
    Column('width', Integer, nullable=False), Column('height', Integer, nullable=False),
    Column('state', String(24), nullable=False), Column('deleted_at', String(32)))
confirmations = Table('capture_confirmations', metadata, *identity(),
    Column('draft_id', String(64), nullable=False, unique=True), Column('revision', Integer, nullable=False),
    Column('actor_id', String(64), nullable=False), Column('scope_key', String(64), nullable=False),
    Column('snapshot_hash', String(64), nullable=False), Column('payload', LargeText, nullable=False),
    Column('idempotency_hash', String(64), nullable=False), Column('operation_id', String(64)),
    Column('state', String(24), nullable=False),
    UniqueConstraint('scope_key','draft_id','revision',name='uq_capture_confirmation_version'))
Index('uq_capture_confirmation_key', confirmations.c.actor_id, confirmations.c.scope_key, confirmations.c.idempotency_hash, unique=True)
links = Table('capture_issue_links', metadata, *identity(),
    Column('task_id', String(64), nullable=False), Column('candidate_id', String(64), nullable=False),
    Column('scope_key', String(64), nullable=False), Column('issue_id', String(128), nullable=False),
    UniqueConstraint('task_id','candidate_id',name='uq_capture_candidate_issue'),
    UniqueConstraint('scope_key','issue_id',name='uq_capture_project_issue'))
organize_tasks = Table('capture_organize_tasks', metadata, *identity(),
    Column('draft_id', String(64), nullable=False), Column('revision', Integer, nullable=False),
    Column('actor_id', String(64), nullable=False), Column('state', String(24), nullable=False),
    Column('result', LargeText), Column('error_code', String(64)), Column('request_id', String(64)))
confirmation_keys = Table('capture_confirmation_keys', metadata,
    Column('actor_id', String(64), primary_key=True), Column('scope_key', String(64), primary_key=True),
    Column('key_hash', String(64), primary_key=True), Column('task_id', String(64), nullable=False))
TABLES = [drafts, revisions, quotas, materials, confirmations, links, organize_tasks, confirmation_keys]
