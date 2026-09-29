from __future__ import annotations

import json
import hashlib
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4, uuid5, NAMESPACE_URL
from sqlalchemy.exc import IntegrityError
from sqlalchemy import delete, and_, func, insert, or_, select, text, update
from sqlalchemy.orm import Session
from app.chat.schema import conversations, turns, events, messages, diffs, turn_materials, uploaded_materials

ACTIVE = ('queued', 'connecting', 'running', 'stopping', 'unknown')
TERMINAL = ('completed', 'failed', 'stopped')
MATERIAL_LIMITS = {
    'max_images': 5,
    'max_image_bytes': 5 * 1024 * 1024,
    'max_total_image_bytes': 20 * 1024 * 1024,
    'allowed_image_mime_types': ['image/png', 'image/jpeg', 'image/webp', 'image/gif'],
    'max_files': 8,
    'max_file_bytes': 10 * 1024 * 1024,
    'max_total_file_bytes': 40 * 1024 * 1024,
    'allowed_file_mime_types': ['image/png', 'image/jpeg', 'image/webp', 'image/gif', 'application/pdf',
        'text/plain', 'text/markdown', 'text/csv', 'application/json'],
    'max_skills': 5,
    'max_skill_summary_chars': 1200,
    'max_prompt_chars': 32000,
}
EXECUTION_CONFIG_KEYS = ('agent', 'model', 'reasoning')

def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')

def identity():
    stamp = now()
    return {'id': str(uuid4()), 'created_at': stamp, 'updated_at': stamp}

class ChatError(Exception):
    def __init__(self, code: int, message: str, status: int = 409, *, kind: str | None = None):
        self.code, self.message, self.status = code, message, status
        self.kind = kind


def authorize_space(db: Session, actor: str, space_id: str):
    row = db.execute(text('''SELECT s.id, s.expires_at FROM admin_spaces s WHERE s.id=:space
        AND s.status='ACTIVE' AND s.deleted_at IS NULL
        AND (s.owner_id=:actor OR EXISTS (SELECT 1 FROM admin_space_members m
          WHERE m.space_id=s.id AND m.user_id=:actor))'''),
        {'space': space_id, 'actor': actor}).first()
    if not row:
        raise ChatError(2501, '空间不可访问', 403)
    if row.expires_at is not None:
        try:
            expiry = datetime.fromisoformat(str(row.expires_at).replace('Z', '+00:00'))
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
        except ValueError:
            raise ChatError(2501, '空间有效期不可确认', 403)
        if expiry <= datetime.now(timezone.utc):
            raise ChatError(2501, '空间已到期', 403)


def conversation(db, actor, conversation_id):
    row = db.execute(select(conversations).where(conversations.c.id == conversation_id,
        conversations.c.owner_id == actor, conversations.c.deleted_at.is_(None))).mappings().first()
    if not row:
        raise ChatError(2502, '会话不存在或无权访问', 404)
    authorize_space(db, actor, row['space_id'])
    from app.chat.settings import repository_catalog
    if not any(item['id']==row['repository_id'] and item['space_id']==row['space_id'] for item in repository_catalog()):
        raise ChatError(2503,'会话仓库已撤销或不可访问',403)
    from app.chat.relations import authorize_history
    authorize_history(db, actor, dict(row))
    return dict(row)


def public_conversation(row, db=None, actor=None):
    data = {k: row[k] for k in ('id', 'space_id', 'repository_id', 'title', 'pinned', 'archived', 'active_turn_id', 'created_at', 'updated_at')}
    data['branch_name'] = row.get('branch_name') if hasattr(row, 'get') else row['branch_name']
    if db is not None and actor:
        from app.chat.policy import write_policy
        policy = write_policy(db, actor, row)
        data.update(write_scope=policy['write_scope'], write_reason_code=policy['reason_code'])
    return data


