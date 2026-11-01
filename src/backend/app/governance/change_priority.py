"""Narrow priority mutation; general independent Change documents remain read-only."""
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import yaml

from app.chat.service import ChatError
from app.governance.change_index import ChangeIndex
from app.governance.change_classification import classification
from app.governance.reader import version
from app.governance.snapshot import materialize
from app.services import requirement_center as legacy

LEVELS = ('P0', 'P1', 'P2', 'P3')


def plan(root, object_id, priority, expected_version, actor, timestamp):
    if priority not in LEVELS or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', object_id):
        raise ChatError(2604, '优先级或对象标识无效', 422)
    record = ChangeIndex(root).records.get(object_id)
    if not record or not record.directory or record.invalid_source or record.issue_ids:
        raise ChatError(2601, '仅支持无来源事项的独立变更', 403)
    if record.directory.parent != root / 'openspec/changes' or record.trace.get('status') in ('archived', 'closed'):
        raise ChatError(2601, '归档变更只读', 403)
    level = classification(object_id, record.trace)
    if level['classification_dimension'] != 'priority' or record.trace.get('change_type') not in (None, 'non_fix') or object_id.startswith('fix-'):
        raise ChatError(2606, '修复变更或类型冲突不能通过优先级接口修改', 409)
    path = record.directory / 'trace.md'
    if path.is_symlink() or not path.is_file():
        raise ChatError(2604, '变更追溯文档不可用', 422)
    previous = path.read_text()
    if version(previous) != expected_version:
        raise ChatError(2606, '版本已变化，请重载后重新选择', 409)
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(\r?\n|$)', previous, re.S)
    if not match:
        raise ChatError(2604, '变更追溯元数据无效', 422)
    metadata = yaml.safe_load(match.group(1))
    if not isinstance(metadata, dict):
        raise ChatError(2604, '变更追溯元数据无效', 422)
    if metadata.get('priority') == priority:
        return {}
    history = metadata.get('priority_history', [])
    if not isinstance(history, list):
        raise ChatError(2604, '分级记录格式无效', 422)
    old = metadata.get('priority')
    metadata['priority_history'] = [*history, {
        'old': old if old in LEVELS else None, 'old_state': 'valid' if old in LEVELS else 'missing' if old is None else 'invalid',
        'new': priority, 'actor_id': actor, 'changed_at': timestamp,
    }]
    metadata['priority'] = priority
    metadata['updated_at'] = timestamp
    body = '---\n' + yaml.safe_dump(metadata, allow_unicode=True, sort_keys=False) + '---\n' + previous[match.end():]
    return {str(path.relative_to(root)): body}


def enqueue_priority(reader, object_id, priority, expected_version, key):
    from app.governance import scope, writer
    project = scope.authorize(reader.db, reader.actor, reader.scope.space_id, reader.scope.repository_id, write=True)
    writer.maintenance(project)
    writer.assert_readable(reader.db, project)
    snapshot = reader.snapshot()
    reader.authorize_object(snapshot, object_id, change=True, write=True)
    timestamp = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
    with materialize(snapshot) as root, legacy.using_governance_root(root):
        after = plan(root, object_id, priority, expected_version, reader.actor, timestamp)
    record = dict(before={p: b.decode() for p, b in snapshot.files.items()}, after=after,
                  kind='change-priority', object_id=object_id, priority=priority,
                  expected_version=expected_version, actor_id=reader.actor, timestamp=timestamp,
                  delivery_context=getattr(reader, 'delivery_context', {}))
    request = dict(object=object_id, priority=priority, expected_version=expected_version)
    return writer.enqueue(reader.db, reader.actor, project, key, request, record, request_id=reader.request_id)
