"""Durable control facts; secrets and executable plans stay outside public records."""
from sqlalchemy import BigInteger, Column, Index, Integer, String, Table, Text, UniqueConstraint
from app.chat.schema import metadata, identity

operations = Table('verification_operations', metadata, *identity(),
    Column('actor_id',String(64),nullable=False), Column('space_id',String(64),nullable=False),
    Column('repository_id',String(64),nullable=False), Column('conversation_id',String(64),nullable=False),
    Column('source_turn_id',String(64),nullable=False), Column('change_id',String(128),nullable=False),
    Column('request_hash',String(64),nullable=False), Column('binding_revision',String(64),nullable=False),
    Column('input_digest',String(64),nullable=False), Column('plan_json',Text,nullable=False),
    Column('source_ref_json',Text,nullable=False,default='{}'),
    Column('status',String(32),nullable=False), Column('version',Integer,nullable=False),
    Column('cancel_requested',Integer,nullable=False), Column('resume_count',Integer,nullable=False),
    Column('attempt_id',String(64),nullable=False), Column('queued_at',Integer,nullable=False),
    Column('expires_at',Integer), Column('checks_deadline',Integer), Column('cleanup_state',String(32),nullable=False),
    Column('reason_code',String(80)),
    UniqueConstraint('actor_id','space_id','repository_id','source_turn_id','request_hash',name='uq_acceptance_request'))
Index('ix_acceptance_scope',operations.c.space_id,operations.c.repository_id,operations.c.source_turn_id)
Index('ix_acceptance_queue',operations.c.status,operations.c.queued_at)
attempts = Table('verification_attempts',metadata,*identity(),
    Column('operation_id',String(64),nullable=False), Column('sequence',Integer,nullable=False),
    Column('epoch',Integer,nullable=False), Column('worker_id',String(64)),
    Column('lease_until',Integer,nullable=False), Column('input_digest',String(64),nullable=False),
    Column('state',String(32),nullable=False), Column('environment_id',String(64)),
    Column('template_digest',String(64)), Column('expires_at',Integer),
    UniqueConstraint('operation_id','sequence',name='uq_acceptance_attempt'))
Index('ix_acceptance_lease',attempts.c.state,attempts.c.lease_until)
steps = Table('verification_environment_steps',metadata,*identity(),
    Column('attempt_id',String(64),nullable=False), Column('step_key',String(128),nullable=False),
    Column('epoch',Integer,nullable=False), Column('status',String(32),nullable=False),
    Column('facts_json',Text,nullable=False),
    UniqueConstraint('attempt_id','step_key',name='uq_acceptance_step'))
results = Table('verification_ac_results',metadata,*identity(),
    Column('attempt_id',String(64),nullable=False), Column('ac_id',String(64),nullable=False),
    Column('input_digest',String(64),nullable=False), Column('status',String(24),nullable=False),
    Column('evidence_json',Text,nullable=False), Column('reason_code',String(80)),
    UniqueConstraint('attempt_id','ac_id',name='uq_acceptance_ac'))
identities = Table('verification_identity_refs',metadata,*identity(),
    Column('attempt_id',String(64),nullable=False),Column('identity_ref',String(64),nullable=False),
    Column('role',String(32),nullable=False),Column('expires_at',Integer,nullable=False),
    Column('revocation_state',String(32),nullable=False),
    UniqueConstraint('attempt_id','identity_ref',name='uq_acceptance_identity'))
reservations = Table('verification_resource_reservations',metadata,
    Column('slot',Integer,primary_key=True), Column('operation_id',String(64),nullable=False,unique=True),
    Column('space_id',String(64),nullable=False,unique=True),
    Column('cpu_millis',Integer,nullable=False), Column('memory_bytes',BigInteger,nullable=False),
    Column('disk_bytes',BigInteger,nullable=False), Column('evidence_bytes',BigInteger,nullable=False),
    Column('expires_at',Integer,nullable=False))
deliveries = Table('verification_result_deliveries',metadata,*identity(),
    Column('operation_id',String(64),nullable=False,unique=True),
    Column('attempt_id',String(64),nullable=False), Column('input_digest',String(64),nullable=False),
    Column('state',String(24),nullable=False), Column('mode',String(24)),
    Column('target_turn_id',String(64)), Column('reason_code',String(80)))
archives = Table('verification_evidence_archives',metadata,*identity(),
    Column('operation_id',String(64),nullable=False),Column('attempt_id',String(64),nullable=False,unique=True),
    Column('digest',String(64),nullable=False),Column('relative_path',String(512),nullable=False),
    Column('manifest_json',Text,nullable=False),Column('state',String(24),nullable=False))
tool_waits = Table('verification_tool_waits',metadata,*identity(),
    Column('source_turn_id',String(64),nullable=False,unique=True),
    Column('call_id',String(128),nullable=False),Column('generation',Integer,nullable=False),
    Column('point_id',String(64)),Column('operation_id',String(64)),
    Column('state',String(24),nullable=False))
TABLES=[operations,attempts,steps,results,identities,reservations,deliveries,archives,tool_waits]
