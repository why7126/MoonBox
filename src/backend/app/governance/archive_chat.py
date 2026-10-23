"""Trusted archive turns bypass the model and keep the original operation on retry."""
import json
import hashlib
import re
from sqlalchemy import select,insert,update
from app.chat import service,worker
from app.chat.schema import relations,reservations,diffs,turns
from app.chat.assistant_output import persist_output
from app.chat.workspace import snapshot,difference
from . import scope



def governance_snapshot(root,*,max_text_bytes):
    """Read only controller-owned governance trees, never repository Git config.

    Trusted tools live under a read-only deployment root. Git ownership rules for
    an Agent workspace do not describe that root; archive diffs cover only the
    trees this controller is allowed to mutate.
    """
    files={};remaining_text=max_text_bytes;remaining_bytes=512*1024*1024
    for name in ('openspec','issues','iterations'):
        folder=root/name
        if not folder.exists():continue
        result=snapshot(folder,max_files=10000-len(files),max_total_bytes=remaining_bytes,max_text_bytes=remaining_text)
        for path,value in result['files'].items():
            files[name+'/'+path]=value
            remaining_bytes-=value['size']
            if value.get('text') is not None:remaining_text-=len(value['text'].encode())
    digest=hashlib.sha256(json.dumps(files,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    return {'files':files,'hash':digest}


def run(factory,token,workspace):
    from app.chat.execution import owned
    with factory() as db:
        row,parent=owned(db,token)
        match=re.fullmatch(r'/(?:opsx-archive|sprint-archive)\s+((?:(?:REQ|BUG)-\d{4}-[A-Za-z0-9_-]+)|[a-z0-9][a-z0-9-]{0,100})',(row['prompt'] or '').strip())
        if not match:return None
        if row['prompt'].strip().startswith('/sprint-archive') and not re.fullmatch(r'sprint-\d{3}',match[1]):
            raise service.ChatError(2606,'迭代归档命令标识无效',409)
        project=scope.authorize(db,parent['owner_id'],parent['space_id'],parent['repository_id'],write=True)
        primary=db.scalar(select(relations.c.object_id).where(relations.c.conversation_id==parent['id'],relations.c.role=='primary'))
        if primary!=match[1]:raise service.ChatError(2606,'归档对象与当前主对象不一致',409)
        if not db.execute(select(reservations).where(reservations.c.turn_id==row['id'])).first():
            raise service.ChatError(2606,'执行预算尚未建立',409)
        if row['status']=='stopping':
            worker.record_event(db,token,'archive:started','execution.state',{'status':'stopping','executor':'trusted_archive'})
            worker.record_event(db,token,'archive:usage','execution.usage',{'total_tokens':0,'actual_bytes':0,'usage_scope':'trusted_archive_v1'})
            worker.record_event(db,token,'archive:stopped','execution.state',{'status':'stopped'},terminal='stopped')
            from app.chat.accounting import reconcile_usage
            reconcile_usage(db,row['id'])
            return 'stopped'
        if not worker.record_event(db,token,'archive:started','execution.state',{'status':'running','executor':'trusted_archive'}):
            raise service.ChatError(2606,'执行租约已变化',409)
    budget=row['reserved_bytes'];before=None;after=None
    terminal='completed';reply='归档已完成，已核验规格、迁移和同步结果。';code=None
    try:
        before=governance_snapshot(project.root,max_text_bytes=min(budget//4,4*1024*1024))
        from .archive_dispatch import execute_object
        with factory() as db:
            owned(db,token)
            execute_object(db,actor=parent['owner_id'],space_id=project.space_id,repository_id=project.repository_id,
                object_id=match[1],request_id=row.get('request_id'))
    except Exception:
        # Partial results retain their durable project operation and fence.
        # Retrying this command observes that operation; it never starts a model.
        terminal='failed';code='trusted_archive_unverified'
        reply='归档尚未确认完成。请核验当前阻断后重试同一对象命令，系统将回读原操作；不要手动重做合并。'
    try:
        if before is not None:after=governance_snapshot(project.root,max_text_bytes=min(budget//4,4*1024*1024))
    except Exception:
        terminal='failed';code='trusted_archive_evidence_unavailable'
        reply='归档结果的差异证据暂不可用。请重试同一对象命令回读原操作，不要手动重新合并。'
    delta=difference(before,after,max_patch_bytes=budget//8) if before is not None and after is not None else None
    encoded=json.dumps({'files':delta['files'],'cumulative_files':delta['files'],'initial_hash':before['hash']},ensure_ascii=False) if delta is not None else None
    from .direct_command_journal import observe,terminal as finish_journal
    from .controlled_successor import authority
    with factory() as db:
        with authority(db,project,parent['owner_id']):
            observe(parent['id'],row['client_request_id'],'trusted-archive','completed',project.root,
                sync=terminal=='completed',sync_succeeded=terminal=='completed')
            finish_journal(parent['id'],row['client_request_id'],terminal,project.root)
    with factory() as db:
        owned(db,token)
        if encoded is not None:
            db.execute(insert(diffs).values(**service.identity(),turn_id=row['id'],before_hash=before['hash'],after_hash=after['hash'],payload=encoded))
        persist_output(db,row['id'],reply)
        db.execute(update(turns).where(turns.c.id==row['id']).values(error_code=code));db.commit()
        worker.record_event(db,token,'archive:usage','execution.usage',{'total_tokens':0,'actual_bytes':len((encoded or '').encode())+len(reply.encode())*2+2048,
            'thread_total':0,'usage_scope':'trusted_archive_v1','usage_pending':False})
        worker.record_event(db,token,'archive:terminal','execution.state',{'status':terminal},terminal=terminal)
    with factory() as db:
        from app.chat.accounting import reconcile_usage
        reconcile_usage(db,row['id'])
    return terminal
