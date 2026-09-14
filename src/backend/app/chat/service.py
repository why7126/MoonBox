from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4, uuid5, NAMESPACE_URL
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete, and_, func, insert, or_, select, text, update
from sqlalchemy.orm import Session
from app.chat.schema import conversations, turns, events, messages, diffs

ACTIVE = ('queued', 'connecting', 'running', 'stopping', 'unknown')
TERMINAL = ('completed', 'failed', 'stopped')

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def identity():
    stamp = now()
    return {'id': str(uuid4()), 'created_at': stamp, 'updated_at': stamp}

class ChatError(Exception):
    def __init__(self, code: int, message: str, status: int = 409, *, kind: str | None = None):
        self.code, self.message, self.status = code, message, status
        self.kind = kind


def authorize_space(db: Session, actor: str, space_id: str):
    row = db.execute(text('''SELECT s.id, s.expires_at FROM admin_spaces s WHERE s.id=:space
        AND s.status='ACTIVE' AND s.deleted_at IS NULL
        AND (s.owner_id=:actor OR EXISTS (SELECT 1 FROM admin_space_members m
          WHERE m.space_id=s.id AND m.user_id=:actor))'''),
        {'space': space_id, 'actor': actor}).first()
    if not row:
        raise ChatError(2501, '空间不可访问', 403)
    if row.expires_at is not None:
        try:
            expiry = datetime.fromisoformat(str(row.expires_at).replace('Z', '+00:00'))
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
        except ValueError:
            raise ChatError(2501, '空间有效期不可确认', 403)
        if expiry <= datetime.now(timezone.utc):
            raise ChatError(2501, '空间已到期', 403)


def conversation(db, actor, conversation_id):
    row = db.execute(select(conversations).where(conversations.c.id == conversation_id,
        conversations.c.owner_id == actor, conversations.c.deleted_at.is_(None))).mappings().first()
    if not row:
        raise ChatError(2502, '会话不存在或无权访问', 404)
    authorize_space(db, actor, row['space_id'])
    from app.chat.settings import repository_catalog
    if not any(item['id']==row['repository_id'] and item['space_id']==row['space_id'] for item in repository_catalog()):
        raise ChatError(2503,'会话仓库已撤销或不可访问',403)
    from app.chat.relations import authorize_history
    authorize_history(db, actor, dict(row))
    return dict(row)


def public_conversation(row):
    return {k: row[k] for k in ('id', 'space_id', 'repository_id', 'title', 'pinned', 'archived', 'active_turn_id', 'created_at', 'updated_at')}


def create_conversation(db, actor, space_id, repository_id, title, client_request_id=None):
    authorize_space(db, actor, space_id)
    # Repository IDs are opaque; paths are never accepted from the client.
    from app.chat.settings import repository_catalog
    if not any(r['id'] == repository_id and r['space_id'] == space_id for r in repository_catalog()):
        raise ChatError(2503, '仓库尚未配置或不可用', 503)
    row = {**identity(), 'owner_id': actor, 'space_id': space_id, 'repository_id': repository_id,
           'title': title, 'pinned': 0, 'archived': 0, 'active_turn_id': None, 'generation': 0}
    if client_request_id:
        row['id'] = str(uuid5(NAMESPACE_URL, json.dumps(['moonbox.chat.create.v1', actor, client_request_id])))
        existing = db.execute(select(conversations.c.id).where(conversations.c.id == row['id'])).first()
        if existing:
            return _created_replay(db, actor, row['id'], space_id, repository_id)
    try:
        db.execute(insert(conversations).values(**row)); db.commit()
    except IntegrityError:
        db.rollback()
        if not client_request_id: raise
        return _created_replay(db, actor, row['id'], space_id, repository_id)
    return public_conversation(row)


def _created_replay(db, actor, cid, space_id, repository_id):
    existing = conversation(db, actor, cid)
    if existing['space_id'] != space_id or existing['repository_id'] != repository_id:
        raise ChatError(2504, '创建请求标识已用于其他空间或仓库')
    return public_conversation(existing)


