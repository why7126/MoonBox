"""Recovery metadata references the existing chunk-backed snapshot store."""
from sqlalchemy import Column, ForeignKey, Integer, String, Table, UniqueConstraint, Text, BigInteger
from app.chat.schema import metadata, identity

points = Table('moonbox_recovery_points', metadata, *identity(),
    Column('workspace_id', String(64), ForeignKey('moonbox_workspaces.id'), nullable=False),
    Column('sequence', Integer, nullable=False),
    Column('version_id', String(64), nullable=False),
    Column('manifest_hash', String(64), nullable=False),
    Column('policy_version', String(64), nullable=False),
    Column('scope_json', Text),
    Column('change_id', String(255)),
    Column('head_commit', String(64), nullable=False),
    Column('state', String(24), nullable=False),
    Column('changed', Integer, nullable=False),
    UniqueConstraint('workspace_id', 'sequence', name='uq_moonbox_recovery_sequence'))
references = Table('moonbox_recovery_references', metadata,
    Column('workspace_id', String(64), ForeignKey('moonbox_workspaces.id'), primary_key=True),
    Column('owner_type', String(32), primary_key=True),
    Column('owner_id', String(128), primary_key=True),
    Column('point_id', String(64), ForeignKey('moonbox_recovery_points.id'), nullable=False),
    Column('protection_reason', String(64)))
entries = Table('moonbox_recovery_entries', metadata,
    Column('point_id', String(64), ForeignKey('moonbox_recovery_points.id'), primary_key=True),
    Column('path_key', String(64), primary_key=True),
    Column('path', Text, nullable=False),
    Column('kind', String(16), nullable=False),
    Column('mode', Integer, nullable=False),
    Column('digest', String(64), nullable=False),
    Column('byte_count', BigInteger, nullable=False),
    Column('object_id', String(64), ForeignKey('chat_content_objects.id')))
operations = Table('moonbox_restore_operations', metadata, *identity(),
    Column('workspace_id', String(64), ForeignKey('moonbox_workspaces.id'), nullable=False),
    Column('actor_id', String(64), nullable=False),
    Column('request_id', String(64), nullable=False),
    Column('request_digest', String(64), nullable=False),
    Column('before_id', String(64), nullable=False), Column('after_id', String(64), nullable=False),
    Column('current_digest', String(64), nullable=False),
    Column('state', String(24), nullable=False), Column('plan', Text, nullable=False),
    Column('error_code', String(64)),
    UniqueConstraint('workspace_id','actor_id','request_id',name='uq_moonbox_restore_request'))
steps = Table('moonbox_restore_steps', metadata,
    Column('operation_id', String(64), ForeignKey('moonbox_restore_operations.id'), primary_key=True),
    Column('path_key', String(64), primary_key=True),
    Column('state', String(24), nullable=False))
snapshot_points = Table('moonbox_snapshot_points', metadata,
    Column('version_id', String(64), ForeignKey('chat_snapshot_versions.id'), primary_key=True),
    Column('point_id', String(64), ForeignKey('moonbox_recovery_points.id'), nullable=False))
TABLES = [points, references, entries, operations, steps, snapshot_points]
