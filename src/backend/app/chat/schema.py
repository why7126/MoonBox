"""增量创建 Chat 表；只增不删，SQLite/MySQL 共用类型。"""
from sqlalchemy import Column, ForeignKey, Index, Integer, BigInteger, MetaData, String, Table, Text, UniqueConstraint

from sqlalchemy.dialects.mysql import LONGTEXT

LargeText = Text().with_variant(LONGTEXT(), "mysql")
metadata = MetaData()
# 外部事实源仅用于外键解析，不由本迁移创建或修改。
Table('admin_users', metadata, Column('id', String(64), primary_key=True))
Table('admin_spaces', metadata, Column('id', String(64), primary_key=True))

def identity():
    return [Column('id', String(64), primary_key=True), Column('created_at', String(32), nullable=False), Column('updated_at', String(32), nullable=False)]

conversations = Table('chat_conversations', metadata, *identity(),
    Column('owner_id', String(64), ForeignKey('admin_users.id'), nullable=False),
    Column('space_id', String(64), ForeignKey('admin_spaces.id'), nullable=False),
    Column('repository_id', String(64), nullable=False), Column('title', String(200), nullable=False),
    Column('branch_name', String(128), nullable=False, default='main'),
    Column('pinned', Integer, nullable=False, default=0), Column('archived', Integer, nullable=False, default=0),
    Column('deleted_at', String(32)), Column('active_turn_id', String(64)),
    Column('thread_id', String(128)), Column('workspace_id', String(64)),
    Column('generation', Integer, nullable=False, default=0),
    Column('cleanup_status', String(32), nullable=False, default='not_requested'))
Index('ix_chat_owner_space_activity', conversations.c.owner_id, conversations.c.space_id, conversations.c.updated_at)
turns = Table('chat_turns', metadata, *identity(),
    Column('conversation_id', String(64), ForeignKey('chat_conversations.id'), nullable=False),
    Column('client_request_id', String(64), nullable=False), Column('status', String(24), nullable=False),
    Column('prompt', LargeText, nullable=False), Column('retry_of', String(64)),
    Column('worker_id', String(64)), Column('generation', Integer, nullable=False, default=0),
    Column('heartbeat_at', String(32)), Column('executor_turn_id', String(128)),
    Column('error_code', String(64)), Column('reserved_bytes', BigInteger, nullable=False, default=0),
    Column('requested_config', Text, nullable=False, default='{}'),
    Column('effective_config', Text, nullable=False, default='{}'),
    Column('config_fallback_reason', String(200)),
    UniqueConstraint('conversation_id', 'client_request_id', name='uq_chat_request'))
Index('ix_chat_turn_queue', turns.c.status, turns.c.created_at)
events = Table('chat_events', metadata, *identity(),
    Column('turn_id', String(64), ForeignKey('chat_turns.id'), nullable=False),
    Column('sequence', Integer, nullable=False), Column('source_id', String(128), nullable=False),
    Column('event_type', String(64), nullable=False), Column('payload', LargeText, nullable=False),
    UniqueConstraint('turn_id', 'source_id', name='uq_chat_event_source'),
    UniqueConstraint('turn_id', 'sequence', name='uq_chat_event_cursor'))
messages = Table('chat_messages', metadata, *identity(),
    Column('turn_id', String(64), ForeignKey('chat_turns.id'), nullable=False),
    Column('role', String(24), nullable=False), Column('content', LargeText, nullable=False))
turn_materials = Table('chat_turn_materials', metadata, *identity(),
    Column('turn_id', String(64), ForeignKey('chat_turns.id'), nullable=False),
    Column('kind', String(24), nullable=False), Column('ordinal', Integer, nullable=False),
    Column('status', String(24), nullable=False), Column('name', String(200), nullable=False),
    Column('summary', LargeText, nullable=False), Column('mime_type', String(80)),
    Column('size_bytes', BigInteger, nullable=False, default=0), Column('ref_id', String(128)),
    Column('metadata', Text, nullable=False, default='{}'),
    UniqueConstraint('turn_id', 'kind', 'ordinal', name='uq_chat_turn_material_ordinal'))
Index('ix_chat_material_turn', turn_materials.c.turn_id, turn_materials.c.kind, turn_materials.c.ordinal)
uploaded_materials = Table('chat_uploaded_materials', metadata, *identity(),
    Column('actor_id', String(64), nullable=False), Column('space_id', String(64), nullable=False),
    Column('repository_id', String(64), nullable=False), Column('object_key', String(200), nullable=False),
    Column('kind', String(24), nullable=False), Column('name', String(200), nullable=False),
    Column('mime_type', String(80), nullable=False), Column('size_bytes', BigInteger, nullable=False),
    Column('status', String(24), nullable=False), Column('deleted_at', String(32)))
Index('ix_chat_uploaded_material_owner', uploaded_materials.c.actor_id, uploaded_materials.c.space_id, uploaded_materials.c.repository_id, uploaded_materials.c.status)
snapshots = Table('chat_context_snapshots', metadata, *identity(),
    Column('turn_id', String(64), ForeignKey('chat_turns.id'), nullable=False),
    Column('object_id', String(128), nullable=False), Column('version', String(128), nullable=False),
    Column('content', LargeText, nullable=False))