def list_conversations(db, actor, space_id, query, archived, page, page_size, filter=None):
    authorize_space(db, actor, space_id)
    conditions = [conversations.c.owner_id == actor, conversations.c.space_id == space_id,
                  conversations.c.deleted_at.is_(None)]
    if filter not in ('all','pinned'):conditions.append(conversations.c.archived == int(archived))
    if filter=='pinned':conditions.append(conversations.c.pinned==1)
    from app.chat.relations import authorize_history, read_relations
    # Filter before pagination/count so even titles and totals cannot reveal revoked context.
    rows = db.execute(select(conversations).where(*conditions).order_by(conversations.c.pinned.desc(),
        conversations.c.updated_at.desc(), conversations.c.id)).mappings().all()
    visible=[]
    for row in rows:
        try:
            authorize_history(db,actor,row)
            relation=read_relations(db,actor,row['id'])
        except ChatError: continue
        objects=([relation['primary']] if relation['primary'] else [])+relation['references']
        searchable=' '.join([row['title'], *[item['id']+' '+item['title'] for item in objects]])
        if query.casefold() not in searchable.casefold(): continue
        visible.append(public_conversation(row))
    start=(page-1)*page_size
    return {'items':visible[start:start+page_size], 'total':len(visible), 'page':page, 'page_size':page_size}


def change_conversation(db, actor, cid, values):
    row = conversation(db, actor, cid)
    if 'archived' in values and row['active_turn_id']:
        raise ChatError(2504, '存在活动或状态未知的运行')
    result = db.execute(update(conversations).where(conversations.c.id == cid,
        conversations.c.active_turn_id.is_(None) if 'archived' in values else True,
        conversations.c.deleted_at.is_(None)).values(**values, updated_at=now()))
    if result.rowcount != 1:
        db.rollback(); raise ChatError(2504, '会话状态已变化')
    db.commit()
    return public_conversation(conversation(db, actor, cid))


def turn(db, actor, tid):
    row = db.execute(select(turns).where(turns.c.id == tid)).mappings().first()
    if not row:
        raise ChatError(2502, '轮次不存在或无权访问', 404)
    conversation(db, actor, row['conversation_id'])
    return dict(row)


def public_turn(row):
    return {k: row[k] for k in ('id','conversation_id','client_request_id','status','retry_of','error_code','created_at','updated_at')}


def request_turn(db, actor, cid, client_id, prompt, *, request_id=None):
    row = conversation(db, actor, cid)
    previous = db.execute(select(turns).where(turns.c.conversation_id == cid, turns.c.client_request_id == client_id)).mappings().first()
    if previous:
        if previous['prompt'] != prompt:
            raise ChatError(2504, '同一请求标识不能用于不同输入')
        return public_turn(previous)
    if row['archived']:
        raise ChatError(2504, '归档会话只读')
    if row['active_turn_id']:
        raise ChatError(2504, '原运行尚未终止或状态未知')
    from app.governance.preparation import check_send
    check_send(db, actor, row)
    from app.chat.isolated import allowed
    if allowed(db,actor,row['space_id'],row['repository_id']):
        from app.chat.admission import enqueue
        from app.chat.settings import execution_limits
        return enqueue(db,actor,cid,client_id,prompt,execution_limits(),request_id=request_id)
    # Normal deployment stays closed; only the isolated launcher has a test gate.
    raise ChatError(2505, '执行服务尚未通过隔离与额度验收，暂不可发送', 503)


