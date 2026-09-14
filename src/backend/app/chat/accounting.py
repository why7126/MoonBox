"""仅以执行端可信事实补结算；没有用量不释放预留。"""
import json
from sqlalchemy import select, update
from app.chat.schema import events, reservations, turns
from app.chat.admission import settle, release_concurrency


def reconcile_usage(db, tid):
    row=db.execute(select(turns).where(turns.c.id==tid)).mappings().first()
    if not row or row['status'] not in ('completed','failed','stopped'):return False
    # Repair terminal reservations left by older workers without inventing usage.
    release_concurrency(db, tid)
    db.commit()
    receipt=db.scalar(select(events.c.payload).where(events.c.turn_id==tid,events.c.source_id=='runner:accounting'))
    if not receipt:return False
    data=json.loads(receipt)
    if data.get('usage_scope') != 'app_server_process_v1':
        db.execute(update(turns).where(turns.c.id==tid, turns.c.error_code.is_(None),
            turns.c.id.in_(select(reservations.c.turn_id).where(reservations.c.status=='reserved'))
        ).values(error_code='usage_unavailable'))
        db.commit();return False
    if data.get('total_tokens') is None:return False
    changed=settle(db,tid,data['total_tokens'],data['actual_bytes'])
    if changed:
        if row['error_code'] in ('usage_unavailable','reconciled_usage_pending'):
            db.execute(update(turns).where(turns.c.id==tid).values(error_code=None))
        db.commit()
    return changed


def pending(db):
    # Safe operational summary: no prompt, credential, path or fabricated cost.
    return [dict(row) for row in db.execute(select(turns.c.id,turns.c.status,turns.c.error_code)
        .join(reservations,reservations.c.turn_id==turns.c.id)
        .where(reservations.c.status=='reserved',turns.c.status.in_(('completed','failed','stopped')))).mappings()]


def main():
    import argparse
    from app.db.session import get_session_factory
    parser=argparse.ArgumentParser(description='读取待对账轮次；只以已持久化的执行端用量补结算')
    parser.add_argument('--turn',help='尝试补结算指定轮次，不接受手填用量')
    args=parser.parse_args()
    with get_session_factory()() as db:
        changed=reconcile_usage(db,args.turn) if args.turn else False
        print(json.dumps({'settled':changed,'pending':pending(db)},ensure_ascii=False))

if __name__=='__main__':main()
