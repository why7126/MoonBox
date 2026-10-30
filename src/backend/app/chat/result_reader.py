"""Authorized bounded v2 readers; opaque cursors bind to the requested resource."""
import base64
import binascii
import json
from sqlalchemy import func, select
from app.chat import service, content_store
from app.chat.content_schema import entries, objects, segments
from app.chat.schema import diffs, events


def encode(tid, stream, position):
    return base64.urlsafe_b64encode(json.dumps([2,tid,stream,position]).encode()).decode().rstrip('=')


def decode(cursor, tid, stream, default):
    if cursor is None: return default
    try:
        if len(cursor) > 1024: raise ValueError()
        value = json.loads(base64.b64decode(cursor+'='*(-len(cursor)%4),altchars=b'-_',validate=True))
        if not isinstance(value,list) or len(value)!=4 or value[:3] != [2,tid,stream]: raise ValueError()
        return value[3]
    except (ValueError, TypeError, UnicodeError, binascii.Error):
        raise service.ChatError(2504,'读取游标无效，请重新加载',422) from None


def results(db, actor, tid, stream='output', cursor=None):
    turn = service.turn(db, actor, tid)
    from app.chat.final_answer import selection
    selected, final_complete = selection(db, tid)
    cursor_stream = stream + ':' + selected if stream == 'final' and selected else stream
    after = decode(cursor,tid,cursor_stream,0)
    if type(after) is not int or after < 0 or stream not in ('output','final'):
        raise service.ChatError(2504,'读取参数无效',422)
    from app.chat.output_window import read_batch
    try:
        items, _, _ = read_batch(db, tid, stream, after, selected if stream == 'final' else None)
    except (ValueError, UnicodeError):
        raise service.ChatError(2504, '部分历史输出不可用', 409) from None
    last = items[-1]['sequence'] if items else after
    maximum = db.scalar(select(func.max(segments.c.sequence)).where(segments.c.turn_id==tid,segments.c.stream_id==stream,
        *([segments.c.source_event_id == selected] if stream == 'final' and selected else []))) or 0
    if not items and not maximum and db.scalar(select(events.c.id).where(
        events.c.turn_id == tid, events.c.event_type == 'execution.output').limit(1)) is not None:
        raise service.ChatError(2504, '此历史轮次未保存可分页正文，请查看本轮轨迹', 409)
    has_final = db.scalar(select(segments.c.id).where(segments.c.turn_id==tid,segments.c.stream_id=='final').limit(1)) is not None
    submitted = bool(turn['executor_turn_id']) or db.scalar(select(events.c.id).where(
        events.c.turn_id==tid, events.c.source_id=='runner:start-requested').limit(1)) is not None
    complete = turn['status']=='completed' and final_complete
    return {'items':items,'next_cursor':encode(tid,cursor_stream,last) if last<maximum else None,
        'resume_cursor':encode(tid,cursor_stream,last),'committed_sequence':maximum,'has_final':has_final,
        'completeness':'complete' if complete else 'unknown_tail', 'format_version':2,
        'storage_status': {'stage':turn['status'], 'code':turn['error_code'],
            'execution_started': 'confirmed' if turn['executor_turn_id'] else 'unknown' if submitted else 'not_confirmed',
            'saved_through':maximum, 'completeness':'complete' if complete else 'unknown_tail',
            'recovery_action':'check' if turn['status'] in ('failed','unknown') else 'read',
            'request_id':turn.get('request_id')}}


