"""Resolve delivery/Sprint authority from current server-side governance facts."""
import re
import yaml
from app.chat import service
from app.chat.relations import resolve_object, _read_file
from app.governance.scope import authorize, visible
from app.governance.sprint_object import resolve, scope_ids


def _meta(content):
    if not content.startswith('---\n'):
        raise service.ChatError(2606, '治理身份不可确认', 409)
    try:
        value = yaml.safe_load(content.split('---', 2)[1])
    except (yaml.YAMLError, IndexError):
        raise service.ChatError(2606, '治理身份不可确认', 409) from None
    if not isinstance(value, dict):
        raise service.ChatError(2606, '治理身份不可确认', 409)
    return value


def delivery(db, actor, space_id, repository_id, change_id):
    project = authorize(db, actor, space_id, repository_id, write=True)
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', change_id):
        raise service.ChatError(2606, '交付变更标识无效', 409)
    item = resolve_object(db, actor, space_id, repository_id, change_id)
    if item['path'] != 'openspec/changes/' + change_id:
        raise service.ChatError(2606, '变更不在活动交付范围', 409)
    meta = _meta(_read_file(project.root, item['path'] + '/trace.md'))
    # Conflicting aliases are never silently resolved by precedence.
    aliases = [meta[k] for k in ('iteration', 'sprint') if k in meta]
    if any(not isinstance(value, str) for value in aliases):
        raise service.ChatError(2606, '迭代归属格式无效', 409)
    sprint_values = set(aliases)
    if len(sprint_values) != 1:
        raise service.ChatError(2606, '迭代归属缺失或不唯一', 409)
    sprint = resolve(project.root, sprint_values.pop())
    if sprint['status'] not in ('planning', 'active', 'in_progress'):
        raise service.ChatError(2606, '迭代已关闭或不可操作', 409)
    try:
        members = scope_ids(sprint['plan'])
    except (ValueError, TypeError):
        raise service.ChatError(2606, '迭代范围不可确认', 409) from None
    if change_id not in members['changes'] or not visible(db, actor, project, sprint['id']):
        raise service.ChatError(2601, '无权操作所属迭代', 403)
    owners = [meta[k] for k in ('requirement_id', 'bug_id') if meta.get(k)]
    if len(owners) > 1:
        raise service.ChatError(2606, '交付链路不唯一', 409)
    root_id = owners[0] if owners else change_id
    if owners:
        if not isinstance(root_id, str) or not re.fullmatch(r'(REQ|BUG)-\d{4}(?:-[A-Za-z0-9_-]+)?', root_id):
            raise service.ChatError(2606, '交付链路标识无效', 409)
        issue = resolve_object(db, actor, space_id, repository_id, root_id)
        im = _meta(_read_file(project.root, issue['path'] + '/trace.md'))
        group = 'requirements' if root_id.startswith('REQ-') else 'bugs'
        linked = im.get('openspec_changes', [])
        if not isinstance(linked, list):
            raise service.ChatError(2606, '需求关联变更格式无效', 409)
        links = []
        for value in linked:
            link = value.get('change_id') if isinstance(value, dict) else value
            if not isinstance(link, str):
                raise service.ChatError(2606, '需求关联变更格式无效', 409)
            links.append(link)
        if (im.get('status') != 'in_sprint' or im.get('iteration') != sprint['id']
                or root_id not in members[group] or change_id not in links):
            raise service.ChatError(2606, '需求与迭代关联已变化', 409)
    if meta.get('status') not in ('proposed', 'in_progress', 'applied'):
        raise service.ChatError(2606, '变更阶段不允许交付操作', 409)
    return project, {'delivery_root': root_id, 'change_id': change_id,
        'sprint_id': sprint['id'], 'change_status': meta['status']}