def interrupt(db, actor, tid):
    row = turn(db, actor, tid)
    if row['status'] in TERMINAL:
        return public_turn(row)
    if row['status'] == 'unknown':
        raise ChatError(2506, '原运行状态未知，需先核实执行端')
    if row['status'] == 'queued':
        changed = db.execute(update(turns).where(turns.c.id == tid, turns.c.status == 'queued').values(status='stopped', updated_at=now())).rowcount
        if changed:
            db.execute(update(conversations).where(conversations.c.id == row['conversation_id'], conversations.c.active_turn_id == tid).values(active_turn_id=None, updated_at=now()))
            from app.chat.admission import settle
            from app.chat.schema import snapshots
            context_bytes=sum(len(value.encode()) for value in db.scalars(select(snapshots.c.content).where(snapshots.c.turn_id==tid)))
            from app.chat.observability import trace
            trace(db,tid,'stopped')
            settle(db,tid,0,len(row['prompt'].encode())+context_bytes)
            db.commit(); return public_turn(turn(db, actor, tid))
    db.execute(update(turns).where(turns.c.id == tid, turns.c.status.in_(('connecting','running'))).values(status='stopping', updated_at=now()))
    db.commit()
    return public_turn(turn(db, actor, tid))


def read_events(db, actor, tid, after):
    turn(db, actor, tid)
    rows = db.execute(select(events).where(events.c.turn_id == tid, events.c.sequence > after).order_by(events.c.sequence).limit(200)).mappings()
    return [{'sequence': r['sequence'], 'type': r['event_type'], 'payload': json.loads(r['payload'])} for r in rows]


def read_diff(db, actor, tid):
    turn(db, actor, tid)
    row = db.execute(select(diffs).where(diffs.c.turn_id == tid)).mappings().first()
    if not row:
        return {'available': False, 'reason': '尚无可信差异快照', 'files': []}
    payload = json.loads(row['payload'])
    return {'available': True, 'before_hash': row['before_hash'], 'after_hash': row['after_hash'], **(payload if isinstance(payload, dict) else {'files': payload})}


def delete_empty_conversation(db, actor, cid):
    row = conversation(db, actor, cid)
    from app.chat.schema import governance_candidates
    if db.scalar(select(governance_candidates.c.id).where(governance_candidates.c.conversation_id == cid)):
        raise ChatError(2605, '治理成果仍在保留期内，不能删除会话', 409)
    if row['active_turn_id'] or db.scalar(select(func.count()).select_from(turns).where(turns.c.conversation_id == cid)):
        raise ChatError(2507, '包含执行数据的会话需先验证代码及副本清理状态，暂不可删除')
    # The conversation is tombstoned, so later writes cannot resurrect it.
    changed = db.execute(update(conversations).where(conversations.c.id == cid,
        conversations.c.active_turn_id.is_(None), conversations.c.deleted_at.is_(None)).values(
            deleted_at=now(), updated_at=now(), title='', cleanup_status='empty_tombstone')).rowcount
    if not changed:
        db.rollback(); raise ChatError(2504, '会话状态已变化')
    from app.chat.schema import relations
    db.execute(delete(relations).where(relations.c.conversation_id==cid))
    db.commit()


def request_retry(db, actor, tid, client_id, *, request_id=None):
    original=turn(db,actor,tid)
    parent=conversation(db,actor,original['conversation_id'])
    previous=db.execute(select(turns).where(turns.c.conversation_id==parent['id'],turns.c.client_request_id==client_id)).mappings().first()
    if previous:
        if previous['retry_of'] != tid: raise ChatError(2504,'同一请求标识不能用于不同重试')
        return public_turn(previous)
    if original['status'] not in ('failed','stopped') or parent['active_turn_id'] or parent['archived']:
        raise ChatError(2506,'原运行未确认失败或停止，或会话当前不可重试')
    from app.chat.isolated import allowed
    if allowed(db,actor,parent['space_id'],parent['repository_id']):
        from app.chat.admission import enqueue
        from app.chat.settings import execution_limits
        return enqueue(db,actor,parent['id'],client_id,original['prompt'],execution_limits(),retry_of=tid,request_id=request_id)
    raise ChatError(2505,'执行服务尚未通过隔离与额度验收，暂不可重试',503)