def create_conversation(db, actor, space_id, repository_id, title, client_request_id=None, branch_name=None):
    authorize_space(db, actor, space_id)
    # Repository IDs are opaque; paths are never accepted from the client.
    from app.chat.settings import repository_catalog
    if not any(r['id'] == repository_id and r['space_id'] == space_id for r in repository_catalog()):
        raise ChatError(2503, '仓库尚未配置或不可用', 503)
    branch_name = normalize_branch(repository_id, space_id, branch_name)
    row = {**identity(), 'owner_id': actor, 'space_id': space_id, 'repository_id': repository_id,
           'branch_name': branch_name, 'title': title, 'pinned': 0, 'archived': 0, 'active_turn_id': None, 'generation': 0}
    if client_request_id:
        row['id'] = str(uuid5(NAMESPACE_URL, json.dumps(['moonbox.chat.create.v1', actor, client_request_id])))
        existing = db.execute(select(conversations.c.id).where(conversations.c.id == row['id'])).first()
        if existing:
            return _created_replay(db, actor, row['id'], space_id, repository_id, branch_name)
    try:
        db.execute(insert(conversations).values(**row)); db.commit()
    except IntegrityError:
        db.rollback()
        if not client_request_id: raise
        return _created_replay(db, actor, row['id'], space_id, repository_id, branch_name)
    return public_conversation(row, db, actor)


def _created_replay(db, actor, cid, space_id, repository_id, branch_name):
    existing = conversation(db, actor, cid)
    if existing['space_id'] != space_id or existing['repository_id'] != repository_id or existing.get('branch_name', 'main') != branch_name:
        raise ChatError(2504, '创建请求标识已用于其他空间、仓库或分支')
    return public_conversation(existing, db, actor)


def normalize_branch(repository_id, space_id, value=None):
    from app.chat.settings import repository_branches
    data = repository_branches(repository_id, space_id)
    names = {item['name'] for item in data['items']}
    branch = (str(value or '')).strip() or data['default']
    if branch not in names:
        raise ChatError(2514, '分支不存在或不可用', 422, kind='branch_invalid')
    return branch


def list_conversations(db, actor, space_id, query, archived, page, page_size, filter=None):
    authorize_space(db, actor, space_id)
    conditions = [conversations.c.owner_id == actor, conversations.c.space_id == space_id,
                  conversations.c.deleted_at.is_(None)]
    if filter not in ('all','pinned'):conditions.append(conversations.c.archived == int(archived))
    if filter=='pinned':conditions.append(conversations.c.pinned==1)
    from app.chat.relations import authorize_history, read_relations
    # Filter before pagination/count so even titles and totals cannot reveal revoked context.
    rows = db.execute(select(conversations).where(*conditions).order_by(conversations.c.pinned.desc(),
        conversations.c.updated_at.desc(), conversations.c.id)).mappings().all()
    visible=[]
    for row in rows:
        try:
            authorize_history(db,actor,row)
            relation=read_relations(db,actor,row['id'])
        except ChatError: continue
        objects=([relation['primary']] if relation['primary'] else [])+relation['references']
        searchable=' '.join([row['title'], *[item['id']+' '+item['title'] for item in objects]])
        if query.casefold() not in searchable.casefold(): continue
        visible.append(public_conversation(row, db, actor))
    start=(page-1)*page_size
    return {'items':visible[start:start+page_size], 'total':len(visible), 'page':page, 'page_size':page_size}


def change_conversation(db, actor, cid, values):
    row = conversation(db, actor, cid)
    if 'archived' in values and row['active_turn_id']:
        raise ChatError(2504, '存在活动或状态未知的运行')
    result = db.execute(update(conversations).where(conversations.c.id == cid,
        conversations.c.active_turn_id.is_(None) if 'archived' in values else True,
        conversations.c.deleted_at.is_(None)).values(**values, updated_at=now()))
    if result.rowcount != 1:
        db.rollback(); raise ChatError(2504, '会话状态已变化')
    db.commit()
    return public_conversation(conversation(db, actor, cid), db, actor)


def turn(db, actor, tid):
    row = db.execute(select(turns).where(turns.c.id == tid)).mappings().first()
    if not row:
        raise ChatError(2502, '轮次不存在或无权访问', 404)
    conversation(db, actor, row['conversation_id'])
    return dict(row)


