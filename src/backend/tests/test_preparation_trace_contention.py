"""Two independent preparation traces must not lose spans on SQLite upgrade races."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import pytest
from sqlalchemy import event, select
from app.governance.observability import trace
from app.chat.schema import task_trace_spans
from test_chat import chat


def test_prepared_traces_serialize_before_reading_sqlite_snapshot(chat, caplog):
    _, factory = chat
    with factory() as db:
        engine = db.get_bind()
        if engine.dialect.name != 'sqlite':
            pytest.skip('SQLite deferred read-to-write upgrade regression')
        for oid in ('trace-one', 'trace-two'):
            trace(db, oid, 'prepared'); db.commit()
    overlap = Barrier(2)
    def after_sql(conn, cursor, statement, params, context, many):
        sql = statement.lstrip().lower()
        if sql.startswith(('update ', 'insert ')):
            conn.info['trace_test_write'] = True
        if sql.startswith('select ') and 'task_traces' in sql and not conn.info.get('trace_test_write'):
            # Reproduce the old interleaving: both deferred transactions have
            # read their snapshot before either requests the SQLite write lock.
            overlap.wait(timeout=3)
    event.listen(engine, 'after_cursor_execute', after_sql)
    def prepared(oid):
        with factory() as db:
            db.connection().info['trace_test_write'] = False
            trace(db, oid, 'prepared', serialize_sqlite=True)
            db.commit()
    try:
        with ThreadPoolExecutor(max_workers=2) as workers:
            list(workers.map(prepared, ('trace-one', 'trace-two')))
    finally:
        event.remove(engine, 'after_cursor_execute', after_sql)
    assert 'governance.trace_unavailable' not in caplog.text
    with factory() as db:
        assert len(db.execute(select(task_trace_spans)).all()) == 4


@pytest.mark.parametrize('dialect,enabled,first_verb', [('sqlite', True, 'UPDATE'), ('mysql', True, 'SELECT'), ('sqlite', False, 'SELECT')])
def test_sqlite_preparation_option_keeps_other_dialects_and_callers_unchanged(chat, dialect, enabled, first_verb):
    from types import SimpleNamespace
    _, factory = chat
    statements = []
    with factory() as db:
        class Facade:
            def get_bind(self): return SimpleNamespace(dialect=SimpleNamespace(name=dialect))
            def __getattr__(self, name): return getattr(db, name)
            def execute(self, statement):
                statements.append(str(statement).split()[0])
                return db.execute(statement)
        trace(Facade(), 'new-trace', 'prepared', serialize_sqlite=enabled)
        db.commit()
        assert statements[0] == first_verb
        assert len(db.execute(select(task_trace_spans)).all()) == 1
