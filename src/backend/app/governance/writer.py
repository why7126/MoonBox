"""Durable single-host writer. API queues; only this controller mutates source files.

The OS lock coordinates registered writers, not arbitrary external editors. A
server-side maintenance window is required in addition to the user's confirmation.
"""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import PurePosixPath
import stat
import time
from uuid import uuid4
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from app.chat import service
from app.chat.schema import governance_applications as applications, governance_candidates as candidates, governance_project_locks as locks
from app.governance import scope,store
from app.governance.snapshot import read_once,digest,stable,Snapshot,materialize
from app.governance.candidates import validate
from app.governance.reader import ProjectReader,version
from app.services import requirement_center as legacy

TERMINAL=('applied','conflict','failed')


def hash_request(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def maintenance(project):
    """Ops-owned registration; public request fields cannot enable the writer."""
    try:
        base=store.root();fd=os.open(base/'maintenance.json',os.O_RDONLY|os.O_NOFOLLOW)
        with os.fdopen(fd) as stream:
            info=os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_mode&0o077: raise ValueError()
            record=json.load(stream)
        if (record.get('scope_key')!=project.key or record.get('binding_revision')!=project.binding_revision
            or record.get('registered_writers')!=['governance-controller']
            or record.get('external_writers_paused') is not True
            or not time.time()<float(record['expires_at'])<=time.time()+3600): raise ValueError()
    except (OSError,ValueError,KeyError,TypeError):
        raise service.ChatError(2605,'项目未建立受控维护窗口，暂不可写入',503) from None


def write_permission(project, kind):
    if kind in ('capture', 'capture_batch'):
        from app.governance.readiness import require_capture
        require_capture(project)
    else:
        maintenance(project)


def public(row):
    return {key:row[key] for key in ('id','candidate_id','state','phase','error_code','created_at','updated_at')}


def operation(db,actor,oid):
    row=db.execute(select(applications).where(applications.c.id==oid,applications.c.actor_id==actor)).mappings().first()
    if not row: raise service.ChatError(2601,'操作不存在或无权访问',404)
    project=scope.authorize(db,actor,row['space_id'],row['repository_id'])
    if row['candidate_id']:
        candidate=db.execute(select(candidates).where(candidates.c.id==row['candidate_id'])).mappings().one()
        service.conversation(db,actor,candidate['conversation_id'])
        if not scope.visible(db,actor,project,candidate['object_id']): raise service.ChatError(2601,'对象不可访问',403)
    result = public(row)
    if row['state'] == 'applied' and not row['candidate_id']:
        record = store.read(oid, 'operation')
        if record.get('kind') == 'capture':
            if not scope.visible(db, actor, project, record['object_id']):
                raise service.ChatError(2601, '对象不可访问', 403)
            result['object_id'] = record['object_id']
    return result


def epoch(db,project):
    return db.scalar(select(locks.c.fencing_token).where(locks.c.scope_key==project.key)) or 0


def assert_readable(db,project):
    blocked=db.scalar(select(applications.c.id).where(applications.c.scope_key==project.key,
        applications.c.state.in_(('applying','recovering','recovery_blocked'))).limit(1))
    if blocked: raise service.ChatError(2603,'项目正在应用或恢复，保留上次完整快照',503)


def enqueue(db,actor,project,key,request,record,candidate_id=None,request_id=None):
    key=hashlib.sha256(key.encode()).hexdigest()
    request_hash=hash_request(request)
    existing=db.execute(select(applications).where(applications.c.actor_id==actor,
        applications.c.scope_key==project.key,applications.c.idempotency_key==key)).mappings().first()
    if existing:
        if existing['request_hash']!=request_hash: raise service.ChatError(2606,'幂等标识已用于其他内容',409)
        return public(existing)
    write_permission(project, record.get('kind'));assert_readable(db,project)
    row={**service.identity(),'actor_id':actor,'space_id':project.space_id,'repository_id':project.repository_id,
        'scope_key':project.key,'idempotency_key':key,'request_hash':request_hash,'request_id':request_id,
        'candidate_id':candidate_id,'state':'pending','phase':'queued','error_code':None}
    record['binding_revision']=project.binding_revision
    store.write(row['id'],'operation',record)
    try:
        db.execute(insert(applications).values(**row))
        from app.governance.observability import trace
        trace(db,row['id'],'queued',actor=actor,request_id=request_id)
        db.commit()
    except IntegrityError:
        db.rollback()
        existing=db.execute(select(applications).where(applications.c.candidate_id==candidate_id if candidate_id else
            ((applications.c.actor_id==actor)&(applications.c.scope_key==project.key)&(applications.c.idempotency_key==key)))).mappings().first()
        if existing and existing['actor_id']==actor and existing['request_hash']==request_hash: return public(existing)
        raise service.ChatError(2606,'该成果已有应用请求，请读取原操作结果',409) from None
    return public(row)


def apply_candidate(db,actor,candidate_id,expected_manifest_hash,candidate_revision,idempotency_key,confirmed,request_id=None):
    row=db.execute(select(candidates).where(candidates.c.id==candidate_id,candidates.c.actor_id==actor)).mappings().first()
    if not row: raise service.ChatError(2601,'成果不存在或无权访问',404)
    service.conversation(db,actor,row['conversation_id'])
    project=scope.authorize(db,actor,row['space_id'],row['repository_id'],write=True)
    if not scope.visible(db,actor,project,row['object_id']): raise service.ChatError(2601,'对象不可访问',403)
    if not confirmed: raise service.ChatError(2605,'请先确认维护窗口与固定成果集合',422)
    if row['state'] not in ('pending','applied') or row['manifest_hash']!=expected_manifest_hash or row['revision']!=candidate_revision or row['binding_revision']!=project.binding_revision:
        raise service.ChatError(2606,'成果或项目绑定版本已变化',409)
    baseline=store.read(row['id'],'baseline');result=store.read(row['id'],'result')
    request={'candidate_id':candidate_id,'manifest_hash':expected_manifest_hash,'revision':candidate_revision}
    record={'before':baseline['files'],'after':result['after'],'base_path':baseline['base_path'],'object_id':row['object_id'],'kind':'req-generate'}
    return enqueue(db,actor,project,idempotency_key,request,record,candidate_id,request_id)


def _enqueue_document(reader,name,object_id,document_name,content,expected_version,key,task_toggle=False,request_id=None):
    project=scope.authorize(reader.db,reader.actor,reader.scope.space_id,reader.scope.repository_id,write=True)
    assert_readable(reader.db,project)
    snapshot=reader.snapshot();is_change='change_document' in name
    entries=reader.authorize_object(snapshot,object_id,change=is_change,write=True)
    if is_change and not entries:
        raise service.ChatError(2601, '独立 Change 仅支持读取', 403)
    maintenance(project)
    actual_id=object_id if is_change else entries[0]['id']
    read_name='read_requirement_center_change_document' if is_change else 'read_requirement_center_document'
    with materialize(snapshot) as root,legacy.using_governance_root(root):
        previous,_=getattr(legacy,read_name)(actual_id,document_name)
        if version(previous)!=expected_version: raise service.ChatError(2606,'源文档已变化，请保留草稿并重新读取',409)
        kwargs={'task_toggle':task_toggle} if is_change else {}
        getattr(legacy,name)(actual_id,document_name,content,**kwargs)
        updated=read_once(root)
    changes={path:body.decode() for path,body in updated.items() if snapshot.files.get(path)!=body}
    request={'object':actual_id,'document':document_name,'content_hash':version(content),'expected_version':expected_version,'task_toggle':task_toggle}
    record={'before':{p:b.decode() for p,b in snapshot.files.items()},'after':changes,'kind':'document',
        'object_id':actual_id,'document_name':document_name,'content':content,'task_toggle':task_toggle,'function':name}
    return enqueue(reader.db,reader.actor,project,key,request,record,request_id=request_id)


def enqueue_document(*args, **kwargs):
    try:
        return _enqueue_document(*args, **kwargs)
    except PermissionError:
        raise service.ChatError(2601, '当前阶段不允许编辑该文档或任务状态', 403) from None
    except FileNotFoundError:
        raise service.ChatError(2604, '文档不存在或已移动', 404) from None
    except ValueError:
        raise service.ChatError(2604, '文档内容或类型不符合编辑边界', 422) from None
    except OSError:
        raise service.ChatError(2605, '文档保存失败，治理目录暂不可写', 503) from None


@contextmanager
def project_lock(project):
    # Never unlink lock files. The same inode must fence every local controller.
    fd=os.open(store.root()/('project-'+project.key+'.lock'),os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW,0o600)
    try:
        fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        yield
    finally: os.close(fd)


def read_target(parent,name):
    try: fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent)
    except FileNotFoundError:return None
    with os.fdopen(fd,'rb') as stream:
        info=os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size>1024*1024: raise ValueError('unsafe_file')
        return stream.read(1024*1024+1)


