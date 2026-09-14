"""Space/repository-scoped governance references with immutable per-turn snapshots."""
import hashlib
import json
import os
import stat
from pathlib import Path
import re
import yaml
from sqlalchemy import delete, insert, select, update
from app.chat import service
from app.chat.schema import conversations, relations, object_access, snapshots, turns
from app.chat.settings import repository_binding
from app.chat.workspace import trusted_directory, WorkspaceError


def _root(repository_id, space_id):
    binding = repository_binding(repository_id, space_id)
    if not binding: raise service.ChatError(2509, '当前仓库尚未配置对象目录', 503)
    try: return trusted_directory(binding['governance_root'])
    except WorkspaceError: raise service.ChatError(2509, '对象目录不可用', 503)


def _read_file(root, relative):
    """Open every component relative to a pinned directory; never follow links."""
    if not isinstance(relative, str) or Path(relative).is_absolute() or '..' in Path(relative).parts:
        raise service.ChatError(2509, '对象不可访问', 403)
    handles = []
    try:
        handles.append(os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW))
        parts = Path(relative).parts
        if not parts: raise ValueError()
        for part in parts[:-1]:
            handles.append(os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=handles[-1]))
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=handles[-1])
        handles.append(fd)
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > 1024*1024: raise ValueError()
        chunks=[]; remaining=1024*1024+1
        while remaining:
            chunk=os.read(fd, min(65536, remaining))
            if not chunk: break
            chunks.append(chunk);remaining-=len(chunk)
        after=os.fstat(fd)
        if not remaining or (before.st_size,before.st_mtime_ns,before.st_ctime_ns) != (after.st_size,after.st_mtime_ns,after.st_ctime_ns): raise ValueError()
        return b''.join(chunks).decode('utf-8')
    except (OSError, ValueError, UnicodeError):
        raise service.ChatError(2509, '对象不可访问', 403)
    finally:
        for fd in reversed(handles): os.close(fd)


def _entries(root):
    result = []
    for folder in ('requirements', 'bugs'):
        try:
            content = _read_file(root, f'issues/{folder}/_registry.yaml')
            data = yaml.safe_load(content) or {}
            if not isinstance(data, dict) or not isinstance(data.get('entries', []), list): raise ValueError()
            for entry in data.get('entries', []):
                if isinstance(entry, dict) and re.fullmatch(r'(REQ|BUG)-\d{4}(?:-[A-Za-z0-9_-]+)?', str(entry.get('id',''))): result.append(entry)
        except service.ChatError: continue
        except (OSError, ValueError, yaml.YAMLError): raise service.ChatError(2509, '对象目录不可用', 503)
    return result


def resolve_object(db, actor, space_id, repository_id, object_id):
    service.authorize_space(db, actor, space_id)
    if not isinstance(object_id,str) or not re.fullmatch(r'(REQ|BUG)-\d{4}(?:-[A-Za-z0-9_-]+)?',object_id): raise service.ChatError(2509, '对象不存在或无权访问', 403)
    root = _root(repository_id, space_id)
    entries = [entry for entry in _entries(root) if entry['id'] == object_id or entry['id'].split('-',2)[:2] == object_id.split('-',2)]
    if len(entries) != 1: raise service.ChatError(2509, '对象不存在或无权访问', 403)
    entry = entries[0]; full_id = entry['id']
    grants = list(db.execute(select(object_access).where(object_access.c.space_id == space_id,
        object_access.c.repository_id == repository_id, object_access.c.object_id == full_id)).mappings())
    if grants and not any(row['user_id'] == actor and row['can_read'] for row in grants): raise service.ChatError(2509, '对象不存在或无权访问', 403)
    # An absent ACL inherits the already-checked repository/space membership; explicit ACL narrows it.
    base = entry.get('path', '')
    if not isinstance(base,str) or not base.startswith('issues/'): raise service.ChatError(2509, '对象不存在或无权访问', 403)
    document = 'requirement.md' if full_id.startswith('REQ-') else 'bug.md'
    try: content = _read_file(root, f'{base.rstrip("/")}/{document}')
    except service.ChatError: content = _read_file(root, f'{base.rstrip("/")}/capture.md')
    return {'id': full_id, 'title': str(entry.get('title') or full_id)[:200],
            'version': hashlib.sha256(content.encode()).hexdigest(), 'content': content,
            'status': str(entry.get('status') or ''), 'path': base, 'root': root}