diffs = Table('chat_diff_snapshots', metadata, *identity(),
    Column('turn_id', String(64), ForeignKey('chat_turns.id'), nullable=False, unique=True),
    Column('before_hash', String(64), nullable=False), Column('after_hash', String(64), nullable=False),
    Column('payload', LargeText, nullable=False))
audit = Table('chat_request_logs', metadata, *identity(),
    Column('request_id', String(64), nullable=False), Column('actor_id', String(64)),
    Column('route_template', String(256), nullable=False), Column('method', String(12), nullable=False),
    Column('status_code', Integer, nullable=False), Column('duration_ms', Integer, nullable=False),
    Column('metadata', Text, nullable=False, default='{}'))

CHAT_TABLES = [conversations, turns, events, messages, turn_materials, uploaded_materials, snapshots, diffs, audit]

def migrate(engine):
    from app.governance.capture_schema import TABLES as capture_tables
    for table in capture_tables:
        if table not in CHAT_TABLES:
            CHAT_TABLES.append(table)
    metadata.create_all(engine, tables=CHAT_TABLES)
    from sqlalchemy import inspect, text
    with engine.begin() as connection:
        turn_columns = {column['name'] for column in inspect(connection).get_columns('chat_turns')}
        if 'requested_config' not in turn_columns:
            connection.execute(text("ALTER TABLE chat_turns ADD COLUMN requested_config TEXT NOT NULL DEFAULT '{}'"))
        if 'effective_config' not in turn_columns:
            connection.execute(text("ALTER TABLE chat_turns ADD COLUMN effective_config TEXT NOT NULL DEFAULT '{}'"))
        if 'config_fallback_reason' not in turn_columns:
            connection.execute(text('ALTER TABLE chat_turns ADD COLUMN config_fallback_reason VARCHAR(200)'))
        conversation_columns = {column['name'] for column in inspect(connection).get_columns('chat_conversations')}
        if 'branch_name' not in conversation_columns:
            connection.execute(text("ALTER TABLE chat_conversations ADD COLUMN branch_name VARCHAR(128) NOT NULL DEFAULT 'main'"))
        audit_columns = {column['name'] for column in inspect(connection).get_columns('chat_request_logs')}
        if 'metadata' not in audit_columns:
            connection.execute(text("ALTER TABLE chat_request_logs ADD COLUMN metadata TEXT NOT NULL DEFAULT '{}'"))
        columns = {column['name'] for column in inspect(connection).get_columns('chat_usage_reservations')}
        if 'concurrency_released' not in columns:
            connection.execute(text('ALTER TABLE chat_usage_reservations ADD COLUMN concurrency_released INTEGER NOT NULL DEFAULT 0'))
        # Earlier settlement already released its slot; never release it twice.
        connection.execute(text("UPDATE chat_usage_reservations SET concurrency_released=1 WHERE status='settled' AND concurrency_released=0"))
    # create_all does not add newly declared indexes to already-existing tables.
    for table in CHAT_TABLES:
        for index in table.indexes:
            index.create(engine, checkfirst=True)

# Capacity/concurrency accounts are global; token accounts are scoped to the reservation month.
usage_accounts = Table('chat_usage_accounts', metadata,
    Column('id', String(160), primary_key=True),
    Column('reserved_tokens', BigInteger, nullable=False, default=0),
    Column('used_tokens', BigInteger, nullable=False, default=0),
    Column('reserved_bytes', BigInteger, nullable=False, default=0),
    Column('used_bytes', BigInteger, nullable=False, default=0),
    Column('active_runs', Integer, nullable=False, default=0))
reservations = Table('chat_usage_reservations', metadata, *identity(),
    Column('turn_id', String(64), ForeignKey('chat_turns.id'), nullable=False, unique=True),
    Column('owner_id', String(64), nullable=False), Column('space_id', String(64), nullable=False),
    Column('period', String(7), nullable=False), Column('tokens', BigInteger, nullable=False),
    Column('bytes', BigInteger, nullable=False), Column('status', String(24), nullable=False),
    Column('concurrency_released', Integer, nullable=False, server_default='0'),
    Column('actual_tokens', BigInteger), Column('actual_bytes', BigInteger))
CHAT_TABLES.extend([usage_accounts, reservations])

workspace_baselines = Table('chat_workspace_baselines', metadata,
    Column('conversation_id', String(64), ForeignKey('chat_conversations.id'), primary_key=True),
    Column('workspace_id', String(64), nullable=False, unique=True),
    Column('content_hash', String(64), nullable=False), Column('payload', LargeText, nullable=False),
    Column('token_total', BigInteger, nullable=False, default=0))
CHAT_TABLES.append(workspace_baselines)
Index('ix_chat_turn_conversation_time', turns.c.conversation_id, turns.c.created_at)
Index('ix_chat_message_turn_time', messages.c.turn_id, messages.c.created_at)
Index('ix_chat_snapshot_turn_object', snapshots.c.turn_id, snapshots.c.object_id)

