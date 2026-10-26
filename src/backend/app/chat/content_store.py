"""Bounded transactional content primitives. Callers retain auth and turn fences.

No helper commits: a caller publishes objects, references and ledger atomically.
Byte counts describe stored content, never physical database/WAL allocation.
"""
from __future__ import annotations

import hashlib
from sqlalchemy import delete, func, insert, select, update
from app.chat import service
from app.chat.content_schema import chunks, objects, segments, ledger

CHUNK_BYTES = 256 * 1024


def charge_metadata(db, cid, key, size):
    """Upsert one stored row's byte ledger in the same publication transaction."""
    from app.chat.schema import conversations, usage_accounts
    from app.chat.settings import execution_limits
    from app.chat.admission import _account
    parent = db.execute(select(conversations).where(conversations.c.id == cid).with_for_update()).mappings().one()
    if parent['deleted_at']: raise service.ChatError(2504, '内容已不可用', 404)
    existing = db.scalar(select(ledger.c.delta_bytes).where(ledger.c.event_id == key).with_for_update())
    delta = size - (existing or 0)
    limits = execution_limits()
    if limits is None: raise service.ChatError(2505, '执行资源配置无效', 503)
    for kind, identifier in (('space', parent['space_id']), ('user', parent['owner_id'])):
        account = f'{kind}:{identifier}'; _account(db, account)
        conditions = [usage_accounts.c.id == account]
        cap = limits[f'{kind}_storage_bytes']
        if cap is not None and delta > 0:
            conditions.append(usage_accounts.c.used_bytes + usage_accounts.c.reserved_bytes + delta <= cap)
        if db.execute(update(usage_accounts).where(*conditions).values(used_bytes=usage_accounts.c.used_bytes+delta)).rowcount != 1:
            raise service.ChatError(2508, '运营存储额度不足，已保存内容保留')
    if existing is None:
        db.execute(insert(ledger).values(event_id=key, object_id=key, conversation_id=cid,
            delta_bytes=size, created_at=service.now()))
    else: db.execute(update(ledger).where(ledger.c.event_id == key).values(delta_bytes=size))


def begin(db, cid, kind):
    from app.chat.resource_guard import lock_budget
    lock_budget(db)
    row = service.identity()
    db.execute(insert(objects).values(**row, conversation_id=cid, kind=kind, status='building'))
    return row['id']


def append(db, oid, number, payload):
    from app.chat.resource_guard import require_database_disk
    require_database_disk(db)
    if not isinstance(payload, bytes) or not 0 < len(payload) <= CHUNK_BYTES:
        raise ValueError('invalid content chunk')
    state = db.scalar(select(objects.c.status).where(objects.c.id == oid).with_for_update())
    if state != 'building':
        raise ValueError('content object is not writable')
    digest = hashlib.sha256(payload).hexdigest()
    old = db.execute(select(chunks.c.sha256, chunks.c.byte_count).where(
        chunks.c.object_id == oid, chunks.c.chunk_no == number)).first()
    if old:
        if (old.sha256, old.byte_count) != (digest, len(payload)):
            raise ValueError('content chunk conflicts with checkpoint')
        return
    last = db.scalar(select(func.max(chunks.c.chunk_no)).where(chunks.c.object_id == oid))
    expected = 0 if last is None else last + 1
    if number != expected:
        raise ValueError('content chunk sequence gap')
    db.execute(insert(chunks).values(object_id=oid, chunk_no=number, payload=payload,
                                   byte_count=len(payload), sha256=digest))


def blocks(db, oid):
    number = 0
    while True:
        row = db.execute(select(chunks).where(chunks.c.object_id == oid,
            chunks.c.chunk_no == number)).mappings().first()
        if row is None:
            return
        payload = bytes(row['payload'])
        if len(payload) != row['byte_count'] or hashlib.sha256(payload).hexdigest() != row['sha256']:
            raise ValueError('content integrity failure')
        yield payload
        number += 1


