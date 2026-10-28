"""Bounded assistant projection; callers authorize reads or hold a fenced turn lock."""
from __future__ import annotations

import base64
import binascii
import re
from datetime import datetime
import hashlib
import json
from sqlalchemy import and_, or_, case, exists, func, insert, literal, select, union_all, update
from app.chat import service
from app.chat.schema import events, messages, turns

MAX_EVENTS = 1000
MAX_CHARS = 200_000


def message_id(tid):
    return 'assistant-' + hashlib.sha256(tid.encode()).hexdigest()[:48]


def saved_output(db, tid):
    # V2 previews read authoritative committed content, not truncated event text.
    from app.chat.content_schema import segments
    from app.chat import content_store
    from app.chat.final_answer import selection
    selected, final_complete = selection(db, tid)
    final_exists = db.scalar(select(segments.c.id).where(segments.c.turn_id == tid,
        segments.c.stream_id == 'final').limit(1))
    stream = 'final' if final_exists else 'output'
    from app.chat.output_window import read_batch, BATCH_SEGMENTS, PREVIEW_SEGMENTS, PREVIEW_BYTES
    preview = []; size_v2 = 0; read_bytes = 0; count = 0; after = 0; reason = None
    while count < PREVIEW_SEGMENTS:
        try:
            batch, more, consumed = read_batch(db, tid, stream, after,
                selected if stream == 'final' else None,
                limit=min(BATCH_SEGMENTS, PREVIEW_SEGMENTS - count),
                byte_budget=PREVIEW_BYTES - read_bytes)
        except (ValueError, UnicodeError):
            reason = 'invalid_payload'
            break
        read_bytes += consumed
        for index, item in enumerate(batch):
            text_v2 = item['text']; remaining = MAX_CHARS - size_v2
            preview.append(text_v2[:remaining]); size_v2 += min(len(text_v2), remaining)
            count += 1; after = item['sequence']
            if len(text_v2) > remaining or (size_v2 == MAX_CHARS and (index + 1 < len(batch) or more)):
                reason = 'preview_limit'
                break
        if reason or not more:
            break
        if not batch or read_bytes == PREVIEW_BYTES or count == PREVIEW_SEGMENTS:
            reason = 'read_window'
            break
    if preview or reason:
        result = {'content': ''.join(preview), 'partial': not final_complete or bool(reason),
                  'truncated': bool(reason)}
        if reason: result['truncation_reason'] = reason
        return result
    # Read sequence metadata for all event types to detect retained-history gaps,
    # but never load tool payloads into the assistant projection.
    relevant = (events.c.event_type == 'execution.output') | events.c.source_id.startswith('assistant:final:')
    rows = db.execute(select(events.c.sequence, events.c.event_type, events.c.source_id,
        case((relevant, events.c.payload), else_='').label('payload'))
        .where(events.c.turn_id == tid).order_by(events.c.sequence).limit(MAX_EVENTS + 1)).mappings()
    parts = {}; final = None; size = 0; previous = 0; truncated = False; reason = None
    for index, row in enumerate(rows):
        if index == MAX_EVENTS:
            truncated = True; reason = reason or 'read_window'; break
        if row['sequence'] != previous + 1: truncated = True; reason = 'history_gap'
        previous = row['sequence']
        if not row['payload']: continue
        try: payload = json.loads(row['payload'])
        except (ValueError, TypeError): truncated = True; reason = 'invalid_payload'; continue
        if not isinstance(payload, dict): truncated = True; reason = 'invalid_payload'; continue
        text = payload.get('text')
        if not isinstance(text, str): continue
        if row['source_id'].startswith('assistant:final:'):
            final = text[:MAX_CHARS]
            truncated |= len(text) > MAX_CHARS
            continue
        key = payload.get('item_id')
        key = key if isinstance(key, str) else 'legacy'
        available = max(0, MAX_CHARS - size)
        parts[key] = parts.get(key, '') + text[:available]
        size += min(len(text), available)
        truncated |= len(text) > available
    joined = '\n\n'.join(parts.values())
    if final is None and len(joined) > MAX_CHARS: truncated = True
    content = final if final is not None else joined[:MAX_CHARS]
    result = {'content': content, 'partial': final is None or truncated, 'truncated': truncated}
    if truncated: result['truncation_reason'] = reason or 'preview_limit'
    return result


def persist_output(db, tid, content=None):
    """No commit: same transaction/turn lock as normal completion or recovery."""
    existing = db.execute(select(messages.c.id).where(messages.c.turn_id == tid,
        messages.c.role == 'assistant').order_by(messages.c.created_at, messages.c.id).limit(1)).first()
    if content is None:
        projection = saved_output(db, tid)
        if existing and projection['truncated']:
            return
        content = projection['content']
    if not content: return
    if existing:
        # Preserve existing authoritative/legacy messages. Only our projection can
        # be upgraded by the normal completion path.
        if existing.id == message_id(tid):
            db.execute(update(messages).where(messages.c.id == existing.id).values(content=content, updated_at=service.now()))
        return
    stamp = service.now()
    db.execute(insert(messages).values(id=message_id(tid), created_at=stamp,
        updated_at=service.now(), turn_id=tid, role='assistant', content=content))


def encode_cursor(cid, key):
    payload = [1, cid, key['turn_created_at'], key['turn_id'], key['role_rank'], key['message_id']]
    return base64.urlsafe_b64encode(json.dumps(payload, separators=(',', ':')).encode()).decode().rstrip('=')


