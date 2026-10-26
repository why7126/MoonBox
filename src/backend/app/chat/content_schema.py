"""Version two content storage; additive SQLite/MySQL schema."""
from sqlalchemy import BigInteger, Column, ForeignKey, Index, Integer, LargeBinary, String, Table, Text, UniqueConstraint
from app.chat.schema import metadata, identity
from sqlalchemy.dialects.mysql import MEDIUMBLOB

objects = Table('chat_content_objects', metadata, *identity(),
    Column('conversation_id', String(64), ForeignKey('chat_conversations.id'), nullable=False),
    Column('format_version', Integer, nullable=False, default=2),
    Column('kind', String(24), nullable=False), Column('status', String(24), nullable=False),
    Column('sha256', String(64)), Column('byte_count', BigInteger, nullable=False, default=0))
Index('ix_chat_content_lookup', objects.c.conversation_id, objects.c.sha256, objects.c.status)
chunks = Table('chat_content_chunks', metadata,
    Column('object_id', String(64), ForeignKey('chat_content_objects.id'), primary_key=True),
    Column('chunk_no', BigInteger, primary_key=True), Column('payload', LargeBinary().with_variant(MEDIUMBLOB(), 'mysql'), nullable=False),
    Column('byte_count', Integer, nullable=False), Column('sha256', String(64), nullable=False))
versions = Table('chat_snapshot_versions', metadata, *identity(),
    Column('conversation_id', String(64), ForeignKey('chat_conversations.id'), nullable=False),
    Column('turn_id', String(64), ForeignKey('chat_turns.id'), nullable=False),
    Column('phase', String(16), nullable=False), Column('parent_version', String(64)),
    Column('scan_cursor', Text), Column('status', String(24), nullable=False),
    Column('manifest_hash', String(64)))
Index('ix_chat_snapshot_version_turn', versions.c.turn_id, versions.c.phase, versions.c.status)
entries = Table('chat_snapshot_entries', metadata,
    Column('version_id', String(64), ForeignKey('chat_snapshot_versions.id'), primary_key=True),
    Column('path_key', String(64), primary_key=True), Column('path', Text, nullable=False),
    Column('kind', String(16), nullable=False), Column('mode', Integer, nullable=False),
    Column('digest', String(64), nullable=False), Column('byte_count', BigInteger, nullable=False),
    Column('verified', Integer, nullable=False, default=0),
    Column('object_id', String(64), ForeignKey('chat_content_objects.id')))
Index('ix_chat_snapshot_digest', entries.c.version_id, entries.c.digest, entries.c.kind, entries.c.mode)
segments = Table('chat_result_segments', metadata, *identity(),
    Column('turn_id', String(64), ForeignKey('chat_turns.id'), nullable=False),
    Column('stream_id', String(24), nullable=False), Column('source_event_id', String(64), nullable=False),
    Column('source_offset', BigInteger, nullable=False), Column('sequence', BigInteger, nullable=False),
    Column('object_id', String(64), ForeignKey('chat_content_objects.id'), nullable=False),
    UniqueConstraint('turn_id', 'stream_id', 'source_event_id', 'source_offset', name='uq_chat_segment_source'),
    UniqueConstraint('turn_id', 'sequence', name='uq_chat_segment_sequence'))
ledger = Table('chat_storage_ledger', metadata,
    Column('event_id', String(64), primary_key=True),
    Column('conversation_id', String(64), ForeignKey('chat_conversations.id'), nullable=False),
    Column('object_id', String(64), nullable=False), Column('delta_bytes', BigInteger, nullable=False),
    Column('created_at', String(32), nullable=False))
prepare_attempts = Table('chat_prepare_attempts', metadata, *identity(),
    Column('turn_id', String(64), ForeignKey('chat_turns.id'), nullable=False),
    Column('request_key', String(64), nullable=False), Column('generation', Integer, nullable=False),
    Column('prior_status', String(24), nullable=False), Column('prior_error', String(64)),
    Column('prior_bytes', BigInteger, nullable=False, default=0),
    Column('state', String(24), nullable=False), Column('request_id', String(64)),
    UniqueConstraint('turn_id', 'request_key', name='uq_chat_prepare_request'))
TABLES = [objects, chunks, versions, entries, segments, ledger, prepare_attempts]