def finish(db, oid):
    row = db.execute(select(objects).where(objects.c.id == oid).with_for_update()).mappings().one()
    if row['status'] == 'complete':
        return oid
    if row['status'] != 'building':
        raise ValueError('content object cannot be published')
    digest = hashlib.sha256(); size = 0
    for block in blocks(db, oid):
        digest.update(block); size += len(block)
    value = digest.hexdigest()
    # Serialize publication per conversation, including empty objects.
    from app.chat.schema import conversations
    db.execute(update(conversations).where(conversations.c.id == row['conversation_id'])
               .values(updated_at=conversations.c.updated_at))
    existing = db.scalar(select(objects.c.id).where(objects.c.conversation_id == row['conversation_id'],
        objects.c.sha256 == value, objects.c.byte_count == size, objects.c.status == 'complete').limit(1))
    if existing:
        db.execute(delete(chunks).where(chunks.c.object_id == oid))
        db.execute(delete(objects).where(objects.c.id == oid))
        return existing
    from app.chat.settings import execution_limits
    from app.chat.schema import usage_accounts
    from app.chat.admission import _account
    limits = execution_limits()
    if limits is None:
        raise service.ChatError(2505, '执行资源配置无效', 503)
    parent = db.execute(select(conversations).where(conversations.c.id == row['conversation_id'])).mappings().one()
    if parent['deleted_at']:
        raise service.ChatError(2504, '内容已不可用', 404)
    for kind, identifier in (('space', parent['space_id']), ('user', parent['owner_id'])):
        key = f'{kind}:{identifier}'; _account(db, key)
        conditions = [usage_accounts.c.id == key]
        cap = limits[f'{kind}_storage_bytes']
        if cap is not None:
            conditions.append(usage_accounts.c.used_bytes + usage_accounts.c.reserved_bytes + size <= cap)
        if db.execute(update(usage_accounts).where(*conditions).values(
            used_bytes=usage_accounts.c.used_bytes + size)).rowcount != 1:
            raise service.ChatError(2508, '运营存储额度不足，已保存内容保留')
    db.execute(update(objects).where(objects.c.id == oid).values(status='complete', sha256=value,
        byte_count=size, updated_at=service.now()))
    db.execute(insert(ledger).values(event_id=oid, conversation_id=row['conversation_id'],
        object_id=oid, delta_bytes=size, created_at=service.now()))
    return oid


def put(db, cid, kind, source):
    """Accept a bounded-block iterator; never concatenate all content."""
    oid = begin(db, cid, kind)
    for number, payload in enumerate(source):
        append(db, oid, number, payload)
    return finish(db, oid)


def result(db, cid, tid, stream, source_id, offset, payload):
    """Turn fence is held by the caller; publication and sequence share its txn."""
    if stream not in ('output', 'final') or offset < 0:
        raise ValueError('invalid result segment')
    source_key = hashlib.sha256(source_id.encode()).hexdigest()
    old = db.execute(select(segments).where(segments.c.turn_id == tid,
        segments.c.stream_id == stream, segments.c.source_event_id == source_key,
        segments.c.source_offset == offset)).mappings().first()
    if old:
        digest = db.scalar(select(objects.c.sha256).where(objects.c.id == old['object_id']))
        if digest != hashlib.sha256(payload).hexdigest():
            raise ValueError('result replay conflict')
        return old['sequence']
    previous = db.execute(select(segments.c.source_offset, objects.c.byte_count)
        .join(objects, objects.c.id == segments.c.object_id).where(segments.c.turn_id == tid,
        segments.c.stream_id == stream, segments.c.source_event_id == source_key)
        .order_by(segments.c.source_offset.desc()).limit(1)).first()
    expected = previous.source_offset + previous.byte_count if previous else 0
    if offset != expected:
        raise ValueError('result source sequence gap')
    oid = put(db, cid, 'result', [payload])
    sequence = (db.scalar(select(func.max(segments.c.sequence)).where(segments.c.turn_id == tid)) or 0) + 1
    db.execute(insert(segments).values(**service.identity(), turn_id=tid, stream_id=stream,
        source_event_id=source_key, source_offset=offset, sequence=sequence, object_id=oid))
    return sequence


def read_page(db, oid, after=-1, max_bytes=CHUNK_BYTES):
    if after < -1 or not 0 < max_bytes <= CHUNK_BYTES:
        raise ValueError('invalid content page')
    obj = db.execute(select(objects).where(objects.c.id == oid, objects.c.status == 'complete')).mappings().first()
    if obj is None:
        raise ValueError('content unavailable')
    row = db.execute(select(chunks).where(chunks.c.object_id == oid, chunks.c.chunk_no == after + 1)).mappings().first()
    if row is None:
        return b'', None
    payload = bytes(row['payload'])
    if hashlib.sha256(payload).hexdigest() != row['sha256']:
        raise ValueError('content integrity failure')
    if len(payload) > max_bytes:
        raise ValueError('page budget smaller than stored chunk')
    more = db.scalar(select(chunks.c.chunk_no).where(chunks.c.object_id == oid, chunks.c.chunk_no == after + 2))
    return payload, after + 1 if more is not None else None


