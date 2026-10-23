"""Additive authorization ledger; intentionally excluded from telemetry cleanup."""
from sqlalchemy import Column, Integer, String, Table, UniqueConstraint
from app.chat.schema import metadata, identity, LargeText
from app.governance.recovery_schema import REQUEST_KEY

proposals = Table('replacement_proposals', metadata, *identity(),
    Column('scope_key', String(64), nullable=False), Column('space_id', String(64), nullable=False),
    Column('repository_id', String(64), nullable=False), Column('binding_revision', String(64), nullable=False),
    Column('change_id', String(128), nullable=False), Column('digest', String(64), nullable=False),
    Column('body', LargeText, nullable=False), Column('prepared_by', String(64), nullable=False),
    Column('revision', Integer, nullable=False), Column('state', String(24), nullable=False),
    Column('owner_id', String(64)), Column('expires_at', String(32)),
    Column('receipt', LargeText), Column('operation_id', String(64)),
    UniqueConstraint('scope_key', 'digest', name='uq_replacement_proposal_digest'))
events = Table('replacement_authorization_events', metadata, *identity(),
    Column('scope_key', String(64), nullable=False), Column('proposal_id', String(64), nullable=False),
    Column('actor_id', String(64), nullable=False), Column('purpose', String(32), nullable=False),
    Column('request_key', REQUEST_KEY, nullable=False), Column('request_hash', String(64), nullable=False),
    Column('revision', Integer, nullable=False), Column('receipt', LargeText, nullable=False),
    UniqueConstraint('scope_key', 'request_key', name='uq_replacement_event_request'),
    UniqueConstraint('proposal_id', 'revision', name='uq_replacement_event_revision'))
activations = Table('policy_activation_operations', metadata, *identity(),
    Column('scope_key', String(64), nullable=False, unique=True),
    Column('binding_revision', String(64), nullable=False), Column('policy_version', String(64), nullable=False),
    Column('state', String(24), nullable=False), Column('manifest_hash', String(64), nullable=False),
    Column('manifest', LargeText, nullable=False), Column('ops_receipt', LargeText),
    Column('owner_receipt', LargeText), Column('operation_id', String(64)),
    Column('revision', Integer, nullable=False), Column('archive_hash', String(64)),
    Column('stage', String(24), nullable=False, default='prepared'),
    Column('fence', Integer, nullable=False, default=0), Column('lease_until', String(32)),
    Column('input_hash', String(64)))
commits = Table('replacement_archive_operations', metadata, *identity(),
    Column('scope_key', String(64), nullable=False), Column('proposal_id', String(64), nullable=False, unique=True),
    Column('actor_id', String(64), nullable=False), Column('stage', String(24), nullable=False),
    Column('fence', Integer, nullable=False), Column('lease_until', String(32), nullable=False),
    Column('input_hash', String(64), nullable=False), Column('expected_hash', String(64), nullable=False),
    Column('observed_hash', String(64)), Column('revision', Integer, nullable=False))
archive_operations = Table('governance_archive_operations', metadata, *identity(),
    Column('scope_key', String(64), nullable=False), Column('binding_revision', String(64), nullable=False),
    Column('change_id', String(128), nullable=False), Column('actor_id', String(64), nullable=False),
    Column('stage', String(24), nullable=False), Column('manifest', LargeText, nullable=False),
    Column('fence', Integer, nullable=False), Column('lease_until', String(32), nullable=False),
    Column('revision', Integer, nullable=False),
    UniqueConstraint('scope_key', 'change_id', name='uq_governance_archive_change'))
TABLES = (proposals, events, activations, commits, archive_operations)


def install_audit_guards(engine):
    """Database-enforced append-only events, also on an existing additive schema."""
    from sqlalchemy import text,inspect
    with engine.begin() as connection:
        columns={column['name'] for column in inspect(connection).get_columns('policy_activation_operations')}
        for name,definition in {'stage':"VARCHAR(24) NOT NULL DEFAULT 'prepared'",'fence':'INTEGER NOT NULL DEFAULT 0',
                               'lease_until':'VARCHAR(32)','input_hash':'VARCHAR(64)'}.items():
            if name not in columns:
                connection.execute(text(f'ALTER TABLE policy_activation_operations ADD COLUMN {name} {definition}'))
        dialect=engine.dialect.name
        if dialect=='sqlite':
            existing=set(connection.execute(text("SELECT name FROM sqlite_master WHERE type='trigger'")).scalars())
        elif dialect=='mysql':
            existing=set(connection.execute(text('SELECT TRIGGER_NAME FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA=DATABASE()')).scalars())
        else:
            raise ValueError('unsupported_authorization_database')
        for operation in ('UPDATE','DELETE'):
            name='replacement_events_no_'+operation.lower()
            if name in existing: continue
            body="SELECT RAISE(ABORT, 'authorization events are immutable');" if dialect=='sqlite' else "SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'authorization events are immutable';"
            connection.execute(text(f'CREATE TRIGGER {name} BEFORE {operation} ON replacement_authorization_events FOR EACH ROW BEGIN {body} END'))
        for operation in ('UPDATE','DELETE'):
            name='rule_change_events_no_'+operation.lower()
            if name in existing: continue
            body="SELECT RAISE(ABORT, 'rule change events are immutable');" if dialect=='sqlite' else "SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'rule change events are immutable';"
            connection.execute(text(f'CREATE TRIGGER {name} BEFORE {operation} ON governance_rule_change_events FOR EACH ROW BEGIN {body} END'))
