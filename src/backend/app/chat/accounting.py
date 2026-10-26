"""仅以执行端可信事实补结算；没有用量不释放预留。"""
import json
from sqlalchemy import select, update
from app.chat.schema import events, reservations, turns
from app.chat.admission import settle, release_concurrency


def stored_metadata_bytes(db, tid):
    """Count persisted UTF-8 payloads, independent of DB pages, WAL and indexes."""
    from sqlalchemy import func, cast, LargeBinary
    from app.chat.schema import messages, snapshots, diffs
    total = 0
    for table, column in ((messages, messages.c.content),
                          (snapshots, snapshots.c.content), (diffs, diffs.c.payload)):
        length = func.octet_length(column) if db.get_bind().dialect.name == 'mysql' else func.length(cast(column, LargeBinary))
        total += db.scalar(select(func.coalesce(func.sum(length), 0)).where(table.c.turn_id == tid)) or 0
    # Preparing the same turn again does not duplicate its prompt/reference rows.
    # Earlier attempts already settled these bytes; charge only the new remainder.
    from app.chat.content_schema import prepare_attempts
    prior = db.scalar(select(func.coalesce(func.sum(prepare_attempts.c.prior_bytes), 0))
        .where(prepare_attempts.c.turn_id == tid)) or 0
    # MySQL SUM(BigInteger) returns Decimal; this is an exact integer byte count.
    return max(0, int(total)-int(prior))


def reconcile_usage(db, tid):
    row=db.execute(select(turns).where(turns.c.id==tid)).mappings().first()
    if not row or row['status'] not in ('completed','failed','stopped'):return False
    # Repair terminal reservations left by older workers without inventing usage.
    release_concurrency(db, tid)
    db.commit()
    receipt=db.scalar(select(events.c.payload).where(events.c.turn_id==tid,events.c.source_id=='runner:accounting'))
    trusted_archive=False
    if not receipt and not row['executor_turn_id']:
        receipt=db.scalar(select(events.c.payload).where(events.c.turn_id==tid,events.c.source_id=='archive:usage'))
        started=db.scalar(select(events.c.payload).where(events.c.turn_id==tid,events.c.source_id=='archive:started'))
        if receipt and started:
            trusted_archive=(json.loads(started).get('executor')=='trusted_archive'
                and json.loads(receipt).get('usage_scope')=='trusted_archive_v1'
                and json.loads(receipt).get('total_tokens')==0)
    if not receipt:return False
    data=json.loads(receipt)
    if data.get('usage_scope') != 'app_server_process_v1' and not trusted_archive:
        db.execute(update(turns).where(turns.c.id==tid, turns.c.error_code.is_(None),
            turns.c.id.in_(select(reservations.c.turn_id).where(reservations.c.status=='reserved'))
        ).values(error_code='usage_unavailable'))
        db.commit();return False
    if data.get('total_tokens') is None:return False
    actual_bytes = stored_metadata_bytes(db, tid) if row['reserved_bytes'] == 0 else data['actual_bytes']
    changed=settle(db,tid,data['total_tokens'],actual_bytes,revised_receipt=True)
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