relations = Table('chat_relations', metadata,
    Column('conversation_id', String(64), ForeignKey('chat_conversations.id'), primary_key=True),
    Column('object_id', String(128), primary_key=True), Column('role', String(16), nullable=False),
    Column('title', String(200), nullable=False))
object_access = Table('chat_object_access', metadata,
    Column('space_id', String(64), primary_key=True), Column('repository_id', String(64), primary_key=True),
    Column('object_id', String(128), primary_key=True), Column('user_id', String(64), primary_key=True),
    Column('can_read', Integer, nullable=False, default=0))
CHAT_TABLES.extend([relations, object_access])

# First runtime instrumentation consumer; shared names follow the observability standard.
usage_events = Table('usage_events', metadata, *identity(),
    Column('behavior_event_id', String(64), nullable=False, unique=True),
    Column('event_name', String(64), nullable=False), Column('client_type', String(24), nullable=False),
    Column('actor_user_id', String(64)), Column('parent_request_id', String(64), nullable=False),
    Column('result', String(24), nullable=False), Column('properties', Text, nullable=False))
task_traces = Table('task_traces', metadata, *identity(),
    Column('task_trace_id', String(64), nullable=False, unique=True),
    Column('turn_id', String(64), nullable=False, unique=True), Column('parent_request_id', String(64)),
    Column('task_type', String(64), nullable=False), Column('task_name', String(64), nullable=False),
    Column('actor_user_id', String(64)), Column('status', String(24), nullable=False),
    Column('finished_at', String(32)), Column('metadata', Text, nullable=False))
task_trace_spans = Table('task_trace_spans', metadata, *identity(),
    Column('task_trace_id', String(64), nullable=False), Column('span_name', String(64), nullable=False),
    Column('status', String(24), nullable=False), Column('metadata', Text, nullable=False))
Index('ix_chat_trace_turn', task_traces.c.turn_id)
Index('ix_chat_span_trace_time', task_trace_spans.c.task_trace_id, task_trace_spans.c.created_at)
CHAT_TABLES.extend([usage_events,task_traces,task_trace_spans])

cleanup_jobs = Table('chat_cleanup_jobs',metadata,*identity(),
    Column('conversation_id',String(64),nullable=False,unique=True),Column('owner_id',String(64),nullable=False),
    Column('workspace_hash',String(64)),Column('executor_thread_id',String(128)),
    Column('main_status',String(24),nullable=False),Column('executor_status',String(24),nullable=False),
    Column('backup_status',String(24),nullable=False),Column('executor_due_at',String(32)),Column('backup_due_at',String(32)))
CHAT_TABLES.append(cleanup_jobs)

# REQ-0022: immutable governance candidates and durable single-writer operations.
governance_candidates = Table('governance_candidates',metadata,*identity(),
    Column('actor_id',String(64),ForeignKey('admin_users.id'),nullable=False),
    Column('space_id',String(64),ForeignKey('admin_spaces.id'),nullable=False),
    Column('repository_id',String(64),nullable=False),Column('scope_key',String(64),nullable=False),
    Column('conversation_id',String(64),ForeignKey('chat_conversations.id'),nullable=False),
    Column('turn_id',String(64),ForeignKey('chat_turns.id'),unique=True),
    Column('object_id',String(128),nullable=False),Column('action',String(32),nullable=False),
    Column('binding_revision',String(64),nullable=False),Column('baseline_hash',String(64),nullable=False),
    Column('manifest_hash',String(64)),Column('revision',Integer,nullable=False,default=1),
    Column('state',String(32),nullable=False),Column('error_code',String(64)),
    Column('prepared_turn_id',String(64)))
Index('ix_governance_candidate_conversation',governance_candidates.c.conversation_id,governance_candidates.c.created_at)
governance_applications = Table('governance_applications',metadata,*identity(),
    Column('candidate_id',String(64),ForeignKey('governance_candidates.id'),unique=True),
    Column('actor_id',String(64),ForeignKey('admin_users.id'),nullable=False),
    Column('space_id',String(64),nullable=False),Column('repository_id',String(64),nullable=False),
    Column('scope_key',String(64),nullable=False),Column('idempotency_key',String(64),nullable=False),
    Column('request_id',String(64)),Column('request_hash',String(64),nullable=False),
    Column('state',String(32),nullable=False),Column('phase',String(64),nullable=False),
    Column('fencing_token',BigInteger),Column('worker_id',String(64)),Column('error_code',String(64)),
    UniqueConstraint('actor_id','scope_key','idempotency_key',name='uq_governance_application_request'))
Index('ix_governance_application_queue',governance_applications.c.state,governance_applications.c.created_at)
governance_project_locks = Table('governance_project_locks',metadata,
    Column('scope_key',String(64),primary_key=True),Column('operation_id',String(64)),
    Column('fencing_token',BigInteger,nullable=False,default=0),Column('worker_id',String(64)),
    Column('updated_at',String(32),nullable=False))
CHAT_TABLES.extend([governance_candidates,governance_applications,governance_project_locks])
