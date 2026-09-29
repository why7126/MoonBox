"""Immutable business confirmation; changing a request key never creates another batch."""
import hashlib
import json
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from app.chat.service import identity, now, ChatError
from app.governance import capture_drafts as service, writer, scope
from app.governance.capture_schema import drafts, confirmations, quotas, links, materials, confirmation_keys


def remember_key(db,actor,project,key_hash,task_id):
    where=(confirmation_keys.c.actor_id==actor)&(confirmation_keys.c.scope_key==project.key)&(confirmation_keys.c.key_hash==key_hash)
    previous=db.scalar(select(confirmation_keys.c.task_id).where(where))
    if previous is None:
        try:
            with db.begin_nested():db.execute(insert(confirmation_keys).values(actor_id=actor,scope_key=project.key,key_hash=key_hash,task_id=task_id))
            return
        except IntegrityError:previous=db.scalar(select(confirmation_keys.c.task_id).where(where))
    if previous!=task_id:
        db.rollback();service.error('幂等键已绑定其他确认内容',reason='idempotency_conflict')


def confirm(db, actor, project, draft_id, revision, key, request_id=None):
    draft=service.get(db,actor,project,draft_id,write=True)
    key_hash=hashlib.sha256(key.encode()).hexdigest()
    keyed=db.execute(select(confirmations).where(confirmations.c.actor_id==actor,confirmations.c.scope_key==project.key,
        confirmations.c.idempotency_hash==key_hash)).mappings().first()
    if keyed and (keyed['draft_id']!=draft_id or keyed['revision']!=revision):service.error('幂等键已绑定其他确认内容',reason='idempotency_conflict')
    existing=db.execute(select(confirmations).where(confirmations.c.draft_id==draft_id)).mappings().first()
    if existing:
        if existing['revision']!=revision:service.error('该草稿已确认其他版本，请查看原任务')
        remember_key(db,actor,project,key_hash,existing['id'])
        return enqueue(db,actor,project,existing,request_id)
    if draft['state']!='editing' or draft['revision']!=revision:service.error()
    payload=json.loads(draft['payload'])
    if not payload['candidates']:service.error('没有可创建的候选',422)
    service.validate_materials(db,actor,project,draft_id,service.protected_media(payload))
    writer.write_permission(project,'capture_batch');writer.assert_readable(db,project)
    row={**identity(),'draft_id':draft_id,'revision':revision,'actor_id':actor,'scope_key':project.key,
         'snapshot_hash':writer.hash_request(payload),'payload':service.encode(payload),
         'idempotency_hash':key_hash,'operation_id':None,'state':'accepted'}
    claimed=db.execute(update(drafts).where(drafts.c.id==draft_id,drafts.c.revision==revision,
        drafts.c.state=='editing',drafts.c.deleted_at.is_(None),drafts.c.confirmed_task_id.is_(None))
        .values(state='confirmed',confirmed_task_id=row['id'],updated_at=now()))
    if claimed.rowcount!=1:
        db.rollback()
        existing=db.execute(select(confirmations).where(confirmations.c.draft_id==draft_id)).mappings().first()
        if existing and existing['revision']==revision:
            remember_key(db,actor,project,key_hash,existing['id'])
            return enqueue(db,actor,project,existing,request_id)
        service.error()
    retained=service.validate_materials(db,actor,project,draft_id,service.protected_media(payload))
    transferred=sum(item['size'] for item in retained if item['state'] in ('ready','detached'))
    if transferred:
        db.execute(update(quotas).where(quotas.c.actor_id==actor,quotas.c.scope_key==project.key).values(material_bytes=quotas.c.material_bytes-transferred))
        db.execute(update(materials).where(materials.c.id.in_(service.protected_media(payload))).values(state='retained',updated_at=now()))
    try:db.execute(insert(confirmations).values(**row))
    except IntegrityError:
        db.rollback();service.error('幂等键已绑定其他确认内容',reason='idempotency_conflict')
    remember_key(db,actor,project,key_hash,row['id'])
    from app.governance.capture_observability import trace
    trace(db,row['id'],'queued',actor=actor,request_id=request_id,kind='capture_confirmation')
    db.execute(update(quotas).where(quotas.c.actor_id==actor,quotas.c.scope_key==project.key,
        quotas.c.draft_count>0).values(draft_count=quotas.c.draft_count-1))
    db.commit()
    return enqueue(db,actor,project,row,request_id)