def public_turn(row):
    data = {k: row[k] for k in ('id','conversation_id','client_request_id','status','retry_of','error_code','created_at','updated_at')}
    if 'image_count' in row: data['image_count'] = row['image_count']
    if 'skill_count' in row: data['skill_count'] = row['skill_count']
    data['requested_config'] = _json_config(row.get('requested_config') if hasattr(row, 'get') else None)
    data['effective_config'] = _json_config(row.get('effective_config') if hasattr(row, 'get') else None)
    data['config_fallback_reason'] = row.get('config_fallback_reason') if hasattr(row, 'get') else None
    return data


def material_capabilities():
    return dict(MATERIAL_LIMITS)


def upload_material(db, actor, space_id, repository_id, name, mime, content):
    authorize_space(db, actor, space_id)
    from app.chat.settings import repository_catalog
    if not any(r['id'] == repository_id and r['space_id'] == space_id for r in repository_catalog()):
        raise ChatError(2503, '仓库尚未配置或不可用', 503)
    mime = _clean_text(mime, 80)
    if mime not in MATERIAL_LIMITS['allowed_file_mime_types']:
        raise ChatError(2510, '文件格式不受支持', 422, kind='file_type')
    if not content or len(content) > MATERIAL_LIMITS['max_file_bytes']:
        raise ChatError(2510, '文件大小超过限制', 422, kind='file_size')
    kind = 'image' if mime.startswith('image/') else 'file'
    extension = _safe_extension(name, mime)
    token = identity()
    object_key = f'chat/materials/{space_id}/{repository_id}/{token["id"]}{extension}'
    row = {**token, 'actor_id': actor, 'space_id': space_id, 'repository_id': repository_id,
        'object_key': object_key, 'kind': kind, 'name': _clean_text(name, 200) or 'attachment',
        'mime_type': mime, 'size_bytes': len(content), 'status': 'uploading', 'deleted_at': None}
    db.execute(insert(uploaded_materials).values(**row)); db.commit()
    try:
        from app.core.object_storage import get_object_storage
        get_object_storage().put(object_key, content, mime)
        db.execute(update(uploaded_materials).where(uploaded_materials.c.id == row['id'], uploaded_materials.c.status == 'uploading')
            .values(status='ready', updated_at=now()))
        db.commit(); row['status'] = 'ready'
    except Exception:
        db.rollback()
        db.execute(update(uploaded_materials).where(uploaded_materials.c.id == row['id']).values(status='failed', updated_at=now()))
        db.commit()
        raise ChatError(2510, '文件保存失败，请重试', 503, kind='file_unavailable') from None
    return public_uploaded_material(row)


def public_uploaded_material(row):
    return {'ref_id': row['id'], 'kind': row['kind'], 'name': row['name'], 'mime_type': row['mime_type'],
        'size_bytes': row['size_bytes'], 'status': row['status']}


def read_uploaded_material_content(db, actor, material_id):
    row = db.execute(select(uploaded_materials).where(uploaded_materials.c.id == material_id,
        uploaded_materials.c.actor_id == actor, uploaded_materials.c.status == 'ready',
        uploaded_materials.c.deleted_at.is_(None))).mappings().first()
    if not row:
        raise ChatError(2510, '文件引用已失效，请重新上传', 404, kind='file_stale')
    try:
        from app.core.object_storage import get_object_storage
        stored = get_object_storage().get(row['object_key'])
    except FileNotFoundError:
        raise ChatError(2510, '文件引用已失效，请重新上传', 404, kind='file_stale') from None
    except Exception:
        raise ChatError(2510, '文件读取失败，请重试', 503, kind='file_unavailable') from None
    return {'data': stored.data, 'content_type': row['mime_type'] or stored.content_type or 'application/octet-stream'}


def _safe_extension(name, mime):
    suffix = Path(str(name or '')).suffix.lower()
    allowed = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.pdf', '.txt', '.md', '.csv', '.json'}
    if suffix in allowed:
        return suffix
    return {'image/png': '.png', 'image/jpeg': '.jpg', 'image/webp': '.webp', 'image/gif': '.gif',
        'application/pdf': '.pdf', 'text/plain': '.txt', 'text/markdown': '.md',
        'text/csv': '.csv', 'application/json': '.json'}.get(mime, '.bin')


def execution_capabilities():
    from app.chat.settings import execution_config
    return execution_config()


