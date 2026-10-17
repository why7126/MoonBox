"""Bounded assistant projection; callers authorize reads or hold a fenced turn lock."""
from __future__ import annotations

import hashlib
import json
from sqlalchemy import case, exists, insert, literal, select, union_all, update
from app.chat import service
from app.chat.schema import events, messages, turns

MAX_EVENTS = 1000
MAX_CHARS = 200_000


def message_id(tid):
    return 'assistant-' + hashlib.sha256(tid.encode()).hexdigest()[:48]


def saved_output(db, tid):
    # Read sequence metadata for all event types to detect retained-history gaps,
    # but never load tool payloads into the assistant projection.
    relevant = (events.c.event_type == 'execution.output') | events.c.source_id.startswith('assistant:final:')
    rows = db.execute(select(events.c.sequence, events.c.event_type, events.c.source_id,
        case((relevant, events.c.payload), else_='').label('payload'))
        .where(events.c.turn_id == tid).order_by(events.c.sequence).limit(MAX_EVENTS + 1)).mappings()
    parts = {}; final = None; size = 0; previous = 0; truncated = False
    for index, row in enumerate(rows):
        if index == MAX_EVENTS:
            truncated = True; break
        if row['sequence'] != previous + 1: truncated = True
        previous = row['sequence']
        if not row['payload']: continue
        try: payload = json.loads(row['payload'])
        except (ValueError, TypeError): truncated = True; continue
        if not isinstance(payload, dict): truncated = True; continue
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
    return {'content': content, 'partial': final is None or truncated, 'truncated': truncated}


def persist_output(db, tid, content=None):
    """No commit: same transaction/turn lock as normal completion or recovery."""
    existing = db.execute(select(messages.c.id).where(messages.c.turn_id == tid,
        messages.c.role == 'assistant').order_by(messages.c.created_at, messages.c.id).limit(1)).first()
    if content is None: content = saved_output(db, tid)['content']
    if not content: return
    if existing:
        # Preserve existing authoritative/legacy messages. Only our projection can
        # be upgraded by the normal completion path.
        if existing.id == message_id(tid):
            db.execute(update(messages).where(messages.c.id == existing.id).values(content=content, updated_at=service.now()))
        return
    stamp = db.scalar(select(turns.c.created_at).where(turns.c.id == tid))
    db.execute(insert(messages).values(id=message_id(tid), created_at=stamp,
        updated_at=service.now(), turn_id=tid, role='assistant', content=content))


def message_page(db, cid, page, page_size):
    # Virtual rows participate in SQL pagination, rather than being appended to
    # every page. Their identity and ordering survive later materialization.
    actual = select(messages.c.id, messages.c.turn_id, messages.c.role, messages.c.content,
        case((messages.c.role == 'assistant', turns.c.created_at), else_=messages.c.created_at).label('created_at'),
        turns.c.effective_config, turns.c.config_fallback_reason, turns.c.status.label('turn_status'), literal(False).label('projected'))        .join(turns, turns.c.id == messages.c.turn_id).where(turns.c.conversation_id == cid)
    has_message = exists(select(messages.c.id).where(messages.c.turn_id == turns.c.id, messages.c.role == 'assistant'))
    has_output = exists(select(events.c.id).where(events.c.turn_id == turns.c.id, (events.c.event_type == 'execution.output') | events.c.source_id.startswith('assistant:final:')))
    virtual = select(literal('').label('id'), turns.c.id.label('turn_id'), literal('assistant').label('role'),
        literal('').label('content'), turns.c.created_at, turns.c.effective_config, turns.c.config_fallback_reason, turns.c.status.label('turn_status'),
        literal(True).label('projected')).where(turns.c.conversation_id == cid, ~has_message, has_output)
    combined = union_all(actual, virtual).subquery()
    rows = db.execute(select(combined).order_by(combined.c.created_at.desc(), combined.c.turn_id.desc(),
        combined.c.role.asc(), combined.c.id.desc()).limit(page_size).offset((page-1)*page_size)).mappings()
    result = []
    for value in rows:
        row = dict(value); projected = row.pop('projected'); status = row.pop('turn_status')
        if row['role'] == 'assistant':
            if projected or row['id'] == message_id(row['turn_id']):
                output = saved_output(db, row['turn_id'])
                if projected:
                    row['id'] = message_id(row['turn_id']); row['content'] = output['content']
                row.update(output_partial=output['partial'] or status != 'completed', output_truncated=output['truncated'],
                    output_source='events' if projected else 'message')
            else:
                row.update(output_partial=status != 'completed', output_truncated=False, output_source='message')
        result.append(row)
    return result
