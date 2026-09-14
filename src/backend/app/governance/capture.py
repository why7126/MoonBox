"""Capture plans are generated under the project's writer fence, never by clients."""
from datetime import datetime
import re
from zoneinfo import ZoneInfo
import yaml
from app.governance.snapshot import stable, validate


def markdown(meta, body):
    return '---\n' + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + '---\n\n' + body


def cell(value):
    return str(value).replace('|', '&#124;').replace('\r', ' ').replace('\n', ' ').replace('`', '&#96;')


def plan(project, payload, actor, operation_id):
    before = stable(project.root).files
    folder = 'requirements' if payload['type'] == 'requirement' else 'bugs'
    prefix = 'REQ' if folder == 'requirements' else 'BUG'
    base = f'issues/{folder}'
    registry_path = f'{base}/_registry.yaml'
    registry = yaml.safe_load(before[registry_path])
    numbers = [0]
    # Include orphan/empty directories, not only registered files.
    candidates = [entry['id'] for entry in registry['entries']]
    for stage in ('plan', 'review', 'archive', ''):
        directory = project.root / base / stage
        if directory.exists():
            candidates.extend(child.name for child in directory.iterdir())
    for name in candidates:
        match = re.match(rf'^{prefix}-(\d+)(?:-|$)', name)
        if match:
            numbers.append(int(match[1]))
    next_id = registry.get('next_id', 1)
    if not isinstance(next_id, int) or isinstance(next_id, bool) or next_id < 1:
        raise ValueError('invalid_registry_number')
    number = max(next_id, max(numbers) + 1)
    if number > 9999:
        raise ValueError('issue_number_exhausted')
    slug = re.sub(r'[^a-z0-9]+', '-', payload['title'].lower()).strip('-')[:40].rstrip('-') or 'capture'
    issue_id = f'{prefix}-{number:04d}-{slug}'
    path = f'{base}/plan/{issue_id}'
    if (project.root / path).exists():
        raise ValueError('issue_exists')
    now = datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')
    key = 'requirement_id' if folder == 'requirements' else 'bug_id'
    level_key = 'priority' if folder == 'requirements' else 'severity'
    level = payload[level_key]
    meta = {key: issue_id, 'title': payload['title'], 'status': 'captured',
            'created_at': now, 'updated_at': now, level_key: level,
            'owner': payload['owner'], 'source': payload['source'], 'lifecycle_stage': 'plan'}
    capture = markdown(meta, '# 现象\n\n' + payload['title'] + '\n\n# 补充说明\n\n' + (payload['description'] or '无') + '\n')
    trace_meta = {**meta, 'iteration': None, 'openspec_changes': [],
                  'lifecycle': {'captured': now, 'generated': None, 'completed': None, 'reviewed': None, 'approved': None}}
    if folder == 'bugs':
        trace_meta.update(related_requirement=None, related_bug=None)
    trace_body = f'# {issue_id} Trace\n\n## 变更记录\n\n| 时间 | 事件 | 状态 | 说明 |\n|---|---|---|---|\n| {now} | capture | captured | 需求中心创建并持久化 |\n'
    entry = {'id': issue_id, 'title': payload['title'], 'status': 'captured',
             level_key: level, 'owner': payload['owner'], 'source': payload['source'],
             'lifecycle_stage': 'plan', 'path': path + '/', 'created': now, 'iteration': None, 'related_change': None}
    if folder == 'bugs':
        entry.update(reporter='user', related_requirement=None, related_bug=None)
    else:
        entry.update(type='feature', requester='user', related_changes=[])
    registry['next_id'] = number + 1
    registry['entries'].insert(0, entry)
    index_path = f'{base}/CHANGELOG.md'
    index = before.get(index_path, b'').decode()
    command = '/req-generate' if folder == 'requirements' else '/bug-generate'
    label = 'REQ' if folder == 'requirements' else 'BUG'
    header = f'| {label} | 标题 | {"优先级" if folder == "requirements" else "严重等级"} | 当前状态 | 阶段 | 关联 Sprint | 关联 Change | 最近更新时间 | 下一步 | 事实源 |'
    row = f'| {issue_id} | {cell(payload["title"])} | {level} | captured | plan | 无 | 无 | {now} | `{command} {issue_id}` | `{path}/trace.md` |'
    lines = index.splitlines()
    table = next((i for i, line in enumerate(lines) if line.startswith(f'| {label} |') and '事实源' in line), None)
    if table is not None and table + 1 < len(lines) and re.match(r'^\|[\s:|-]+\|$', lines[table + 1]):
        lines.insert(table + 2, row)
        index = '\n'.join(lines) + '\n'
        index = re.sub(r'^updated_at:.*$', 'updated_at: ' + now, index, count=1, flags=re.M)
    else:
        index += '\n## 当前态看板\n\n' + header + '\n|---|---|---|---|---|---|---|---|---|---|\n' + row + '\n'
        if not before.get(index_path):
            index = markdown({'created_at': now, 'updated_at': now}, '# 当前态索引\n' + index)
    after = {f'{path}/capture.md': capture, f'{path}/trace.md': markdown(trace_meta, trace_body),
             registry_path: yaml.safe_dump(registry, allow_unicode=True, sort_keys=False), index_path: index}
    validate({**before, **{name: body.encode() for name, body in after.items()}})
    return {'before': {name: body.decode() for name, body in before.items()}, 'after': after,
            'object_id': issue_id, 'planned': True, 'new_directory': path}