def _json_config(value):
    try:
        parsed = json.loads(value or '{}')
        return {key: parsed[key] for key in EXECUTION_CONFIG_KEYS if isinstance(parsed.get(key), str)}
    except (TypeError, ValueError):
        return {}


def same_requested_config(stored, requested):
    parsed = _json_config(stored)
    return not parsed or parsed == requested


def _option_map(config, group):
    return {item['value']: item for item in config[group]}


def normalize_execution_config(value=None):
    config = execution_capabilities()
    incoming = value if isinstance(value, dict) else {}
    requested = {key: str(incoming.get(key) or config['defaults'][key]).strip() for key in EXECUTION_CONFIG_KEYS}
    for key, group in (('agent', 'agents'), ('model', 'models'), ('reasoning', 'reasoning')):
        options = _option_map(config, group)
        option = options.get(requested[key])
        if not option:
            raise ChatError(2513, '执行配置不可用', 422, kind='execution_config_invalid')
        if not option.get('available'):
            raise ChatError(2513, option.get('disabled_reason') or '执行配置不可用', 409, kind='execution_config_unavailable')
    return {
        'requested': requested,
        'effective': dict(requested),
        'fallback_reason': None,
        'policy_version': config['policy_version'],
    }


def execution_config_metadata(config):
    effective = (config or {}).get('effective') or {}
    result = {key: effective[key] for key in EXECUTION_CONFIG_KEYS if isinstance(effective.get(key), str)}
    reason = (config or {}).get('fallback_reason')
    if isinstance(reason, str) and reason:
        result['config_fallback'] = reason[:80]
    return result


def _clean_text(value, limit):
    value = str(value or '').strip()
    return value[:limit]


def normalize_materials(images=None, skills=None):
    attachments = images or []
    skills = skills or []
    if len(attachments) > MATERIAL_LIMITS['max_files']:
        raise ChatError(2510, '文件数量超过限制', 422, kind='file_limit')
    if len(skills) > MATERIAL_LIMITS['max_skills']:
        raise ChatError(2511, 'Skill 引用数量超过限制', 422, kind='skill_limit')
    image_total = 0
    file_total = 0
    image_count = 0
    normalized = []
    for index, item in enumerate(attachments):
        mime = _clean_text(item.get('mime_type'), 80)
        size = item.get('size_bytes', 0)
        kind = _clean_text(item.get('kind') or ('image' if mime.startswith('image/') else 'file'), 24)
        if kind not in ('image', 'file'):
            raise ChatError(2510, '文件类型无效', 422, kind='file_kind')
        if mime not in MATERIAL_LIMITS['allowed_file_mime_types']:
            raise ChatError(2510, '文件格式不受支持', 422, kind='file_type')
        if type(size) is not int or size <= 0 or size > MATERIAL_LIMITS['max_file_bytes']:
            raise ChatError(2510, '文件大小超过限制', 422, kind='file_size')
        file_total += size
        if file_total > MATERIAL_LIMITS['max_total_file_bytes']:
            raise ChatError(2510, '文件总大小超过限制', 422, kind='file_total_size')
        if kind == 'image':
            image_count += 1
            image_total += size
            if image_count > MATERIAL_LIMITS['max_images']:
                raise ChatError(2510, '图片数量超过限制', 422, kind='image_limit')
            if size > MATERIAL_LIMITS['max_image_bytes']:
                raise ChatError(2510, '图片大小超过限制', 422, kind='image_size')
            if image_total > MATERIAL_LIMITS['max_total_image_bytes']:
                raise ChatError(2510, '图片总大小超过限制', 422, kind='image_total_size')
        name = _clean_text(item.get('name'), 200) or f'attachment-{index + 1}'
        ref_id = _clean_text(item.get('ref_id'), 128)
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', ref_id or ''):
            ref_id = None
        normalized.append({'kind': kind, 'ordinal': index, 'status': 'referenced', 'name': name,
            'summary': f"{name} · {mime} · {size} bytes", 'mime_type': mime, 'size_bytes': size,
            'ref_id': ref_id,
            'metadata': {'registration': 'uploaded' if ref_id else 'client_reference', 'sha256': _clean_text(item.get('sha256'), 64)}})
    for index, item in enumerate(skills):
        skill_id = _clean_text(item.get('id'), 96)
        name = _clean_text(item.get('name') or skill_id, 120)
        source = _clean_text(item.get('source'), 200)
        digest = _clean_text(item.get('digest'), 64)
        if not skill_id or not name or '..' in source or source.startswith('/'):
            raise ChatError(2511, 'Skill 引用无效', 422, kind='skill_invalid')
        summary = _clean_text(item.get('summary') or f'{name}（{source or "未声明来源"}）', MATERIAL_LIMITS['max_skill_summary_chars'])
        normalized.append({'kind': 'skill', 'ordinal': index, 'status': 'snapshotted', 'name': name,
            'summary': summary, 'mime_type': None, 'size_bytes': len(summary.encode()), 'ref_id': skill_id,
            'metadata': {'source': source, 'digest': digest, 'injection_scope': 'context_reference_only'}})
    return normalized