def decode_cursor(value, cid):
    try:
        if not value or len(value) > 1024 or not re.fullmatch(r'[A-Za-z0-9_-]+', value):
            raise ValueError()
        data = json.loads(base64.b64decode(value + '=' * (-len(value) % 4), altchars=b'-_', validate=True))
        if not isinstance(data, list) or len(data) != 6 or type(data[0]) is not int or data[0] != 1 or data[1] != cid:
            raise ValueError()
        if not isinstance(data[2], str) or len(data[2]) > 32 or datetime.fromisoformat(data[2].replace('Z', '+00:00')).utcoffset() is None:
            raise ValueError()
        if type(data[4]) is not int or data[4] not in (0, 1, 2):
            raise ValueError()
        if any(not isinstance(data[i], str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', data[i]) for i in (3, 5)):
            raise ValueError()
        return data[2:]
    except (ValueError, TypeError, UnicodeError, binascii.Error):
        raise service.ChatError(2504, '消息分页游标无效，请重新加载会话', 422) from None


def message_page(db, cid, page, page_size, before=None, *, with_cursor=False):
    # All persisted timestamps use UTC. Normalize the legacy Z suffix before SQL
    # comparison; binary collation keeps identifiers identical to JS ordering.
    dialect = db.get_bind().dialect.name
    collation = 'utf8mb4_bin' if dialect == 'mysql' else 'BINARY'
    if dialect == 'sqlite':
        db.connection().connection.driver_connection.create_function(
            'sha2', 2, lambda value, bits: hashlib.sha256(value.encode()).hexdigest(), deterministic=True)
    stamp = func.replace(turns.c.created_at, 'Z', '+00:00')
    virtual_id = literal('assistant-') + func.substr(func.sha2(turns.c.id, 256), 1, 48)
    actual = select(messages.c.id, messages.c.turn_id, messages.c.role, messages.c.content,
        messages.c.created_at, stamp.label('turn_created_at'),
        case((messages.c.role == 'user', 0), (messages.c.role == 'assistant', 1), else_=2).label('role_rank'),
        turns.c.effective_config, turns.c.config_fallback_reason, turns.c.status.label('turn_status'),
        literal(False).label('projected')).join(turns, turns.c.id == messages.c.turn_id).where(turns.c.conversation_id == cid)
    has_message = exists(select(messages.c.id).where(messages.c.turn_id == turns.c.id, messages.c.role == 'assistant'))
    relevant = (events.c.event_type == 'execution.output') | events.c.source_id.startswith('assistant:final:')
    has_output = exists(select(events.c.id).where(events.c.turn_id == turns.c.id, relevant))
    virtual = select(virtual_id.label('id'), turns.c.id.label('turn_id'), literal('assistant').label('role'),
        literal('').label('content'), turns.c.created_at, stamp.label('turn_created_at'), literal(1).label('role_rank'),
        turns.c.effective_config, turns.c.config_fallback_reason, turns.c.status.label('turn_status'),
        literal(True).label('projected')).where(turns.c.conversation_id == cid, ~has_message, has_output)
    combined = union_all(actual, virtual).subquery()
    keys = [combined.c.turn_created_at.collate(collation), combined.c.turn_id.collate(collation),
            combined.c.role_rank, combined.c.id.collate(collation)]
    query = select(combined)
    if before is not None:
        boundary = decode_cursor(before, cid)
        query = query.where(or_(*(and_(*(keys[j] == boundary[j] for j in range(i)), keys[i] < boundary[i]) for i in range(4))))
    else:
        query = query.offset((page - 1) * page_size)
    rows = list(db.execute(query.order_by(*(key.desc() for key in keys)).limit(page_size + 1)).mappings())
    has_more = len(rows) > page_size
    # One batched event-time lookup per page; do not add per-message time queries.
    tids = list({row['turn_id'] for row in rows[:page_size] if row['role'] == 'assistant'})
    first_sequences = select(events.c.turn_id, func.min(events.c.sequence).label('sequence')).where(
        events.c.turn_id.in_(tids), relevant).group_by(events.c.turn_id).subquery()
    event_times = dict(db.execute(select(events.c.turn_id, events.c.created_at).join(first_sequences,
        and_(events.c.turn_id == first_sequences.c.turn_id, events.c.sequence == first_sequences.c.sequence))).all()) if tids else {}
    result = []
    for value in rows[:page_size]:
        row = dict(value); projected = row.pop('projected'); status = row.pop('turn_status')
        row['order_key'] = {'turn_created_at': row.pop('turn_created_at'), 'turn_id': row['turn_id'],
                            'role_rank': row.pop('role_rank'), 'message_id': row['id']}
        row['display_time'] = row['created_at']; row['time_source'] = 'message_saved'
        if row['role'] == 'assistant':
            # Output event time is an observation, not the model's start time.
            event_time = event_times.get(row['turn_id'])
            if event_time:
                row['display_time'] = event_time; row['time_source'] = 'output_event'
            elif projected or row['created_at'].replace('Z', '+00:00') == row['order_key']['turn_created_at']:
                row['display_time'] = None; row['time_source'] = 'legacy_unknown'
            if projected or row['id'] == message_id(row['turn_id']):
                output = saved_output(db, row['turn_id'])
                from app.chat.final_answer import selection
                selected, complete = selection(db, row['turn_id'])
                if projected or (selected and complete and output['content'] and not output['truncated']):
                    row['content'] = output['content']
                row.update(output_partial=output['partial'] or status != 'completed', output_truncated=output['truncated'], output_truncation_reason=output.get('truncation_reason'),
                    output_source='events' if projected else 'message')
            else:
                row.update(output_partial=status != 'completed', output_truncated=False, output_source='message')
        result.append(row)
    if with_cursor:
        return {'items': result, 'has_more': has_more,
                'next_cursor': encode_cursor(cid, result[-1]['order_key']) if has_more and result else None}
    return result