def files(db,actor,tid,cursor=None,scope='turn'):
    service.turn(db,actor,tid)
    raw=db.scalar(select(diffs.c.payload).where(diffs.c.turn_id==tid))
    if not raw: return {'files':[],'next_cursor':None,'available':False}
    data=json.loads(raw)
    if not isinstance(data,dict) or data.get('format_version') != 2:
        return {'files':data.get('files',[]) if isinstance(data,dict) else data,'next_cursor':None,'format_version':1,'available':True}
    if scope not in ('turn', 'cumulative'): raise service.ChatError(2504,'比较范围无效',422)
    after=decode(cursor,tid,'files:'+scope,'')
    if not isinstance(after,str) or len(after)>64: raise service.ChatError(2504,'读取游标无效',422)
    from app.chat.snapshot_store import diff_page
    value=diff_page(db,data['initial_version'] if scope == 'cumulative' else data['before_version'],data['after_version'],after)
    if value['next_cursor']: value['next_cursor']=encode(tid,'files:'+scope,value['next_cursor'])
    return {**value,'format_version':2,'available':True}


def content(db,actor,tid,file_id,side,cursor=None,scope='turn'):
    turn=service.turn(db,actor,tid)
    raw=db.scalar(select(diffs.c.payload).where(diffs.c.turn_id==tid))
    data=json.loads(raw) if raw else {}
    if not isinstance(data,dict) or data.get('format_version') != 2:
        raise service.ChatError(2504,'历史全文不可用',404)
    if side not in ('before','after'): raise service.ChatError(2504,'读取侧无效',422)
    if scope not in ('turn','cumulative'): raise service.ChatError(2504,'比较范围无效',422)
    version = data['initial_version'] if side == 'before' and scope == 'cumulative' else data[side+'_version']
    from app.chat.content_schema import versions
    manifest = db.execute(select(versions).where(versions.c.id == version,
        versions.c.conversation_id == turn['conversation_id'])).mappings().first()
    if not manifest:
        raise service.ChatError(2504, '内容不可用', 404)
    if manifest['status'] == 'expired':
        raise service.ChatError(2507, '文件版本已轮转，对话记录仍保留', 410)
    item=db.execute(select(entries).where(entries.c.version_id==version,entries.c.path_key==file_id)).mappings().first()
    if not item or not item['object_id']:
        return {'status':'legacy_unavailable' if item and item['kind']=='file' else 'metadata_only','text':None,'next_cursor':None}
    oid=item['object_id']
    from app.chat.schema import conversations
    parent = db.execute(select(conversations.c.space_id, conversations.c.repository_id).where(
        conversations.c.id == turn['conversation_id'])).one()
    # Authority follows this live manifest reference, never an object's first owner.
    valid = db.scalar(select(objects.c.id).join(conversations, conversations.c.id == objects.c.conversation_id).where(
        objects.c.id == oid, objects.c.status == 'complete', conversations.c.space_id == parent.space_id,
        conversations.c.repository_id == parent.repository_id))
    if not valid: raise service.ChatError(2504,'内容不可用',404)
    # Reconstruct UTF-8 carry from trusted stored bytes, never from the cursor.
    cursor_stream=scope+':'+side+':'+file_id
    position=decode(cursor,tid,cursor_stream,-1)
    if type(position) is not int or position < -1:
        raise service.ChatError(2504,'读取游标无效',422)
    carry=b''
    if position >= 0:
        previous, _ = content_store.read_page(db,oid,position-1)
        suffix=previous[-4:]
        start=len(suffix)-1
        while start>=0 and suffix[start]&0xc0==0x80: start-=1
        if start>=0:
            candidate=suffix[start:]
            lead=candidate[0]
            expected=1 if lead<0x80 else 2 if 0xc2<=lead<=0xdf else 3 if 0xe0<=lead<=0xef else 4 if 0xf0<=lead<=0xf4 else 0
            if expected>len(candidate): carry=candidate
    payload,next_chunk=content_store.read_page(db,oid,position)
    import codecs
    try:
        decoder=codecs.getincrementaldecoder('utf-8')(); text=decoder.decode(carry+payload,final=next_chunk is None)
        if '\0' in text: raise UnicodeError()
    except UnicodeError:
        return {'status':'binary','text':None,'next_cursor':None,'byte_count':item['byte_count']}
    return {'status':'available','text':text,'byte_count':item['byte_count'],
        'next_cursor':encode(tid,cursor_stream,next_chunk) if next_chunk is not None else None}