def material_fingerprint(materials):
    public = [{k: item.get(k) for k in ('kind','ordinal','name','summary','mime_type','size_bytes','ref_id','metadata')} for item in (materials or [])]
    return hashlib.sha256(json.dumps(public, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def material_counts(materials):
    return {'image_count': sum(1 for item in materials if item['kind'] == 'image'),
        'file_count': sum(1 for item in materials if item['kind'] == 'file'),
        'skill_count': sum(1 for item in materials if item['kind'] == 'skill')}


def material_message(prompt, materials):
    if not materials:
        return prompt
    lines = [prompt.strip()] if prompt.strip() else ['（仅材料上下文）']
    images = [item for item in materials if item['kind'] == 'image']
    files = [item for item in materials if item['kind'] == 'file']
    skills = [item for item in materials if item['kind'] == 'skill']
    if images:
        lines.append('图片引用：' + '；'.join(item['summary'] for item in images))
    if files:
        lines.append('文件引用：' + '；'.join(item['summary'] for item in files))
    if skills:
        lines.append('Skill 引用：' + '；'.join(item['name'] for item in skills))
    return '\n'.join(lines)


def save_materials(db, tid, materials):
    for item in materials:
        db.execute(insert(turn_materials).values(**identity(), turn_id=tid, kind=item['kind'],
            ordinal=item['ordinal'], status=item['status'], name=item['name'], summary=item['summary'],
            mime_type=item.get('mime_type'), size_bytes=item.get('size_bytes') or 0, ref_id=item.get('ref_id'),
            metadata=json.dumps(item.get('metadata') or {}, ensure_ascii=False)))


def read_turn_materials(db, turn_ids):
    if not turn_ids:
        return {}
    rows = db.execute(select(turn_materials).where(turn_materials.c.turn_id.in_(turn_ids))
        .order_by(turn_materials.c.turn_id, turn_materials.c.kind, turn_materials.c.ordinal)).mappings()
    result = {}
    for row in rows:
        metadata = json.loads(row['metadata'] or '{}')
        if row['kind'] == 'image' and row['ref_id'] and not any(metadata.get(key) for key in ('preview_url', 'url', 'download_url', 'content_url')):
            metadata['preview_url'] = f'/api/v1/chat/materials/{row["ref_id"]}/content'
        result.setdefault(row['turn_id'], []).append({'kind': row['kind'], 'status': row['status'],
            'ordinal': row['ordinal'], 'name': row['name'], 'summary': row['summary'], 'mime_type': row['mime_type'],
            'size_bytes': row['size_bytes'], 'ref_id': row['ref_id'], 'metadata': metadata})
    return result


def skill_candidates(db, actor, *, cid=None, space_id=None, repository_id=None):
    if cid:
        row = conversation(db, actor, cid)
        space_id, repository_id = row['space_id'], row['repository_id']
    else:
        if not space_id or not repository_id:
            raise ChatError(2503, '仓库尚未选择', 422)
        authorize_space(db, actor, space_id)
        from app.chat.settings import repository_catalog
        if not any(item['id'] == repository_id and item['space_id'] == space_id for item in repository_catalog()):
            raise ChatError(2503, '仓库尚未配置或不可用', 503)
    from app.chat.settings import repository_binding
    binding = repository_binding(repository_id, space_id) or {}
    root = Path(binding.get('governance_root') or Path.cwd())
    skill_root = (root / '.agents' / 'skills').resolve()
    try:
        if root.resolve() not in skill_root.parents or not skill_root.exists():
            return {'items': [], 'boundary': 'skill-directory-unavailable'}
        items = []
        for skill_md in sorted(skill_root.glob('*/SKILL.md'))[:80]:
            raw = skill_md.read_text(encoding='utf-8', errors='replace')
            name = skill_md.parent.name[:120]
            first = _skill_summary(raw, name)
            digest = hashlib.sha256(raw.encode()).hexdigest()
            items.append({'id': name, 'name': name, 'summary': first, 'source': f'.agents/skills/{name}/SKILL.md',
                'digest': digest, 'injection_scope': 'context_reference_only'})
        return {'items': items, 'boundary': 'context-reference-only'}
    except OSError:
        return {'items': [], 'boundary': 'skill-read-failed'}


def _skill_summary(raw, fallback):
    lines = raw.splitlines()
    body_start = 0
    if lines and lines[0].strip() == '---':
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == '---':
                body_start = index + 1
                break
            if line.strip().startswith('description:'):
                value = line.split(':', 1)[1].strip().strip('"').strip("'")
                if value:
                    return value[:200]
    for line in lines[body_start:]:
        text = line.strip()
        if not text or text == '---' or re.match(r'^[A-Za-z_][A-Za-z0-9_-]*:', text):
            continue
        return text.strip('# ').strip()[:200] or fallback
    return fallback


def revalidate_skill_materials(db, actor, row, materials):
    if not any(item['kind'] == 'skill' for item in materials):
        return materials
    candidates = {item['id']: item for item in skill_candidates(db, actor, space_id=row['space_id'], repository_id=row['repository_id'])['items']}
    updated = []
    for item in materials:
        if item['kind'] != 'skill':
            updated.append(item); continue
        candidate = candidates.get(item.get('ref_id'))
        if not candidate or (item.get('metadata') or {}).get('digest') not in ('', candidate['digest']):
            raise ChatError(2511, 'Skill 引用已失效，请重新选择', 409, kind='skill_stale')
        refreshed = dict(item)
        refreshed.update(name=candidate['name'], summary=candidate['summary'], size_bytes=len(candidate['summary'].encode()),
            metadata={'source': candidate['source'], 'digest': candidate['digest'], 'injection_scope': candidate['injection_scope']})
        updated.append(refreshed)
    return updated


def revalidate_uploaded_materials(db, actor, row, materials):
    refs = [item.get('ref_id') for item in materials if item['kind'] in ('image', 'file') and item.get('ref_id')]
    if not refs:
        return materials
    rows = {item['id']: item for item in db.execute(select(uploaded_materials).where(
        uploaded_materials.c.id.in_(refs), uploaded_materials.c.actor_id == actor,
        uploaded_materials.c.space_id == row['space_id'], uploaded_materials.c.repository_id == row['repository_id'],
        uploaded_materials.c.status == 'ready', uploaded_materials.c.deleted_at.is_(None))).mappings()}
    updated = []
    for item in materials:
        ref = item.get('ref_id')
        if item['kind'] not in ('image', 'file') or not ref:
            updated.append(item); continue
        uploaded = rows.get(ref)
        if not uploaded:
            raise ChatError(2510, '文件引用已失效，请重新上传', 409, kind='file_stale')
        refreshed = dict(item)
        refreshed.update(kind=uploaded['kind'], status='uploaded', name=uploaded['name'], mime_type=uploaded['mime_type'],
            size_bytes=uploaded['size_bytes'], summary=f"{uploaded['name']} · {uploaded['mime_type']} · {uploaded['size_bytes']} bytes",
            metadata={'registration': 'object_storage_upload', **({'preview_url': f'/api/v1/chat/materials/{ref}/content'} if uploaded['kind'] == 'image' else {})})
        updated.append(refreshed)
    return updated


def request_turn(db, actor, cid, client_id, prompt, *, images=None, skills=None, execution_config=None, request_id=None):
    prompt = (prompt or '').strip()
    materials = normalize_materials(images, skills)
    config = normalize_execution_config(execution_config)
    if not prompt and not any(item['kind'] in ('image', 'file') for item in materials):
        raise ChatError(2512, '请输入消息或添加文件', 422, kind='empty_input')
    row = conversation(db, actor, cid)
    materials = revalidate_uploaded_materials(db, actor, row, materials)
    materials = revalidate_skill_materials(db, actor, row, materials)
    previous = db.execute(select(turns).where(turns.c.conversation_id == cid, turns.c.client_request_id == client_id)).mappings().first()
    if previous:
        previous_materials = read_turn_materials(db, [previous['id']]).get(previous['id'], [])
        if previous['prompt'] != prompt or material_fingerprint(previous_materials) != material_fingerprint(materials) or not same_requested_config(previous.get('requested_config'), config['requested']):
            raise ChatError(2504, '同一请求标识不能用于不同输入')
        result = public_turn(previous)
        result.update(material_counts(previous_materials))
        return result
    if row['archived']:
        raise ChatError(2504, '归档会话只读')
    if row['active_turn_id']:
        raise ChatError(2504, '原运行尚未终止或状态未知')
    from app.governance.preparation import check_send
    check_send(db, actor, row)
    from app.chat.isolated import allowed
    if allowed(db,actor,row['space_id'],row['repository_id']):
        from app.chat.admission import enqueue
        from app.chat.settings import execution_limits
        return enqueue(db,actor,cid,client_id,prompt,execution_limits(),materials=materials,execution_config=config,request_id=request_id)
    # Normal deployment stays closed; only the isolated launcher has a test gate.
    raise ChatError(2505, '执行服务尚未通过隔离与额度验收，暂不可发送', 503)


def interrupt(db, actor, tid):
    row = turn(db, actor, tid)
    if row['status'] in TERMINAL:
        return public_turn(row)
    if row['status'] == 'unknown':
        raise ChatError(2506, '原运行状态未知，需先核实执行端')
    if row['status'] == 'queued':
        changed = db.execute(update(turns).where(turns.c.id == tid, turns.c.status == 'queued').values(status='stopped', updated_at=now())).rowcount
        if changed:
            db.execute(update(conversations).where(conversations.c.id == row['conversation_id'], conversations.c.active_turn_id == tid).values(active_turn_id=None, updated_at=now()))
            from app.chat.admission import settle
            from app.chat.schema import snapshots
            context_bytes=sum(len(value.encode()) for value in db.scalars(select(snapshots.c.content).where(snapshots.c.turn_id==tid)))
            from app.chat.observability import trace
            trace(db,tid,'stopped')
            settle(db,tid,0,len(row['prompt'].encode())+context_bytes)
            db.commit(); return public_turn(turn(db, actor, tid))
    db.execute(update(turns).where(turns.c.id == tid, turns.c.status.in_(('connecting','running'))).values(status='stopping', updated_at=now()))
    db.commit()
    return public_turn(turn(db, actor, tid))


def read_events(db, actor, tid, after):
    turn(db, actor, tid)
    rows = db.execute(select(events).where(events.c.turn_id == tid, events.c.sequence > after).order_by(events.c.sequence).limit(200)).mappings()
    return [{'sequence': r['sequence'], 'type': r['event_type'], 'payload': json.loads(r['payload'])} for r in rows]


def read_diff(db, actor, tid):
    row_turn = turn(db, actor, tid)
    row = db.execute(select(diffs).where(diffs.c.turn_id == tid)).mappings().first()
    if not row:
        return {'available': False, 'reason': '尚无可信差异快照', 'files': []}
    payload = json.loads(row['payload'])
    data = payload if isinstance(payload, dict) else {'files': payload}
    result = {'available': True, 'before_hash': row['before_hash'], 'after_hash': row['after_hash'], **data}
    return _attach_workspace_status(db, row_turn, result)


def _attach_workspace_status(db, row_turn, result):
    try:
        parent = db.execute(select(conversations).where(conversations.c.id == row_turn['conversation_id'])).mappings().one()
        from app.chat.settings import repository_binding
        binding = repository_binding(parent['repository_id'], parent['space_id']) or {}
        workspace_id = parent['workspace_id']
        root = binding.get('workspace_root')
        if not workspace_id or not isinstance(root, str):
            return result
        from app.chat.workspace import snapshot, trusted_directory
        workspace = trusted_directory(Path(root) / workspace_id)
        current = snapshot(workspace, max_text_bytes=0)
        for key in ('files', 'cumulative_files'):
            if isinstance(result.get(key), list):
                result[key] = [_with_workspace_status(workspace, current, item) for item in result[key]]
    except Exception:
        for key in ('files', 'cumulative_files'):
            if isinstance(result.get(key), list):
                result[key] = [{**item, 'workspace_status': 'unknown'} if isinstance(item, dict) else item for item in result[key]]
    return result


def _with_workspace_status(workspace, current, item):
    if not isinstance(item, dict) or not isinstance(item.get('path'), str):
        return item
    path = item['path']
    current_file = current['files'].get(path)
    status = 'missing' if current_file is None else 'present'
    if _git_untracked(workspace, path):
        status = 'untracked'
    current_sha = current_file.get('sha256') if current_file else None
    expected_sha = item.get('after_sha256') if item.get('status') != 'deleted' else None
    if expected_sha and current_sha and expected_sha != current_sha:
        status = 'mismatch'
    return {**item, 'workspace_status': status}


def _git_untracked(workspace, path):
    if path.startswith('/') or '..' in Path(path).parts:
        return False
    try:
        from app.chat.workspace import git_env
        result = subprocess.run(['git', '-C', str(workspace), 'status', '--porcelain=v1', '--untracked-files=all', '--', path],
            env=git_env(), capture_output=True, timeout=5)
        return any(line.startswith('?? ') for line in result.stdout.decode('utf-8', 'replace').splitlines())
    except (OSError, subprocess.SubprocessError):
        return False


def delete_empty_conversation(db, actor, cid):
    row = conversation(db, actor, cid)
    from app.chat.schema import governance_candidates
    if db.scalar(select(governance_candidates.c.id).where(governance_candidates.c.conversation_id == cid)):
        raise ChatError(2605, '治理成果仍在保留期内，不能删除会话', 409)
    if row['active_turn_id'] or db.scalar(select(func.count()).select_from(turns).where(turns.c.conversation_id == cid)):
        raise ChatError(2507, '包含执行数据的会话需先验证代码及副本清理状态，暂不可删除')
    # The conversation is tombstoned, so later writes cannot resurrect it.
    changed = db.execute(update(conversations).where(conversations.c.id == cid,
        conversations.c.active_turn_id.is_(None), conversations.c.deleted_at.is_(None)).values(
            deleted_at=now(), updated_at=now(), title='', cleanup_status='empty_tombstone')).rowcount
    if not changed:
        db.rollback(); raise ChatError(2504, '会话状态已变化')
    from app.chat.schema import relations
    db.execute(delete(relations).where(relations.c.conversation_id==cid))
    db.commit()


def request_retry(db, actor, tid, client_id, *, request_id=None):
    original=turn(db,actor,tid)
    parent=conversation(db,actor,original['conversation_id'])
    previous=db.execute(select(turns).where(turns.c.conversation_id==parent['id'],turns.c.client_request_id==client_id)).mappings().first()
    if previous:
        if previous['retry_of'] != tid: raise ChatError(2504,'同一请求标识不能用于不同重试')
        return public_turn(previous)
    if original['status'] not in ('failed','stopped') or parent['active_turn_id'] or parent['archived']:
        raise ChatError(2506,'原运行未确认失败或停止，或会话当前不可重试')
    from app.chat.isolated import allowed
    if allowed(db,actor,parent['space_id'],parent['repository_id']):
        from app.chat.admission import enqueue
        from app.chat.settings import execution_limits
        original_materials = read_turn_materials(db, [tid]).get(tid, [])
        return enqueue(db,actor,parent['id'],client_id,original['prompt'],execution_limits(),retry_of=tid,materials=original_materials,request_id=request_id)
    raise ChatError(2505,'执行服务尚未通过隔离与额度验收，暂不可重试',503)
