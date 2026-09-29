"""Offline SQLite + private-record backup. Restore never starts workers or writes a repo."""
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
from uuid import UUID
from sqlalchemy import select
from app.chat.schema import governance_candidates,governance_applications,turns
from app.chat.workspace import trusted_directory
from app.governance import store,scope
from app.chat.backup import LocalBackupStore
from app.chat.settings import backup_root
from app.governance.writer import project_lock


RECORD_NAMES={'baseline.json','result.json','operation.json'}


def records(root):
    result={}
    for directory in sorted(root.iterdir()):
        try: UUID(directory.name)
        except ValueError:continue
        trusted_directory(directory)
        fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:
            for name in sorted(os.listdir(fd)):
                if name not in RECORD_NAMES: raise ValueError('unfinished_or_unknown_private_record')
                child=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
                with os.fdopen(child,'rb') as stream:
                    import stat
                    info=os.fstat(stream.fileno())
                    if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size>64*1024*1024:raise ValueError('unsafe_backup_record')
                    body=stream.read(64*1024*1024+1)
                result[directory.name+'/'+name]=body
        finally:os.close(fd)
    if sum(map(len,result.values()))>512*1024*1024:raise ValueError('backup_capacity')
    return result


def facts(db):
    return {table.name:[dict(row) for row in db.execute(select(table).order_by(table.c.id)).mappings()]
            for table in (governance_candidates,governance_applications)}


def create(factory,destination):
    destination=Path(destination).absolute();trusted_directory(destination.parent)
    private=store.root()
    if destination.exists() or private==destination or private in destination.parents:raise ValueError('backup_destination_not_new_or_separate')
    with factory() as db,ExitStack() as stack:
        if db.get_bind().dialect.name!='sqlite':raise ValueError('use_mysql_native_offline_backup')
        if db.scalar(select(turns.c.id).where(turns.c.status.in_(service_active())).limit(1)):
            raise ValueError('stop_active_chat_before_backup')
        if db.scalar(select(governance_applications.c.id).where(governance_applications.c.state.in_(('applying','recovering'))).limit(1)):
            raise ValueError('recover_active_application_before_backup')
        before=facts(db)
        projects={(row['actor_id'],row['space_id'],row['repository_id']) for values in before.values() for row in values}
        acquired=set()
        for actor,space_id,repository_id in sorted(projects):
            project=scope.authorize(db,actor,space_id,repository_id)
            if project.key not in acquired:stack.enter_context(project_lock(project));acquired.add(project.key)
        blobs=records(private)
        destination.mkdir(mode=0o700)
        try:
            database=Path(db.get_bind().url.database).resolve()
            target=destination/'database.sqlite'
            history_store=LocalBackupStore(backup_root())
            history_id=history_store.create(database)
            shutil.copyfile(history_store.root/(history_id+'.sqlite'),target)
            target.chmod(0o600)
            for name,body in blobs.items():
                path=destination/'records'/name;path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
                path.write_bytes(body);path.chmod(0o600)
            db.commit()
            if before!=facts(db) or blobs!=records(private):raise ValueError('backup_inputs_changed')
            hashes={name:hashlib.sha256(body).hexdigest() for name,body in blobs.items()}
            hashes['database.sqlite']=hashlib.sha256(target.read_bytes()).hexdigest()
            manifest=destination/'manifest.json';manifest.write_text(json.dumps({'version':1,'files':hashes,'history_backup_id':history_id}));manifest.chmod(0o600)
            for path in destination.rglob('*'):
                if path.is_file():
                    with path.open('rb') as handle:os.fsync(handle.fileno())
            fd=os.open(destination,os.O_RDONLY|os.O_DIRECTORY);os.fsync(fd);os.close(fd)
        except BaseException:
            shutil.rmtree(destination);raise
    return {'files':len(blobs),'offline_only':True}


def service_active():
    return ('queued','connecting','running','stopping','unknown')


def restore(backup,destination):
    backup=trusted_directory(backup);destination=Path(destination).absolute();trusted_directory(destination.parent)
    if destination.exists() or backup==destination or backup in destination.parents:raise ValueError('restore_destination_not_new_or_separate')
    # Verify every input before creating the destination; reject links/tampering.
    manifest_path=backup/'manifest.json'
    if manifest_path.is_symlink():raise ValueError('unsafe_backup_manifest')
    manifest=json.loads(manifest_path.read_text())
    if manifest.get('version')!=1:raise ValueError('unsupported_backup')
    blobs=records(backup/'records') if (backup/'records').exists() else {}
    database=backup/'database.sqlite'
    if database.is_symlink() or not database.is_file():raise ValueError('unsafe_backup_database')
    blobs['database.sqlite']=database.read_bytes()
    if {name:hashlib.sha256(body).hexdigest() for name,body in blobs.items()}!=manifest['files']:raise ValueError('backup_checksum_mismatch')
    with sqlite3.connect(database.as_uri()+'?mode=ro',uri=True) as db:
        if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('backup_database_corrupt')
    history_store=LocalBackupStore(backup_root())
    history_source=history_store.root/(manifest['history_backup_id']+'.sqlite')
    if history_source.is_symlink() or hashlib.sha256(history_source.read_bytes()).hexdigest()!=manifest['files']['database.sqlite']:
        raise ValueError('history_backup_missing_or_changed')
    destination.mkdir(mode=0o700)
    try:
        history_store.restore(manifest['history_backup_id'],destination/'database.sqlite')
        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session
        from app.governance.capture_cleanup import replay
        restored_engine=create_engine('sqlite:///'+str(destination/'database.sqlite'))
        try:
            with Session(restored_engine) as restored_db:
                replay(restored_db);restored_db.commit()
        finally:restored_engine.dispose()
        with sqlite3.connect(destination/'database.sqlite') as restored:
            live_ids={row[0] for table in ('governance_candidates','governance_applications') for row in restored.execute('SELECT id FROM '+table)}
        for name,body in blobs.items():
            if name=='database.sqlite' or name.split('/')[0] not in live_ids:continue
            path=destination/name if name=='database.sqlite' else destination/'records'/name
            path.parent.mkdir(parents=True,exist_ok=True,mode=0o700);path.write_bytes(body);path.chmod(0o600)
    except BaseException:
        shutil.rmtree(destination);raise
    return {'offline_only':True,'maintenance_registration_required':True,'files':len(blobs)}