def candidates(db, actor, parent, query=''):
    try: root = _root(parent['repository_id'], parent['space_id'])
    except service.ChatError as error: return {'items': [], 'reason': error.message}
    items = []
    for entry in _entries(root):
        if query.lower() not in (entry['id']+' '+str(entry.get('title',''))).lower(): continue
        try: item = resolve_object(db, actor, parent['space_id'], parent['repository_id'], entry['id'])
        except service.ChatError: continue
        items.append({key:item[key] for key in ('id','title','version')})
        if len(items) == 100: break
    return {'items':items,'reason':None}


def authorize_history(db, actor, parent):
    ids = set(db.scalars(select(snapshots.c.object_id).join(turns, turns.c.id == snapshots.c.turn_id)
        .where(turns.c.conversation_id == parent['id'])))
    for object_id in ids:
        try: resolve_object(db,actor,parent['space_id'],parent['repository_id'],object_id)
        except service.ChatError: raise service.ChatError(2509, '会话引用的对象已不可访问，请新建干净会话', 403)


def read_relations(db, actor, cid):
    parent = service.conversation(db, actor, cid)
    result = []
    for row in db.execute(select(relations).where(relations.c.conversation_id == cid)).mappings():
        item = resolve_object(db,actor,parent['space_id'],parent['repository_id'],row['object_id'])
        result.append({'id':item['id'],'title':item['title'],'role':row['role']})
    return {'primary':next((r for r in result if r['role']=='primary'),None),'references':[r for r in result if r['role']=='reference']}


def set_relations(db, actor, cid, primary, references):
    parent = service.conversation(db,actor,cid)
    if parent['archived'] or parent['active_turn_id']: raise service.ChatError(2504, '归档或活动运行期间不能调整关联')
    ids = ([primary] if primary else []) + references
    if len(ids) != len(set(ids)): raise service.ChatError(2504, '主对象和引用不能重复')
    resolved = [(resolve_object(db,actor,parent['space_id'],parent['repository_id'],oid), 'primary' if oid == primary else 'reference') for oid in ids]
    if len({item['id'] for item,_ in resolved}) != len(resolved): raise service.ChatError(2504, '对象不能重复')
    won=db.execute(update(conversations).where(conversations.c.id==cid,conversations.c.active_turn_id.is_(None),conversations.c.archived==0,conversations.c.deleted_at.is_(None)).values(updated_at=service.now())).rowcount
    if won != 1: db.rollback();raise service.ChatError(2504,'会话状态已变化')
    db.execute(delete(relations).where(relations.c.conversation_id==cid))
    for item,role in resolved:db.execute(insert(relations).values(conversation_id=cid,object_id=item['id'],title=item['title'],role=role))
    db.commit();return read_relations(db,actor,cid)


def capture_for_turn(db, actor, parent, turn_id, max_chars=12000):
    result=[]; remaining=48000
    for row in db.execute(select(relations).where(relations.c.conversation_id==parent['id']).order_by(relations.c.role,relations.c.object_id)).mappings():
        item=resolve_object(db,actor,parent['space_id'],parent['repository_id'],row['object_id'])
        excerpt=item['content'][:max_chars].encode('utf-8')[:remaining].decode('utf-8',errors='ignore')
        remaining-=len(excerpt.encode('utf-8'))
        payload={'title':item['title'],'content':excerpt,'truncated':excerpt!=item['content'],'role':row['role']}
        db.execute(insert(snapshots).values(**service.identity(),turn_id=turn_id,object_id=item['id'],version=item['version'],content=json.dumps(payload,ensure_ascii=False)))
        result.append({'object_id':item['id'],'version':item['version'],**payload})
    return result


def read_snapshots(db, actor, tid):
    service.turn(db,actor,tid)
    return [{'object_id':row['object_id'],'version':row['version'],**json.loads(row['content'])} for row in db.execute(select(snapshots).where(snapshots.c.turn_id==tid)).mappings()]


def copy_for_retry(db, actor, source_tid, target_tid):
    # Authorization is current; content and version are the original immutable facts.
    items=read_snapshots(db,actor,source_tid)
    for item in items:
        payload={key:value for key,value in item.items() if key not in ('object_id','version')}
        db.execute(insert(snapshots).values(**service.identity(),turn_id=target_tid,object_id=item['object_id'],version=item['version'],content=json.dumps(payload,ensure_ascii=False)))
    return items
