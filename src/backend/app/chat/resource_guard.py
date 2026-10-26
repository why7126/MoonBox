"""Deployment safeguards; these are not user or space operating quotas."""
import errno
import shutil
from pathlib import Path
from sqlalchemy.exc import OperationalError
from app.chat.app_server import ExecutorError

DISK_RESERVE_BYTES = 256 * 1024 * 1024


def lock_budget(db):
    """Apply a worker-only five-second lock wait; restore pooled connections."""
    from sqlalchemy import event
    connection = db.connection()
    engine = connection.engine
    dialect = engine.dialect.name
    if dialect not in ('sqlite', 'mysql'): return
    if not event.contains(engine.pool, 'checkin', _restore_lock_budget):
        event.listen(engine.pool, 'checkin', _restore_lock_budget)
    if 'chat_lock_restore' in connection.info: return
    query = 'PRAGMA busy_timeout' if dialect == 'sqlite' else 'SELECT @@SESSION.innodb_lock_wait_timeout'
    previous = int(connection.exec_driver_sql(query).scalar())
    connection.info['chat_lock_restore'] = (dialect, previous)
    connection.exec_driver_sql('PRAGMA busy_timeout=5000' if dialect == 'sqlite'
                              else 'SET SESSION innodb_lock_wait_timeout=5')


def _restore_lock_budget(connection, record):
    previous = record.info.pop('chat_lock_restore', None)
    if connection is None or previous is None: return
    dialect, value = previous
    cursor = connection.cursor()
    try:
        cursor.execute(f'PRAGMA busy_timeout={value}' if dialect == 'sqlite'
                       else f'SET SESSION innodb_lock_wait_timeout={value}')
    finally: cursor.close()


def require_disk(path):
    if shutil.disk_usage(path).free < DISK_RESERVE_BYTES:
        raise ExecutorError('workspace_resource_exhausted')


def require_database_disk(db):
    url = db.get_bind().url
    if url.get_backend_name() == 'sqlite' and url.database and url.database != ':memory:':
        require_disk(Path(url.database).absolute().parent)


def classify(error):
    if isinstance(error, OSError) and error.errno in (errno.ENOSPC, errno.EDQUOT, errno.ENOMEM):
        return 'workspace_resource_exhausted'
    if isinstance(error, OperationalError):
        return 'result_persistence_failed'
    return 'execution_internal_error'
