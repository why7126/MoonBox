"""Deployment safeguards; these are not user or space operating quotas."""
import errno
import shutil
from pathlib import Path
from sqlalchemy.exc import OperationalError
from app.chat.app_server import ExecutorError

DISK_RESERVE_BYTES = 256 * 1024 * 1024


def lock_budget(db, *, seconds=5):
    """Apply a bounded lock wait; restore pooled connections on checkin."""
    from sqlalchemy import event
    from sqlalchemy.pool import Pool
    connection = db.connection()
    engine = connection.engine
    dialect = engine.dialect.name
    if dialect not in ('sqlite', 'mysql'): return
    # Register on the stable Pool class. Short-lived pool identities can be reused
    # before SQLAlchemy's weak event registry is collected: contains(instance)
    # may then report an old registration while its actual dispatch list is empty.
    if not event.contains(Pool, 'checkin', _restore_lock_budget):
        event.listen(Pool, 'checkin', _restore_lock_budget)
    if 'chat_lock_restore' in connection.info: return
    query = 'PRAGMA busy_timeout' if dialect == 'sqlite' else 'SELECT @@SESSION.innodb_lock_wait_timeout'
    previous = int(connection.exec_driver_sql(query).scalar())
    connection.info['chat_lock_restore'] = (dialect, previous)
    milliseconds = max(1, min(5000, int(seconds * 1000)))
    connection.exec_driver_sql(f'PRAGMA busy_timeout={milliseconds}' if dialect == 'sqlite'
                              else f'SET SESSION innodb_lock_wait_timeout={max(1, milliseconds // 1000)}')


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


def database_failure_details(error):
    """Safe diagnosis only: no SQL, driver message, parameters, or file paths."""
    original = getattr(error, 'orig', None)
    code = getattr(original, 'sqlite_errorcode', None)
    args = getattr(original, 'args', ())
    if code is None and args and isinstance(args[0], int):
        code = args[0]
    frames = []
    traceback = error.__traceback__
    while traceback:
        module = traceback.tb_frame.f_globals.get('__name__', '')
        if module.startswith('app.'):
            frames.append(module + '.' + traceback.tb_frame.f_code.co_name)
        traceback = traceback.tb_next
    return {'database_code': code, 'frames': frames[-8:]}
