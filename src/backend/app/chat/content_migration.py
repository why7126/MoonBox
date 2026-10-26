"""Resumable, conversation-at-a-time v1 baseline backfill; no old data deletion."""
import json
from sqlalchemy import select, update
from app.chat.schema import conversations, turns, workspace_baselines
from app.chat.snapshot_store import import_legacy


def batch(factory, after='', limit=10):
    if not 1 <= limit <= 100: raise ValueError('invalid migration window')
    with factory() as db:
        ids = list(db.scalars(select(workspace_baselines.c.conversation_id)
            .where(workspace_baselines.c.conversation_id > after)
            .order_by(workspace_baselines.c.conversation_id).limit(limit)))
    migrated = 0
    for cid in ids:
        with factory() as db:
            parent = db.execute(select(conversations).where(conversations.c.id == cid).with_for_update()).mappings().first()
            if not parent or parent['deleted_at'] or parent['active_turn_id']: continue
            baseline = db.execute(select(workspace_baselines).where(workspace_baselines.c.conversation_id == cid)).mappings().one()
            old = json.loads(baseline['payload'])
            if old.get('format_version') == 2: continue
            tid = db.scalar(select(turns.c.id).where(turns.c.conversation_id == cid).order_by(turns.c.created_at, turns.c.id).limit(1))
            if not tid: continue
            reference = import_legacy(db, cid, tid, old)
            # Publication and pointer swap share a transaction. Failed work leaves v1 readable.
            db.execute(update(workspace_baselines).where(workspace_baselines.c.conversation_id == cid)
                .values(payload=json.dumps(reference, ensure_ascii=False)))
            db.commit(); migrated += 1
    return {'migrated': migrated, 'next_cursor': ids[-1] if len(ids) == limit else None}


def main():
    import argparse
    from app.db.session import get_session_factory
    parser = argparse.ArgumentParser(description='按会话窗口回填旧 Chat 基线，保留旧格式读取能力')
    parser.add_argument('--after', default='')
    parser.add_argument('--limit', type=int, default=10)
    args = parser.parse_args()
    print(json.dumps(batch(get_session_factory(), args.after, args.limit)))


if __name__ == '__main__': main()
