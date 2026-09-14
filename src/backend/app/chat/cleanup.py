"""History deletion preserves repositories and tracks each retained copy independently."""
import os
import subprocess
from pathlib import Path
from datetime import datetime,timedelta,timezone
from sqlalchemy import delete,insert,select,update,func
from app.chat import service
from app.chat.schema import conversations,turns,messages,events,snapshots,diffs,relations,reservations,workspace_baselines,cleanup_jobs,usage_accounts
from app.chat.settings import repository_binding,retention_limits
from app.chat.workspace import trusted_directory,snapshot,WorkspaceError


def inspect_deletion(db,actor,cid):
    parent=service.conversation(db,actor,cid)
    from app.chat.schema import governance_candidates
    if db.scalar(select(governance_candidates.c.id).where(governance_candidates.c.conversation_id==cid).limit(1)):
        return {'allowed':False,'reason':'治理成果仍在保留期内，需先完成受控成果清理','workspace_hash':None}
    if parent['active_turn_id']:return {'allowed':False,'reason':'存在活动或未知运行','workspace_hash':None}
    count=db.scalar(select(func.count()).select_from(turns).where(turns.c.conversation_id==cid))
    if not count:return {'allowed':True,'reason':None,'workspace_hash':None}
    if not retention_limits():return {'allowed':False,'reason':'执行副本及备份删除时限尚未配置','workspace_hash':None}
    if db.scalar(select(reservations.c.id).join(turns,turns.c.id==reservations.c.turn_id).where(turns.c.conversation_id==cid,reservations.c.status=='reserved').limit(1)):
        return {'allowed':False,'reason':'执行使用量尚未结算','workspace_hash':None}
    if not parent['workspace_id']:return {'allowed':True,'reason':None,'workspace_hash':None}
    binding=repository_binding(parent['repository_id'],parent['space_id'])
    try:
        root=trusted_directory(binding['workspace_root']) if binding and isinstance(binding.get('workspace_root'),str) and Path(binding['workspace_root']).is_absolute() else None
        if root is None or parent['workspace_id']!=cid:raise ValueError()
        workspace=trusted_directory(root/cid)
        trusted_directory(workspace/'.git')
        env={'PATH':os.environ.get('PATH','/usr/bin:/bin'),'HOME':'/nonexistent','GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null','GIT_OPTIONAL_LOCKS':'0'}
        result=subprocess.run(['git','-c','core.fsmonitor=false','-c','core.hooksPath=/dev/null','-C',str(workspace),'status','--porcelain=v1','--untracked-files=all'],env=env,capture_output=True,timeout=10)
        if result.returncode or result.stdout:return {'allowed':False,'reason':'工作区存在尚未处理的变更或状态不可确认','workspace_hash':None}
        current=snapshot(workspace,max_text_bytes=0)
        return {'allowed':True,'reason':None,'workspace_hash':current['hash']}
    except (OSError,ValueError,WorkspaceError,subprocess.SubprocessError):
        return {'allowed':False,'reason':'工作区或代码保留状态不可确认','workspace_hash':None}