def purge_conversation(db, cid):
    """Called only after deletion intent/permission checks, in the same transaction."""
    from app.chat.content_schema import entries, versions
    from app.chat.schema import turns
    from app.chat.content_schema import prepare_attempts
    total = db.scalar(select(func.coalesce(func.sum(ledger.c.delta_bytes), 0)).where(ledger.c.conversation_id == cid))
    total += db.scalar(select(func.coalesce(func.sum(prepare_attempts.c.prior_bytes), 0)).where(
        prepare_attempts.c.turn_id.in_(select(turns.c.id).where(turns.c.conversation_id == cid))))
    version_ids = select(versions.c.id).where(versions.c.conversation_id == cid)
    object_ids = select(objects.c.id).where(objects.c.conversation_id == cid)
    db.execute(delete(segments).where(segments.c.turn_id.in_(select(turns.c.id).where(turns.c.conversation_id == cid))))
    db.execute(delete(prepare_attempts).where(prepare_attempts.c.turn_id.in_(select(turns.c.id).where(turns.c.conversation_id == cid))))
    db.execute(delete(entries).where(entries.c.version_id.in_(version_ids)))
    db.execute(delete(versions).where(versions.c.conversation_id == cid))
    db.execute(delete(chunks).where(chunks.c.object_id.in_(object_ids)))
    db.execute(delete(ledger).where(ledger.c.conversation_id == cid))
    db.execute(delete(objects).where(objects.c.conversation_id == cid))
    return total


def collect_orphans(db, cid, limit=100):
    """One bounded maintenance batch; never races an active conversation writer."""
    from app.chat.schema import conversations, usage_accounts
    from app.chat.content_schema import entries, versions
    from sqlalchemy import exists
    if not 1 <= limit <= 100: raise ValueError('invalid maintenance window')
    parent = db.execute(select(conversations).where(conversations.c.id == cid).with_for_update()).mappings().first()
    if not parent or parent['active_turn_id']: return 0
    abandoned = select(versions.c.id).where(versions.c.conversation_id == cid,
        versions.c.status.in_(('building', 'abandoned')))
    stale = list(db.execute(select(entries.c.version_id, entries.c.path_key).where(
        entries.c.version_id.in_(abandoned)).limit(limit)))
    for vid, key in stale:
        db.execute(delete(entries).where(entries.c.version_id == vid, entries.c.path_key == key))
    candidates = list(db.execute(select(objects.c.id, objects.c.byte_count).where(
        objects.c.conversation_id == cid,
        ~exists(select(entries.c.object_id).where(entries.c.object_id == objects.c.id)),
        ~exists(select(segments.c.object_id).where(segments.c.object_id == objects.c.id))).limit(limit)))
    removed = 0; remaining_blocks = limit
    for oid, _ in candidates:
        charged = db.scalar(select(ledger.c.delta_bytes).where(ledger.c.object_id == oid)) or 0
        # Delete only a bounded number of blocks, even for a multi-gigabyte orphan.
        if remaining_blocks <= 0: break
        numbers = list(db.scalars(select(chunks.c.chunk_no).where(chunks.c.object_id == oid).limit(remaining_blocks)))
        remaining_blocks -= len(numbers)
        if numbers: db.execute(delete(chunks).where(chunks.c.object_id == oid, chunks.c.chunk_no.in_(numbers)))
        if db.scalar(select(chunks.c.chunk_no).where(chunks.c.object_id == oid).limit(1)) is not None: continue
        db.execute(delete(ledger).where(ledger.c.object_id == oid))
        db.execute(delete(objects).where(objects.c.id == oid))
        for kind, owner in (('space', parent['space_id']), ('user', parent['owner_id'])):
            db.execute(update(usage_accounts).where(usage_accounts.c.id == f'{kind}:{owner}').values(
                used_bytes=usage_accounts.c.used_bytes-charged))
        removed += 1
    return removed
