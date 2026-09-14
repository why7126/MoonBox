"""独立恢复 worker。租约失效只标记 unknown，绝不重启旧运行。"""
from __future__ import annotations

import argparse
import json
import signal
import time
from datetime import datetime, timedelta, timezone
from sqlalchemy import insert, select, update
from app.chat import service
from app.chat.schema import conversations, events, turns
from app.db.session import get_session_factory, init_database


def mark_stale_unknown(db, stale_seconds=120):
    cutoff=(datetime.now(timezone.utc)-timedelta(seconds=stale_seconds)).isoformat(timespec='seconds')
    candidates=list(db.scalars(select(turns.c.id).where(turns.c.status.in_(('connecting','running','stopping')),turns.c.heartbeat_at<cutoff)))
    count=0
    from app.chat.observability import trace
    for tid in candidates:
        changed=db.execute(update(turns).where(turns.c.id==tid,turns.c.status.in_(('connecting','running','stopping')),turns.c.heartbeat_at<cutoff).values(status='unknown',error_code='worker_heartbeat_lost',updated_at=service.now())).rowcount
        if changed:count+=1;trace(db,tid,'unknown')
    # active_turn_id is deliberately retained; lease expiry is not termination evidence.
    db.commit()
    return count


def claim(db, worker_id):
    candidate=db.execute(select(turns).where(turns.c.status=='queued').order_by(turns.c.created_at,turns.c.id).limit(1)).mappings().first()
    if not candidate: return None
    cid=candidate['conversation_id']; tid=candidate['id']
    won=db.execute(update(turns).where(turns.c.id==tid,turns.c.status=='queued').values(
        status='connecting',worker_id=worker_id,heartbeat_at=service.now(),updated_at=service.now())).rowcount
    if won!=1:
        db.rollback();return None
    won=db.execute(update(conversations).where(conversations.c.id==cid,
        conversations.c.active_turn_id==tid,conversations.c.archived==0,
        conversations.c.deleted_at.is_(None)).values(generation=conversations.c.generation+1)).rowcount
    if won!=1:
        db.rollback();return None
    generation=db.scalar(select(conversations.c.generation).where(conversations.c.id==cid))
    db.execute(update(turns).where(turns.c.id==tid).values(generation=generation))
    from app.chat.observability import trace
    trace(db,tid,'connecting')
    db.commit()
    return {'turn_id':tid,'conversation_id':cid,'worker_id':worker_id,'generation':generation}


def record_event(db, claim_token, source_id, event_type, payload, terminal=None):
    """Serialize at the turn row, fence old workers, deduplicate before cursor allocation."""
    if event_type not in ('execution.state','execution.output','execution.usage','execution.tool'):
        raise ValueError('unsupported event type')
    if terminal is not None and terminal not in service.TERMINAL:
        raise ValueError('terminal state required')
    encoded=json.dumps(payload,ensure_ascii=False)
    if len(encoded.encode())>65536:
        raise ValueError('event payload exceeds page boundary')
    t=turns.c; token=claim_token
    won=db.execute(update(turns).where(t.id==token['turn_id'],t.worker_id==token['worker_id'],
        t.generation==token['generation'],t.status.in_(('connecting','running','stopping'))).values(
            heartbeat_at=service.now(),updated_at=service.now())).rowcount
    if won!=1:
        db.rollback();return False
    parent=db.execute(select(conversations).where(conversations.c.id==token['conversation_id'],
        conversations.c.active_turn_id==token['turn_id'],conversations.c.generation==token['generation'])).first()
    if not parent:
        db.rollback();return False
    previous=db.execute(select(events.c.id).where(events.c.turn_id==token['turn_id'],events.c.source_id==source_id)).first()
    if previous:
        db.rollback();return False
    from sqlalchemy import func
    seq=(db.scalar(select(func.max(events.c.sequence)).where(events.c.turn_id==token['turn_id'])) or 0)+1
    db.execute(insert(events).values(**service.identity(),turn_id=token['turn_id'],sequence=seq,
        source_id=source_id,event_type=event_type,payload=encoded))
    if not terminal and event_type == 'execution.state' and payload.get('status') == 'running':
        db.execute(update(turns).where(t.id==token['turn_id'],t.status=='connecting').values(status='running'))
    if terminal:
        db.execute(update(turns).where(t.id==token['turn_id']).values(status=terminal))
        db.execute(update(conversations).where(conversations.c.id==token['conversation_id'],conversations.c.active_turn_id==token['turn_id']).values(active_turn_id=None,updated_at=service.now()))
        from app.chat.admission import release_concurrency
        release_concurrency(db, token['turn_id'])
    from app.chat.observability import trace
    if terminal: trace(db,token['turn_id'],terminal)
    elif event_type=='execution.state' and payload.get('status')=='running':trace(db,token['turn_id'],'running')
    db.commit();return True


def main():
    parser=argparse.ArgumentParser(description='Chat 恢复 worker；当前不领取或执行模型任务')
    parser.add_argument('--once',action='store_true')
    args=parser.parse_args();running=True
    def stop(*_):
        nonlocal running
        running=False
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    init_database()
    while running:
        with get_session_factory()() as db:
            count=mark_stale_unknown(db)
            from app.chat.observability import prune
            try:prune(db)
            except Exception:
                db.rollback()
                print(json.dumps({'event':'chat.observability_prune_unavailable'}),flush=True)
        print(json.dumps({'event':'chat.reconcile','unknown_count':count,'execution_enabled':False}),flush=True)
        if args.once:return
        for _ in range(30):
            if not running:break
            time.sleep(1)

if __name__=='__main__':main()