def delete_history(db,actor,cid,expected_hash=None):
    parent=service.conversation(db,actor,cid)
    # Lock before inspection and keep the lock through purging, preventing new admissions.
    db.execute(update(conversations).where(conversations.c.id==cid).values(updated_at=service.now()))
    verdict=inspect_deletion(db,actor,cid)
    if not verdict['allowed'] or verdict['workspace_hash']!=expected_hash:
        db.rollback();raise service.ChatError(2507,verdict['reason'] or '工作区已变化，请重新检查')
    ids=list(db.scalars(select(turns.c.id).where(turns.c.conversation_id==cid)))
    from app.chat.settings import backup_root
    if not ids and not backup_root():
        db.rollback();service.delete_empty_conversation(db,actor,cid)
        return {'deleted':True,'code_preserved':True,'main_status':'empty','executor_status':'not_applicable','backup_status':'not_applicable'}
    limits=retention_limits()
    if ids and not limits:db.rollback();raise service.ChatError(2507,'删除时限尚未配置')
    if backup_root():
        from app.chat.backup import LocalBackupStore
        try:
            engine=db.get_bind()
            if engine.dialect.name!='sqlite':raise ValueError('local backup requires SQLite')
            LocalBackupStore(backup_root()).record_deletion(cid,source=Path(engine.url.database).absolute())
        except Exception:
            db.rollback();raise service.ChatError(2507,'独立备份删除日志不可用，删除未完成')
    stamp=datetime.now(timezone.utc)
    job={**service.identity(),'conversation_id':cid,'owner_id':actor,'workspace_hash':verdict['workspace_hash'],
        'executor_thread_id':parent['thread_id'],'main_status':'purged','executor_status':'pending' if parent['thread_id'] else 'not_applicable',
        'backup_status':'pending','executor_due_at':(stamp+timedelta(seconds=limits['executor_delete_seconds'])).isoformat(timespec='seconds') if limits and limits['executor_delete_seconds'] is not None else None,
        'backup_due_at':(stamp+timedelta(seconds=limits['backup_expiry_seconds'])).isoformat(timespec='seconds') if limits and limits['backup_expiry_seconds'] is not None else None}
    # Accounted bytes include the baseline once; audit/trace records are retained separately.
    used=db.scalar(select(func.coalesce(func.sum(reservations.c.actual_bytes),0)).where(reservations.c.turn_id.in_(ids)))
    for key in (f'user:{actor}',f"space:{parent['space_id']}"):
        row=db.execute(select(usage_accounts).where(usage_accounts.c.id==key)).mappings().first()
        if row:db.execute(update(usage_accounts).where(usage_accounts.c.id==key).values(used_bytes=max(0,row['used_bytes']-used)))
    for table in (events,messages,snapshots,diffs,reservations):db.execute(delete(table).where(table.c.turn_id.in_(ids)))
    db.execute(delete(turns).where(turns.c.conversation_id==cid))
    db.execute(delete(relations).where(relations.c.conversation_id==cid))
    db.execute(delete(workspace_baselines).where(workspace_baselines.c.conversation_id==cid))
    db.execute(insert(cleanup_jobs).values(**job))
    db.execute(update(conversations).where(conversations.c.id==cid).values(deleted_at=service.now(),title='',thread_id=None,cleanup_status='copies_pending',updated_at=service.now()))
    db.commit()
    return {'deleted':True,'code_preserved':True,**{key:job[key] for key in ('main_status','executor_status','backup_status')}}


def status(db,actor,cid):
    row=db.execute(select(cleanup_jobs).where(cleanup_jobs.c.conversation_id==cid,cleanup_jobs.c.owner_id==actor)).mappings().first()
    if not row:raise service.ChatError(2502,'清理记录不存在或无权访问',404)
    space=db.scalar(select(conversations.c.space_id).where(conversations.c.id==cid))
    if not space:raise service.ChatError(2502,'清理会话不存在',404)
    service.authorize_space(db,actor,space)
    return {key:row[key] for key in ('main_status','executor_status','backup_status','executor_due_at','backup_due_at')}


def process_copies(db, cid, executor, backup):
    """Trusted deployment adapters return True only after verified deletion; deadlines aren't evidence.

    executor(job) removes the exact thread's retained history. backup(job) checks
    the deployment's backup inventory/tombstone policy. No browser-supplied callback.
    """
    job=db.execute(select(cleanup_jobs).where(cleanup_jobs.c.conversation_id==cid).with_for_update()).mappings().first()
    if not job:return False
    parent=db.execute(select(conversations).where(conversations.c.id==cid)).mappings().first()
    if not parent or not parent['deleted_at'] or parent['active_turn_id']:return False
    changes={}
    for field,adapter in (('executor_status',executor),('backup_status',backup)):
        if job[field] in ('pending','retry'):
            try:changes[field]='purged' if adapter(dict(job)) is True else 'retry'
            except Exception:changes[field]='retry'
    if changes:
        db.execute(update(cleanup_jobs).where(cleanup_jobs.c.id==job['id']).values(**changes,updated_at=service.now()))
    complete=all(changes.get(field,job[field]) in ('purged','not_applicable') for field in ('executor_status','backup_status'))
    db.execute(update(conversations).where(conversations.c.id==cid).values(cleanup_status='complete' if complete else 'copies_pending'))
    db.commit()
    return complete
