"""Bounded, integrity-checked reads of committed result segments.

Metadata lookahead never loads extra text. Callers authorize the turn or hold
its fence; this module never mutates data or chooses an answer version.
"""
import hashlib
from sqlalchemy import select
from app.chat.content_schema import segments, objects, chunks

BATCH_SEGMENTS = 512
PREVIEW_SEGMENTS = 4096
PREVIEW_BYTES = 1024 * 1024
PAGE_BYTES = 256 * 1024


def read_batch(db, tid, stream, after=0, selected=None, *, limit=BATCH_SEGMENTS, byte_budget=PAGE_BYTES):
    rows = db.execute(select(segments.c.sequence, segments.c.object_id,
        objects.c.byte_count, objects.c.sha256, objects.c.status)
        .outerjoin(objects, objects.c.id == segments.c.object_id)
        .where(segments.c.turn_id == tid, segments.c.stream_id == stream,
            segments.c.sequence > after,
            *([segments.c.source_event_id == selected] if selected else []))
        .order_by(segments.c.sequence).limit(limit + 1)).mappings().all()
    chosen = []; size = 0
    for row in rows[:limit]:
        if row['status'] != 'complete' or not 0 < row['byte_count'] <= PAGE_BYTES:
            raise ValueError('invalid result object')
        if size + row['byte_count'] > byte_budget:
            break
        chosen.append(row); size += row['byte_count']
    if not chosen:
        return [], bool(rows), 0
    ids = {r['object_id'] for r in chosen}
    # Result objects are bounded single-chunk writes. Query no unneeded chunks.
    stored = {r.object_id: r for r in db.execute(select(chunks.c.object_id,
        chunks.c.payload, chunks.c.byte_count, chunks.c.sha256)
        .where(chunks.c.object_id.in_(ids), chunks.c.chunk_no == 0))}
    result = []
    for row in chosen:
        chunk = stored.get(row['object_id'])
        if chunk is None:
            raise ValueError('missing result chunk')
        data = bytes(chunk.payload)
        digest = hashlib.sha256(data).hexdigest()
        if len(data) != row['byte_count'] or len(data) != chunk.byte_count or digest != chunk.sha256 or digest != row['sha256']:
            raise ValueError('result integrity failure')
        result.append({'sequence': row['sequence'], 'text': data.decode('utf-8'), 'byte_count': len(data)})
    return result, len(rows) > len(chosen), size
