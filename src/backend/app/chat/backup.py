"""受控本地SQLite备份：删除日志独立保留，恢复只生成离线副本。"""
from contextlib import contextmanager
import fcntl
import hashlib
import os
from pathlib import Path
import re
import sqlite3
import uuid

from sqlalchemy import create_engine, delete, insert, select, update
from sqlalchemy.orm import Session
from app.chat import service
from app.chat.schema import conversations, turns, events, messages, snapshots, diffs, relations, reservations, workspace_baselines, cleanup_jobs
from app.chat.workspace import trusted_directory


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', value):
        raise ValueError('invalid backup identifier')
    return value


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


class LocalBackupStore:
    """仅受信任运维代码调用；目录必须独立于业务DB、仓库和恢复目标。"""
    def __init__(self, root, *, initialize=False):
        self.root = trusted_directory(root)
        if self.root.stat().st_mode & 0o077:
            raise ValueError('backup directory must be private')
        self.ledger = self.root / 'deletions.sqlite'
        if initialize:
            fd = os.open(self.ledger, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(fd)
            with sqlite3.connect(self.ledger) as db:
                db.executescript('''
                    CREATE TABLE identity (id TEXT PRIMARY KEY, source_hash TEXT);
                    CREATE TABLE deletions (conversation_id TEXT PRIMARY KEY, deleted_at TEXT NOT NULL);
                    CREATE TABLE backups (id TEXT PRIMARY KEY, sha256 TEXT NOT NULL, created_at TEXT NOT NULL);
                ''')
                db.execute('INSERT INTO identity(id) VALUES (?)', (uuid.uuid4().hex,))
        self._validate()

    def _validate(self):
        if self.ledger.is_symlink() or not self.ledger.is_file():
            raise ValueError('independent deletion ledger missing')
        if self.ledger.stat().st_mode & 0o077:
            raise ValueError('deletion ledger must be private')
        with sqlite3.connect(self.ledger) as db:
            if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise ValueError('deletion ledger corrupt')
            if len(db.execute('SELECT id FROM identity').fetchall()) != 1:
                raise ValueError('deletion ledger identity invalid')

    @contextmanager
    def locked(self):
        self._validate()
        fd = os.open(self.root / 'store.lock', os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, 'w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            yield

    def record_deletion(self, cid, *, source=None):
        """删除意图先于主存储事务落盘；主事务失败时重试，不撤销删除日志。"""
        cid = identifier(cid)
        with self.locked(), sqlite3.connect(self.ledger) as db:
            if source is not None:
                expected = hashlib.sha256(str(Path(source)).encode()).hexdigest()
                if db.execute('SELECT source_hash FROM identity').fetchone()[0] != expected:
                    raise ValueError('deletion database does not match backup store')
            db.execute('PRAGMA synchronous=FULL')
            db.execute('INSERT OR IGNORE INTO deletions VALUES (?,?)', (cid, service.now()))

    def create(self, source):
        source = Path(source)
        if not source.is_absolute() or source.is_symlink() or not source.is_file():
            raise ValueError('source must be an existing trusted SQLite file')
        trusted_directory(source.parent)
        if source.is_relative_to(self.root):
            raise ValueError('backup store must be outside source database directory')
        backup_id = uuid.uuid4().hex
        output = self.root / (backup_id + '.sqlite')
        with self.locked(), sqlite3.connect(self.ledger) as ledger:
            source_hash = hashlib.sha256(str(source).encode()).hexdigest()
            old = ledger.execute('SELECT source_hash FROM identity').fetchone()[0]
            if old is not None and old != source_hash:
                raise ValueError('backup store belongs to a different database')
            try:
                fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                os.close(fd)
                with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True) as live, sqlite3.connect(output) as copy:
                    live.backup(copy)
                    if copy.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                        raise ValueError('backup integrity failure')
                with output.open('rb') as stream:
                    os.fsync(stream.fileno())
                ledger.execute('UPDATE identity SET source_hash=?', (source_hash,))
                ledger.execute('INSERT INTO backups VALUES (?,?,?)', (backup_id, digest(output), service.now()))
            except Exception:
                output.unlink(missing_ok=True)
                raise
        return backup_id

    def restore(self, backup_id, destination):
        backup_id = identifier(backup_id)
        destination = Path(destination)
        if not destination.is_absolute() or destination.exists() or destination.is_symlink():
            raise ValueError('restore requires a new offline destination')
        trusted_directory(destination.parent)
        if destination.is_relative_to(self.root):
            raise ValueError('restore destination cannot replace backup store')
        stage = destination.parent / ('.restore-' + uuid.uuid4().hex + '.sqlite')
        engine = None
        with self.locked(), sqlite3.connect(self.ledger) as ledger:
            entry = ledger.execute('SELECT sha256 FROM backups WHERE id=?', (backup_id,)).fetchone()
            source = self.root / (backup_id + '.sqlite')
            if not entry or source.is_symlink() or not source.is_file() or digest(source) != entry[0]:
                raise ValueError('backup inventory/hash mismatch')
            ids = [row[0] for row in ledger.execute('SELECT conversation_id FROM deletions')]
            try:
                fd = os.open(stage, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                os.close(fd)
                with sqlite3.connect(source.as_uri() + '?mode=ro', uri=True) as backup, sqlite3.connect(stage) as copy:
                    backup.backup(copy)
                engine = create_engine('sqlite:///' + str(stage))
                with Session(engine) as db:
                    for cid in ids:
                        parent=db.execute(select(conversations).where(conversations.c.id==cid)).mappings().first()
                        # Older backups may predate governance tables. New backups must replay
                        # deletion into candidate/application metadata before turn FK removal.
                        from sqlalchemy import inspect
                        from app.chat.schema import governance_candidates, governance_applications
                        if inspect(db.get_bind()).has_table('governance_candidates'):
                            candidate_ids=list(db.scalars(select(governance_candidates.c.id).where(governance_candidates.c.conversation_id==cid)))
                            db.execute(delete(governance_applications).where(governance_applications.c.candidate_id.in_(candidate_ids)))
                            db.execute(delete(governance_candidates).where(governance_candidates.c.id.in_(candidate_ids)))
                        turn_ids = list(db.scalars(select(turns.c.id).where(turns.c.conversation_id == cid)))
                        for table in (events, messages, snapshots, diffs, reservations):
                            db.execute(delete(table).where(table.c.turn_id.in_(turn_ids)))
                        db.execute(delete(turns).where(turns.c.conversation_id == cid))
                        for table in (relations, workspace_baselines):
                            db.execute(delete(table).where(table.c.conversation_id == cid))
                        db.execute(update(conversations).where(conversations.c.id == cid).values(
                            deleted_at=service.now(), title='', active_turn_id=None, thread_id=None,
                            cleanup_status='copies_pending', updated_at=service.now()))
                        if parent and not db.scalar(select(cleanup_jobs.c.id).where(cleanup_jobs.c.conversation_id==cid)):
                            db.execute(insert(cleanup_jobs).values(**service.identity(),conversation_id=cid,
                                owner_id=parent['owner_id'],executor_thread_id=parent['thread_id'],
                                main_status='purged',executor_status='pending' if parent['thread_id'] else 'not_applicable',
                                backup_status='pending'))
                    # Old queued/running work is never automatically replayed after restore.
                    db.execute(update(turns).where(turns.c.status.in_(('queued','connecting','running','stopping'))).values(
                        status='unknown', error_code='offline_backup_restore', updated_at=service.now()))
                    db.commit()
                engine.dispose();engine = None
                with sqlite3.connect(stage) as copy:
                    if copy.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                        raise ValueError('restored database integrity failure')
                with stage.open('rb') as stream:
                    os.fsync(stream.fileno())
                # Link fails atomically if another process has created the destination.
                os.link(stage, destination)
            finally:
                if engine is not None:engine.dispose()
                stage.unlink(missing_ok=True)
        return {'deleted_conversations_replayed': len(ids), 'execution_quarantined': True,
                'offline_only': True, 'quota_reconciliation_required': True}

    def expire(self, backup_id):
        """调用方选择明确副本；无默认到期天数，不删除独立删除日志。"""
        backup_id = identifier(backup_id)
        with self.locked(), sqlite3.connect(self.ledger) as ledger:
            if not ledger.execute('SELECT id FROM backups WHERE id=?', (backup_id,)).fetchone():
                return False
            source = self.root / (backup_id + '.sqlite')
            if source.is_symlink():raise ValueError('backup path changed')
            source.unlink(missing_ok=True)
            ledger.execute('DELETE FROM backups WHERE id=?', (backup_id,))
        return True

    def copies_cleared(self, cid):
        """仅所有受登记备份都不含该会话正文时返回True；过滤恢复不算清除。"""
        cid=identifier(cid)
        with self.locked(), sqlite3.connect(self.ledger) as ledger:
            if not ledger.execute('SELECT 1 FROM deletions WHERE conversation_id=?',(cid,)).fetchone():
                return False
            for backup_id, expected in ledger.execute('SELECT id,sha256 FROM backups'):
                source=self.root/(identifier(backup_id)+'.sqlite')
                if source.is_symlink() or not source.is_file() or digest(source)!=expected:return False
                with sqlite3.connect(source.as_uri()+'?mode=ro',uri=True) as db:
                    row=db.execute('SELECT deleted_at FROM chat_conversations WHERE id=?',(cid,)).fetchone()
                    if row and not row[0]:return False
                    if db.execute('SELECT 1 FROM chat_turns WHERE conversation_id=? LIMIT 1',(cid,)).fetchone():return False
        return True


def main():
    import argparse,json
    parser=argparse.ArgumentParser(description='受控SQLite本地备份；恢复输出仅用于离线审核')
    parser.add_argument('--root',required=True)
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('init')
    create=sub.add_parser('create');create.add_argument('--source',required=True)
    restore=sub.add_parser('restore');restore.add_argument('--backup',required=True);restore.add_argument('--destination',required=True)
    expire=sub.add_parser('expire');expire.add_argument('--backup',required=True)
    args=parser.parse_args()
    try:
        store=LocalBackupStore(args.root,initialize=args.command=='init')
        if args.command=='init':result={'initialized':True}
        elif args.command=='create':result={'backup_id':store.create(Path(args.source))}
        elif args.command=='restore':result=store.restore(args.backup,Path(args.destination))
        else:result={'physically_removed':store.expire(args.backup)}
        print(json.dumps(result))
    except Exception:
        raise SystemExit('备份操作未完成；检查独立日志、目录权限、备份摘要和目标是否已存在')


if __name__=='__main__':main()
