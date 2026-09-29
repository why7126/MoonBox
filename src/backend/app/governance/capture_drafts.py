"""Versioned Capture drafts. No source-tree writer is imported on this path."""
import json
from uuid import uuid4
from sqlalchemy import insert, select, update, func
from sqlalchemy.exc import IntegrityError
from app.chat.service import ChatError, identity, now
from app.governance import scope
from app.governance.capture_schema import drafts, revisions, quotas, materials
from app.schemas.capture_drafts import DraftContent

LIMITS = {'max_images':10, 'max_image_bytes':10*1024*1024, 'max_total_image_bytes':50*1024*1024,
          'max_pixels':20_000_000, 'max_text_codepoints':20000, 'max_candidates':50,
          'max_title_codepoints':60, 'max_description_codepoints':10000,
          'max_drafts':50, 'max_material_bytes':1024**3,
          'image_types':['image/png','image/jpeg','image/webp']}

def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))

def error(message='草稿版本已变化，请重新读取并保留本次修改', status=409, *, reason=None):
    raise ChatError(2606 if status == 409 else 2604, message, status,kind=reason or ('revision_conflict' if status==409 else 'invalid_candidates'))

def authorize(db, actor, project, *, write=False):
    current=scope.authorize(db,actor,project.space_id,project.repository_id,write=write)
    if current.binding_revision != project.binding_revision:
        error('项目绑定已变化，请重新加载',reason='binding_changed')
    return current

def get(db, actor, project, draft_id, *, write=False):
    authorize(db, actor, project, write=write)
    row=db.execute(select(drafts).where(drafts.c.id==draft_id,drafts.c.actor_id==actor,
        drafts.c.scope_key==project.key)).mappings().first()
    if not row: raise ChatError(2601,'草稿不存在或无权访问',404)
    if row['deleted_at']: error('草稿已删除',410)
    from app.governance.capture_cleanup import deleted
    if deleted(draft_id,actor,project.key):error('草稿已删除，清理正在恢复',410)
    if row['binding_revision'] != project.binding_revision: error('草稿项目绑定已变化',reason='binding_changed')
    return row

def public(row):
    payload=json.loads(row['payload'])
    return {'id':row['id'],'revision':row['revision'],'state':row['state'],
            'content':{key:payload[key] for key in ('text','media_ids','candidates')},
            'updated_at':row['updated_at'],'confirmed_task_id':row['confirmed_task_id']}

def ensure_quota(db, actor, project):
    existing=db.execute(select(quotas).where(quotas.c.actor_id==actor,quotas.c.scope_key==project.key)).first()
    if existing:return
    try:
        with db.begin_nested():
            db.execute(insert(quotas).values(actor_id=actor,scope_key=project.key,draft_count=0,material_bytes=0))
    except IntegrityError:pass

def create(db, actor, project):
    authorize(db,actor,project,write=True);ensure_quota(db,actor,project)
    claimed=db.execute(update(quotas).where(quotas.c.actor_id==actor,quotas.c.scope_key==project.key,
        quotas.c.draft_count<LIMITS['max_drafts']).values(draft_count=quotas.c.draft_count+1))
    if claimed.rowcount != 1:
        db.rollback();error('未确认草稿已达50个，请先查看或删除已有草稿',422,reason='quota_exceeded')
    row={**identity(),'actor_id':actor,'space_id':project.space_id,'repository_id':project.repository_id,
         'scope_key':project.key,'binding_revision':project.binding_revision,'revision':1,'state':'editing',
         'payload':encode({'text':'','media_ids':[],'candidates':[],'history':{}}),
         'confirmed_task_id':None,'deleted_at':None}
    db.execute(insert(drafts).values(**row))
    db.execute(insert(revisions).values(**identity(),draft_id=row['id'],revision=1,payload=row['payload']))
    db.commit();return public(row)

def listing(db, actor, project, page=1, page_size=20):
    authorize(db,actor,project)
    where=(drafts.c.actor_id==actor)&(drafts.c.scope_key==project.key)&drafts.c.deleted_at.is_(None)
    total=db.scalar(select(func.count()).select_from(drafts).where(where))
    rows=db.execute(select(drafts).where(where).order_by(drafts.c.updated_at.desc(),drafts.c.id)
        .offset((page-1)*page_size).limit(page_size)).mappings()
    return {'items':[public(row) for row in rows],'total':total,'page':page,'page_size':page_size}

def validate_materials(db, actor, project, draft_id, media_ids):
    if len(set(media_ids))!=len(media_ids):error('材料重复',422)
    rows=list(db.execute(select(materials).where(materials.c.id.in_(media_ids),
        materials.c.draft_id==draft_id,materials.c.actor_id==actor,materials.c.scope_key==project.key,
        materials.c.state.in_(('ready','retained','detached')),materials.c.deleted_at.is_(None))).mappings()) if media_ids else []
    if len(rows)!=len(media_ids):error('图片失效或无权访问，请重新检查材料',422,reason='material_unreadable')
    if sum(row['size'] for row in rows)>LIMITS['max_total_image_bytes']:error('图片总量超过50 MiB',413,reason='quota_exceeded')
    return rows

