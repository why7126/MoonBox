"""Fenced answer checkpoints and bounded, non-destructive read projection."""
import hashlib
import json
from sqlalchemy import select, func, insert
from app.chat.schema import events
from app.chat.content_schema import segments, objects
from app.chat import service


def source(item_id):
    if not isinstance(item_id, str) or not item_id or len(item_id) > 256:
        # Never collapse unrelated unidentified items onto final:None.
        raise ValueError('final answer identity unavailable')
    return 'final:' + item_id


def key(source_id):
    if source_id.startswith('recovered-final:'):
        source_id = 'final:' + source_id[len('recovered-final:'):]
    return hashlib.sha256(source_id.encode()).hexdigest()


def mark(db, tid, source_id, phase):
    """Caller owns the turn fence. Mark complete only after all bytes commit."""
    digest = key(source_id)
    sid = 'answer:' + phase + ':' + digest
    if db.scalar(select(events.c.id).where(events.c.turn_id == tid, events.c.source_id == sid)):
        return
    seq = (db.scalar(select(func.max(events.c.sequence)).where(events.c.turn_id == tid)) or 0) + 1
    db.execute(insert(events).values(**service.identity(), turn_id=tid, sequence=seq,
        source_id=sid, event_type='execution.state', payload=json.dumps({'answer_source': digest})))


def selection(db, tid):
    """Return (source hash or None, complete). None preserves ambiguous legacy data."""
    complete = db.scalar(select(events.c.source_id).where(events.c.turn_id == tid,
        events.c.source_id.startswith('answer:complete:')).order_by(events.c.sequence.desc()).limit(1))
    if complete:
        return complete.split(':', 2)[2], True
    started = db.scalar(select(events.c.id).where(events.c.turn_id == tid,
        events.c.source_id.startswith('answer:begin:')).limit(1))
    if started:
        # Retain committed partial data, but do not call it a complete final.
        return None, False
    rows = db.execute(select(segments.c.source_event_id, segments.c.source_offset,
        objects.c.sha256, objects.c.byte_count).join(objects, objects.c.id == segments.c.object_id)
        .where(segments.c.turn_id == tid, segments.c.stream_id == 'final')
        .order_by(segments.c.sequence).limit(257)).all()
    if not rows:
        return None, False
    # Old writers have no explicit completion checkpoint. Do not guess on large
    # or ambiguous histories. A recovery plus equal whole source groups is proof
    # of a duplicate candidate, never a reason to remove repeating paragraphs.
    if len(rows) > 256:
        return None, False
    groups = {}
    for r in rows:
        groups.setdefault(r.source_event_id, []).append((r.source_offset, r.sha256, r.byte_count))
    if len(groups) == 1:
        return None, True  # legacy compatibility; no new writer checkpoint
    recovered = db.scalar(select(events.c.id).where(events.c.turn_id == tid,
        events.c.source_id == 'reconcile:terminal').limit(1))
    values = list(groups.values())
    contiguous = all(all(offset == sum(x[2] for x in group[:i])
                         for i, (offset, _, _) in enumerate(group)) for group in values)
    if recovered and contiguous and all(group == values[0] for group in values[1:]):
        return next(iter(groups)), True
    return None, False