def enqueue(db,actor,project,row,request_id=None):
    payload=json.loads(row['payload'])
    service.validate_materials(db,actor,project,row['draft_id'],service.protected_media(payload))
    values={'candidates':payload['candidates'],'origins':payload.get('origins',{}),'owner':actor,'task_id':row['id'],'revision':row['revision']}
    result=writer.enqueue(db,actor,project,'capture-confirmation:'+row['id'],
        {'kind':'capture_batch','task_id':row['id'],'snapshot_hash':row['snapshot_hash']},
        {'kind':'capture_batch','payload':values,'before':{},'after':{}},request_id=request_id)
    db.execute(update(confirmations).where(confirmations.c.id==row['id']).values(operation_id=result['id'],updated_at=now()))
    db.commit()
    return status(db,actor,project,row['id'])


def status(db,actor,project,task_id):
    service.authorize(db,actor,project)
    row=db.execute(select(confirmations).where(confirmations.c.id==task_id,confirmations.c.actor_id==actor,
        confirmations.c.scope_key==project.key)).mappings().first()
    if not row:raise ChatError(2601,'确认任务不存在或无权访问',404)
    service.get(db,actor,project,row['draft_id'])
    result={'id':row['id'],'revision':row['revision'],'state':'accepted','phase':'queued','issue_links':[]}
    if row['operation_id']:
        operation=writer.operation(db,actor,row['operation_id'])
        result.update(state='completed' if operation['state']=='applied' else operation['state'],phase=operation['phase'])
        if result['state']=='completed':
            found=db.execute(select(links).where(links.c.task_id==task_id)).mappings().all()
            for item in found:
                if not scope.visible(db,actor,project,item['issue_id']):raise ChatError(2601,'采集结果不可访问',403)
            result['issue_links']=[{'candidate_id':v['candidate_id'],'issue_id':v['issue_id']} for v in found]
    return result


def complete(db,project,task_id,issue_links):
    row=db.execute(select(confirmations).where(confirmations.c.id==task_id,confirmations.c.scope_key==project.key)).mappings().one()
    expected={c['id'] for c in json.loads(row['payload'])['candidates']}
    if expected!={v['candidate_id'] for v in issue_links}:raise ValueError('capture_mapping_mismatch')
    existing={v['candidate_id']:v['issue_id'] for v in db.execute(select(links).where(links.c.task_id==task_id)).mappings()}
    for item in issue_links:
        if item['candidate_id'] in existing:
            if existing[item['candidate_id']]!=item['issue_id']:raise ValueError('capture_mapping_conflict')
        else:db.execute(insert(links).values(**identity(),task_id=task_id,scope_key=project.key,
            candidate_id=item['candidate_id'],issue_id=item['issue_id']))
    db.execute(update(confirmations).where(confirmations.c.id==task_id).values(state='completed',updated_at=now()))


def source(db,actor,project,issue_id):
    service.authorize(db,actor,project)
    if not scope.visible(db,actor,project,issue_id):raise ChatError(2601,'来源不可访问',403)
    item=db.execute(select(links).where(links.c.scope_key==project.key,links.c.issue_id==issue_id)).mappings().first()
    if not item:raise ChatError(2601,'来源不存在',404)
    row=db.execute(select(confirmations).where(confirmations.c.id==item['task_id'],confirmations.c.actor_id==actor)).mappings().first()
    if not row:raise ChatError(2601,'来源不存在或无权访问',404)
    return {'task_id':row['id'],'candidate_id':item['candidate_id'],'revision':row['revision'],'content':json.loads(row['payload'])}


def retry(db,actor,project,task_id):
    current=status(db,actor,project,task_id)
    if current['state']=='completed':return current
    row=db.execute(select(confirmations).where(confirmations.c.id==task_id,confirmations.c.actor_id==actor)).mappings().one()
    service.authorize(db,actor,project,write=True)
    if not row['operation_id']:return enqueue(db,actor,project,row)
    from app.chat.schema import governance_applications
    from app.governance import store
    from app.governance.snapshot import read_once
    with writer.project_lock(project):
        writer.write_permission(project,'capture_batch')
        record=store.read(row['operation_id'],'operation')
        if record['binding_revision']!=project.binding_revision:service.error('项目绑定已变化，不能恢复')
        if record.get('planned'):
            before={p:b.encode() for p,b in record['before'].items()}
            after={p:b.encode() for p,b in record['after'].items()}
            actual=read_once(project.root)
            if set(actual)-set(before)-set(after):service.error('存在外部修改，请先核对恢复冲突')
            if any(actual.get(p) not in ((before.get(p),after[p]) if p in after else (before[p],)) for p in set(before)|set(after)):
                service.error('文件已被外部修改，原任务保留，请先核对冲突')
            state='recovering'
        else:
            if current['state']=='recovery_blocked':service.error('恢复计划不可用，需核对持久化证据',reason='recovery_blocked')
            state='pending'
        db.execute(update(governance_applications).where(governance_applications.c.id==row['operation_id'],
            governance_applications.c.state.in_(('conflict','failed','recovery_blocked')))
            .values(state=state,error_code=None,updated_at=now()))
        db.commit()
    return status(db,actor,project,task_id)