def normalize(content, previous):
    value=DraftContent.model_validate(content).model_dump(exclude_none=True)
    previous_payload=json.loads(previous['payload'])
    history=dict(previous_payload.get('history',{}))
    origins=dict(previous_payload.get('origins',{}))
    old={item['id']:item for item in previous_payload['candidates']}
    refs=set(value['media_ids'])|({'text'} if value['text'].strip() else set())
    ids=set()
    for item in value['candidates']:
        cid=item.get('id')
        if cid and cid not in old:error('未知候选身份',422)
        parents=item.get('parents',[])
        if any(parent not in old and parent not in history for parent in parents):error('未知父候选',422)
        if cid and cid in ids:error('候选身份重复',422)
        if not set(item['source_refs'])<=refs:error('候选来源不在当前材料中',422)
        if len(item['clarifications'])>50 or any(len(v)>2000 for v in item['clarifications']):error('待澄清内容超限',422)
        if not cid:
            cid=str(uuid4());item['id']=cid
        elif item['parents']!=old[cid].get('parents',[]):error('候选来源关系不能被覆盖',422)
        origins.setdefault(cid,{'candidate':dict(item),'text':value['text']})
        ids.add(cid)
        # AI/user history remains in immutable prior revisions. Type edits never change IDs.
    for cid,item in old.items():
        if cid not in ids:history[cid]=item
    value['history']=history
    value['origins']=origins
    return value

def save(db, actor, project, draft_id, expected_revision, content):
    row=get(db,actor,project,draft_id,write=True)
    if row['state']!='editing' or row['revision']!=expected_revision:error()
    validate_materials(db,actor,project,draft_id,content.get('media_ids',[]))
    normalized=normalize(content,row);payload=encode(normalized);timestamp=now()
    changed=db.execute(update(drafts).where(drafts.c.id==draft_id,drafts.c.revision==expected_revision,
        drafts.c.state=='editing',drafts.c.deleted_at.is_(None)).values(payload=payload,
        revision=expected_revision+1,updated_at=timestamp))
    if changed.rowcount!=1:db.rollback();error()
    protected=protected_media(normalized)
    try:validate_materials(db,actor,project,draft_id,protected)
    except ChatError:
        db.rollback();raise
    db.execute(update(materials).where(materials.c.draft_id==draft_id,materials.c.state=='ready',
        materials.c.id.not_in(protected)).values(state='detached',updated_at=timestamp))
    db.execute(update(materials).where(materials.c.draft_id==draft_id,materials.c.state=='detached',
        materials.c.id.in_(protected)).values(state='ready',updated_at=timestamp))
    db.execute(insert(revisions).values(**identity(),draft_id=draft_id,revision=expected_revision+1,payload=payload))
    db.commit();return public(get(db,actor,project,draft_id))

def remove(db, actor, project, draft_id, expected_revision):
    row=get(db,actor,project,draft_id,write=True)
    changed=db.execute(update(drafts).where(drafts.c.id==draft_id,drafts.c.revision==expected_revision,
        drafts.c.state=='editing',drafts.c.confirmed_task_id.is_(None),drafts.c.deleted_at.is_(None))
        .values(state='deleted',deleted_at=now(),updated_at=now()))
    if changed.rowcount!=1:db.rollback();error('草稿已变化或正在创建，无法删除')
    from app.governance.capture_cleanup import record
    try:record(row)
    except (OSError,ValueError):
        db.rollback();raise ChatError(2605,'删除日志不可用，草稿未删除',503) from None
    db.execute(update(quotas).where(quotas.c.actor_id==actor,quotas.c.scope_key==project.key,
        quotas.c.draft_count>0).values(draft_count=quotas.c.draft_count-1))
    # Tombstone first; a cleanup worker removes only unreferenced blobs and execution copies.
    db.execute(update(materials).where(materials.c.draft_id==draft_id,materials.c.state.in_(('ready','uploading','detached')))
        .values(state='delete_pending',deleted_at=now(),updated_at=now()))
    db.commit();return {'id':draft_id,'state':'deleted','cleanup':'pending'}


def protected_media(payload):
    refs=set(payload['media_ids'])
    history=payload.get('history',{})
    origins=payload.get('origins',{})
    pending=list(payload['candidates']);seen=set()
    while pending:
        item=pending.pop();cid=item['id']
        if cid in seen:continue
        seen.add(cid)
        refs.update(item['source_refs'])
        origin=origins.get(cid,{}).get('candidate',{})
        refs.update(origin.get('source_refs',[]))
        pending.extend(history[parent] for parent in item.get('parents',[]) if parent in history)
    refs.discard('text')
    return sorted(refs)
