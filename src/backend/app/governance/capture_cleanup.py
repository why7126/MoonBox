"""Independent deletion intentions survive restoring an older business database."""
import json
from contextlib import closing
import os
import sqlite3
from datetime import datetime,timedelta,timezone
from sqlalchemy import delete,select,update,inspect
from app.governance import store
from app.governance.capture_schema import drafts,materials,revisions,organize_tasks,quotas,confirmations
from app.chat.service import now


def ledger():
    path=store.root()/'capture-deletions.sqlite'
    if path.is_symlink():raise ValueError('unsafe_deletion_ledger')
    fd=os.open(path,os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600);os.close(fd)
    if path.stat().st_mode&0o077:raise ValueError('unsafe_deletion_permissions')
    connection=sqlite3.connect(path)
    connection.execute('PRAGMA synchronous=FULL')
    connection.execute('CREATE TABLE IF NOT EXISTS deletions (draft_id TEXT PRIMARY KEY, actor_id TEXT NOT NULL, scope_key TEXT NOT NULL, deleted_at TEXT NOT NULL)')
    connection.commit()
    return connection


def record(row):
    with closing(ledger()) as db, db:
        db.execute('INSERT OR IGNORE INTO deletions VALUES (?,?,?,?)',(row['id'],row['actor_id'],row['scope_key'],now()))


def deleted(draft_id,actor,scope_key):
    # No destructive request has run before the ledger exists; reads need no filesystem mutation.
    path=store.root()/'capture-deletions.sqlite'
    if not path.exists():return False
    with closing(ledger()) as db, db:
        return bool(db.execute('SELECT 1 FROM deletions WHERE draft_id=? AND actor_id=? AND scope_key=?',(draft_id,actor,scope_key)).fetchone())


def replay(db):
    if not inspect(db.get_bind()).has_table('capture_drafts'):return
    with closing(ledger()) as source, source:entries=source.execute('SELECT draft_id,actor_id,scope_key,deleted_at FROM deletions').fetchall()
    for did,actor,key,stamp in entries:
        row=db.execute(select(drafts).where(drafts.c.id==did,drafts.c.actor_id==actor,drafts.c.scope_key==key)).mappings().first()
        if not row or row['confirmed_task_id']:continue  # Formal sources never fall under draft deletion.
        if not row['deleted_at']:
            db.execute(update(quotas).where(quotas.c.actor_id==actor,quotas.c.scope_key==key,quotas.c.draft_count>0).values(draft_count=quotas.c.draft_count-1))
        db.execute(update(drafts).where(drafts.c.id==did).values(state='deleted',deleted_at=stamp,updated_at=stamp,
            payload=json.dumps({'text':'','media_ids':[],'candidates':[],'history':{}})))
        db.execute(delete(revisions).where(revisions.c.draft_id==did))
        db.execute(update(organize_tasks).where(organize_tasks.c.draft_id==did).values(state='cancelled',result=None,error_code='draft_deleted'))
        db.execute(update(materials).where(materials.c.draft_id==did,materials.c.state!='deleted').values(state='delete_pending',deleted_at=stamp))


def cleanup(db,storage):
    replay(db);db.commit()
    cutoff=(datetime.now(timezone.utc)-timedelta(hours=24)).isoformat(timespec='seconds')
    rows=db.execute(select(materials).where((materials.c.state=='delete_pending')|
        (materials.c.state.in_(('ready','uploading','detached'))&(materials.c.created_at<cutoff)))).mappings().all()
    removed=0
    for row in rows:
        draft=db.execute(select(drafts).where(drafts.c.id==row['draft_id'])).mappings().first()
        if not draft:continue
        if db.scalar(select(organize_tasks.c.id).where(organize_tasks.c.draft_id==row['draft_id'],organize_tasks.c.state.in_(('pending','running'))).limit(1)):continue
        payload=json.loads(draft['payload'])
        from app.governance.capture_drafts import protected_media
        if row['state'] in ('ready','detached') and row['id'] in protected_media(payload):continue
        # Reserve against concurrent save/confirm while checking references again.
        held=db.execute(update(drafts).where(drafts.c.id==draft['id'],drafts.c.revision==draft['revision'],
            drafts.c.state==draft['state']).values(updated_at=draft['updated_at']))
        if held.rowcount!=1:db.rollback();continue
        storage.remove(row['object_key'])
        changed=db.execute(update(materials).where(materials.c.id==row['id'],materials.c.state!='deleted').values(state='deleted',updated_at=now()))
        if changed.rowcount:
            db.execute(update(quotas).where(quotas.c.actor_id==row['actor_id'],quotas.c.scope_key==row['scope_key'])
                .values(material_bytes=quotas.c.material_bytes-row['size']))
            removed+=1
        db.commit()
    return removed


def main():
    import argparse
    parser=argparse.ArgumentParser(description='重放Capture删除意图或清理到期材料')
    parser.add_argument('action',choices=['replay-deletions','cleanup'])
    action=parser.parse_args().action
    from app.chat.api import get_session_factory
    try:
        with get_session_factory()() as db:
            if action=='replay-deletions':replay(db);db.commit();print('Capture删除意图已重放')
            else:
                from app.core.object_storage import get_object_storage
                count=cleanup(db,get_object_storage());print(f'Capture材料清理完成：{count}')
    except Exception:
        raise SystemExit('Capture维护失败，请检查私有状态目录、数据库与对象存储配置') from None

if __name__=='__main__':main()
