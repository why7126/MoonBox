"""Plan guard mutations without a write transaction; apply them behind fresh fences.

Only reconciliation uses this adapter. It is not a general Session replacement:
SQL reads are materialized and their transactions ended immediately; guard DML
is recorded, never executed while filesystem verification is running.
"""
from contextlib import nullcontext
from types import SimpleNamespace
import logging
import time
from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.sql.dml import Update, Insert
from sqlalchemy.sql.elements import TextClause
from app.chat import service
from app.governance import execution_guard as guards, scope


class StaleVerification(Exception):
    pass


def lock_code(error):
    if not isinstance(error, OperationalError):
        return None
    original = error.orig
    code = getattr(original, 'sqlite_errorcode', None)
    if isinstance(code, int) and code & 255 in (5, 6):
        return code
    args = getattr(original, 'args', ())
    return args[0] if args and args[0] in (1205, 1213) else None


def diagnostic(event, *, operation_id=None, code=None, attempt=1, started=None):
    # Never log exception text/SQL/parameters. Logging must not break recovery.
    try:
        logging.getLogger('moonbox.governance.transaction').info(
            'verification_transaction event=%s operation_id=%s code=%s attempt=%s duration_ms=%s',
            event, operation_id, code, attempt,
            round((time.monotonic() - started) * 1000, 2) if started else None)
    except Exception:
        pass


class VerificationPlan:
    def __init__(self, db):
        self.db = db
        self.statements = []

    def execute(self, statement, *args, **kwargs):
        if isinstance(statement, (Update, Insert)):
            if statement.table.name not in ('governance_execution_guards', 'task_trace_spans'):
                raise ValueError('unsupported verification mutation')
            self.statements.append((statement, args, kwargs))
            return SimpleNamespace(rowcount=1)
        if not getattr(statement, "is_select", False) and not (
                isinstance(statement, TextClause) and str(statement).lstrip().upper().startswith("SELECT ")):
            raise ValueError("verification planning only permits reads")
        result = self.db.execute(statement, *args, **kwargs).freeze()
        self.db.rollback()
        return result()

    def scalar(self, statement, *args, **kwargs):
        return self.execute(statement, *args, **kwargs).scalar()

    def scalars(self, statement, *args, **kwargs):
        return self.execute(statement, *args, **kwargs).scalars()

    def begin_nested(self):
        return nullcontext()

    def apply(self, *, actor, project, expected, turn=None, expected_epoch=None, expected_batch=None):
        if not self.statements:
            return False
        from app.chat.schema import turns
        g = guards.execution_guards.c
        deadline = time.monotonic() + 1
        for attempt in range(1, 4):
            started = time.monotonic()
            committing = False
            try:
                from app.chat.resource_guard import lock_budget
                lock_budget(self.db, seconds=0.2)
                current_scope = scope.authorize(self.db, actor, project.space_id, project.repository_id,
                                                write=not project.readonly)
                if current_scope.binding_revision != project.binding_revision:
                    raise StaleVerification()
                from app.governance.writer import epoch, assert_readable
                assert_readable(self.db, current_scope)
                if expected_epoch is not None and epoch(self.db, current_scope) != expected_epoch:
                    raise StaleVerification()
                current_rows = []
                for item in expected_batch or [expected]:
                    oid = item['object_id']
                    if not scope.visible(self.db, actor, current_scope, oid):
                        raise StaleVerification()
                    current = guards.read(self.db, project.key, oid)
                    if (dict(current) if current else None) != item.get('_row'):
                        raise StaleVerification()
                    current_rows.append((oid, current))
                if turn:
                    current_turn = self.db.execute(select(turns).where(turns.c.id == turn['id'])).mappings().first()
                    if not current_turn or current_turn['status'] != turn['status']:
                        raise StaleVerification()
                # CAS acquires the write fence only AFTER all file work. On
                # SQLite a concurrent writer gets BUSY; on MySQL the predicate
                # is re-evaluated after waiting for the row lock.
                for oid, current in current_rows:
                    if current:
                        conditions = [g.scope_key == project.key, g.object_id == oid]
                        conditions.extend(g[key] == value for key, value in dict(current).items())
                        locked = self.db.execute(guards.execution_guards.update().where(*conditions)
                                                 .values(version=g.version))
                        if locked.rowcount != 1:
                            raise StaleVerification()
                for statement, args, kwargs in self.statements:
                    if statement.table.name == "task_trace_spans":
                        try:
                            with self.db.begin_nested():
                                self.db.execute(statement, *args, **kwargs)
                        except Exception:
                            diagnostic("span_unavailable")
                        continue
                    result = self.db.execute(statement, *args, **kwargs)
                    if isinstance(statement, Update) and result.rowcount != 1:
                        raise StaleVerification()
                committing = True
                self.db.commit()
                diagnostic('committed', operation_id=turn['id'] if turn else None,
                           attempt=attempt, started=started)
                return True
            except StaleVerification:
                self.db.rollback()
                diagnostic('stale', operation_id=turn['id'] if turn else None, started=started)
                return False
            except OperationalError as error:
                self.db.rollback()
                code = lock_code(error)
                diagnostic('commit_unknown' if committing else 'database_error',
                           operation_id=turn['id'] if turn else None, code=code,
                           attempt=attempt, started=started)
                # Commit ambiguity is never retried: the next read checks the
                # durable guard, and no model/command side effect is replayed.
                delay = (0.05, 0.15)[min(attempt - 1, 1)]
                if committing or code is None or attempt == 3 or time.monotonic() + delay >= deadline:
                    raise
                time.sleep(delay)
            except Exception:
                self.db.rollback()
                raise
