"""Exact bounded block comparison over persisted chunk indexes, not a line heuristic."""
import json
from sqlalchemy import select
from app.chat import service
from app.chat.content_schema import chunks, entries
from app.chat.schema import diffs
from app.chat.result_reader import decode, encode


def read(db, actor, tid, file_id, before_file_id=None, scope='turn', cursor=None):
    service.turn(db, actor, tid)
    raw = db.scalar(select(diffs.c.payload).where(diffs.c.turn_id == tid))
    data = json.loads(raw) if raw else {}
    if not isinstance(data,dict) or data.get('format_version') != 2:
        return {'status':'legacy_unavailable','items':[],'next_cursor':None}
    before_version = data['initial_version'] if scope == 'cumulative' else data['before_version']
    def entry(version, key):
        return db.execute(select(entries).where(entries.c.version_id==version,entries.c.path_key==key)).mappings().first()
    a=entry(before_version,before_file_id or file_id); b=entry(data['after_version'],file_id)
    if any(item and item['kind']=='file' and not item['object_id'] for item in (a,b)):
        return {'status':'legacy_unavailable','items':[],'next_cursor':None}
    stream=f'blocks:{scope}:{file_id}:{before_file_id or file_id}'
    position=decode(cursor,tid,stream,-1)
    if type(position) is not int or position < -1: raise service.ChatError(2504,'读取游标无效',422)
    def batch(item):
        if not item or not item['object_id']: return {}
        return {r.chunk_no:r for r in db.execute(select(chunks.c.chunk_no,chunks.c.sha256,chunks.c.byte_count)
            .where(chunks.c.object_id==item['object_id'],chunks.c.chunk_no>position)
            .order_by(chunks.c.chunk_no).limit(101))}
    left,right=batch(a),batch(b); numbers=sorted(set(left)|set(right)); window=numbers[:100]
    items=[]
    for number in window:
        old,new=left.get(number),right.get(number)
        if old and new and old.sha256==new.sha256 and old.byte_count==new.byte_count: continue
        items.append({'block':number,'before_bytes':old.byte_count if old else 0,'after_bytes':new.byte_count if new else 0,
            'before_sha256':old.sha256 if old else None,'after_sha256':new.sha256 if new else None})
    return {'status':'compared','items':items,'next_cursor':encode(tid,stream,window[-1]) if len(numbers)>100 else None}