def replace_file(root,relative,before,after,oid,*,create_parents=False):
    parts=PurePosixPath(relative).parts
    if not parts or PurePosixPath(relative).is_absolute() or '..' in parts: raise ValueError('invalid_path')
    handles=[os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)]
    temporary='.moonbox-'+oid+'.tmp'
    owned_temp=False
    try:
        for part in parts[:-1]:
            if create_parents:
                try:
                    os.mkdir(part, mode=0o755, dir_fd=handles[-1]); os.fsync(handles[-1])
                except FileExistsError:
                    pass
            handles.append(os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=handles[-1]))
        parent=handles[-1];name=parts[-1]
        if read_target(parent,name)!=before: raise ValueError('external_change')
        # Retain ordinary read/write permissions; never propagate executable bits.
        mode=(os.stat(name,dir_fd=parent,follow_symlinks=False).st_mode&0o666) if before is not None else 0o644
        try:
            fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode,dir_fd=parent)
        except FileExistsError:
            if read_target(parent,temporary)!=after: raise ValueError('unknown_temporary')
            os.unlink(temporary,dir_fd=parent);os.fsync(parent)
            fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,mode,dir_fd=parent)
        owned_temp=True
        with os.fdopen(fd,'wb') as stream:
            stream.write(after);stream.flush();os.fsync(stream.fileno())
        if read_target(parent,name)!=before: raise ValueError('external_change')
        os.replace(temporary,name,src_dir_fd=parent,dst_dir_fd=parent);os.fsync(parent)
        if read_target(parent,name)!=after: raise ValueError('external_change')
    finally:
        if owned_temp:
            try: os.unlink(temporary,dir_fd=handles[-1])
            except FileNotFoundError:pass
        for fd in reversed(handles):os.close(fd)


def set_state(db,oid,state,phase,error=None):
    db.execute(update(applications).where(applications.c.id==oid).values(state=state,phase=phase,error_code=error,updated_at=service.now()))
    from app.governance.observability import trace
    trace(db,oid,state)
    from app.governance.capture_schema import confirmations as capture_confirmations
    capture_row=db.execute(select(capture_confirmations).where(capture_confirmations.c.operation_id==oid)).mappings().first()
    if capture_row:
        from app.governance.capture_observability import trace as capture_trace
        capture_trace(db,capture_row['id'],phase if phase in ('prepared','verified') or phase.startswith('file-') else state,
                      actor=capture_row['actor_id'],kind='capture_confirmation')
    db.commit()


def refresh_capture_authorization(db,row,record):
    db.commit()  # Refresh MySQL's authorization snapshot at each durable boundary.
    project=scope.authorize(db,row['actor_id'],row['space_id'],row['repository_id'],write=True)
    if project.binding_revision!=record['binding_revision']:raise ValueError('binding_changed')
    return project


def process(db,oid,*,after_write=None):
    db.commit()
    row=db.execute(select(applications).where(applications.c.id==oid)).mappings().one()
    if row['state'] in TERMINAL or row['state']=='recovery_blocked': return public(row)
    project=scope.authorize(db,row['actor_id'],row['space_id'],row['repository_id'],write=True)
    with project_lock(project):
        # Refresh MySQL's snapshot after acquiring the OS fence.
        db.commit()
        # An acquired flock proves the previous registered local controller no longer holds it.
        row=db.execute(select(applications).where(applications.c.id==oid)).mappings().one()
        if row['state'] in TERMINAL or row['state']=='recovery_blocked': return public(row)
        project=scope.authorize(db,row['actor_id'],row['space_id'],row['repository_id'],write=True)
        recovering=row['state'] in ('applying','recovering')
        wrote=False
        other=db.scalar(select(applications.c.id).where(applications.c.scope_key==project.key,
            applications.c.id!=oid,applications.c.state.in_(('applying','recovering','recovery_blocked'))).limit(1))
        if other: raise service.ChatError(2605,'项目存在待恢复操作',503)
        try:
            record=store.read(oid,'operation');before={p:b.encode() for p,b in record['before'].items()};after={p:b.encode() for p,b in record['after'].items()}
        except (OSError,ValueError,KeyError,AttributeError,TypeError):
            set_state(db,oid,'recovery_blocked','record_unavailable','recovery_record_invalid')
            return public(db.execute(select(applications).where(applications.c.id==oid)).mappings().one())
        try:
            write_permission(project, record.get('kind'))
            if project.binding_revision!=record['binding_revision']: raise ValueError('binding_changed')
            if record['kind'] in ('capture','capture_batch') and not record.get('planned'):
                baseline=digest(read_once(project.root))
                if recovering:
                    if record.get('planning_baseline_hash')!=baseline:raise ValueError('capture_plan_missing')
                else:
                    record['planning_baseline_hash']=baseline
                    store.write(oid,'operation',record)
            lock=db.execute(select(locks).where(locks.c.scope_key==project.key)).mappings().first()
            fence=(lock['fencing_token'] if lock else 0)+1;worker_id=str(uuid4())
            values={'operation_id':oid,'fencing_token':fence,'worker_id':worker_id,'updated_at':service.now()}
            if lock:db.execute(update(locks).where(locks.c.scope_key==project.key).values(**values))
            else:db.execute(insert(locks).values(scope_key=project.key,**values))
            db.execute(update(applications).where(applications.c.id==oid).values(fencing_token=fence,worker_id=worker_id,state='recovering' if recovering else 'applying',phase='validating'));db.commit()
            if record['kind'] in ('capture', 'capture_batch') and not record.get('planned'):
                from app.governance.capture import plan, batch_plan
                planner = batch_plan if record['kind'] == 'capture_batch' else plan
                record.update(planner(project, record['payload'], row['actor_id'], oid))
                store.write(oid, 'operation', record)
                before = {p: b.encode() for p, b in record['before'].items()}
                after = {p: b.encode() for p, b in record['after'].items()}
            current=read_once(project.root)
            expected=dict(before)
            if recovering:
                for path,body in after.items():
                    actual=current.get(path)
                    if actual==body: expected[path]=body
                    elif actual!=before.get(path):raise ValueError('external_change')
            if current!=expected: raise ValueError('source_conflict')
            reader=ProjectReader(db,row['actor_id'],project)
            if record['kind'] not in ('capture', 'capture_batch'):
                authorized = reader.authorize_object(Snapshot(before,digest(before)),record['object_id'],change=record.get('function')=='update_requirement_center_change_document',write=True)
                if record.get('function') == 'update_requirement_center_change_document' and not authorized:
                    raise ValueError('standalone_change_readonly')
            if record['kind']=='req-generate':
                if row['candidate_id'] is None: raise ValueError('candidate_missing')
                candidate=db.execute(select(candidates).where(candidates.c.id==row['candidate_id'])).mappings().one()
                service.conversation(db,row['actor_id'],candidate['conversation_id'])
                result=validate(before,{**before,**after},record['object_id'],record['base_path'])
                if result['manifest_hash']!=candidate['manifest_hash']: raise ValueError('candidate_changed')
            elif record['kind'] in ('capture', 'capture_batch'):
                if not record.get('planned') or not record.get('object_id'): raise ValueError('invalid_capture_plan')
            else:
                # Reapply legacy capability/task-toggle validation to the original immutable input.
                with materialize(Snapshot(before,digest(before))) as root,legacy.using_governance_root(root):
                    kwargs={'task_toggle':record['task_toggle']} if 'change_document' in record['function'] else {}
                    getattr(legacy,record['function'])(record['object_id'],record['document_name'],record['content'],**kwargs)
                    if read_once(root)!={**before,**after}:raise ValueError('write_set_changed')
            record['phase']='prepared';store.write(oid,'operation',record)
            set_state(db,oid,'recovering' if recovering else 'applying','prepared')
            for index,(path,body) in enumerate(sorted(after.items())):
                if record['kind']=='capture_batch':project=refresh_capture_authorization(db,row,record)
                write_permission(project, record.get('kind'))
                actual=read_once(project.root)
                if actual!=expected: raise ValueError('external_change')
                if actual.get(path)!=body:
                    wrote=True
                    replace_file(project.root,path,before.get(path),body,oid,create_parents=record['kind'] in ('capture','capture_batch'))
                expected[path]=body
                if after_write: after_write(index,path)
                record['phase']=f'file-{index+1}';store.write(oid,'operation',record)
                set_state(db,oid,'applying',record['phase'])
            if record['kind']=='capture_batch':project=refresh_capture_authorization(db,row,record)
            if stable(project.root).files!={**before,**after}:raise ValueError('final_conflict')
            if record['kind'] == 'capture_batch':
                from app.governance.capture_confirmations import complete
                complete(db, project, record['payload']['task_id'], record['issue_links'])
            set_state(db,oid,'applied','verified')
            if row['candidate_id']:
                db.execute(update(candidates).where(candidates.c.id==row['candidate_id']).values(state='applied',updated_at=service.now()))
            db.execute(update(locks).where(locks.c.scope_key==project.key,locks.c.fencing_token==fence).values(operation_id=None,worker_id=None));db.commit()
        except (ValueError,OSError,service.ChatError,PermissionError):
            # If any file may have changed, preserve all recovery evidence and block further writes.
            latest=db.execute(select(applications.c.state).where(applications.c.id==oid)).scalar_one()
            state='recovery_blocked' if recovering or wrote else 'conflict'
            set_state(db,oid,state,'verification_failed','source_or_permission_conflict')
            if state=='conflict':
                db.execute(update(locks).where(locks.c.scope_key==project.key,locks.c.operation_id==oid).values(operation_id=None,worker_id=None));db.commit()
        return public(db.execute(select(applications).where(applications.c.id==oid)).mappings().one())
