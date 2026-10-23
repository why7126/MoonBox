"""Canonical Sprint identity and preparation eligibility, without archive writes."""
import os
import re
import yaml
from app.chat.service import ChatError


def resolve(root, sprint_id):
    from app.chat.relations import _read_file
    if not re.fullmatch(r'sprint-\d{3}', sprint_id):
        raise ChatError(2509, '迭代标识无效', 403)
    active = f'iterations/change/{sprint_id}'
    archived = f'iterations/archive/{sprint_id}'
    present = [base for base in (active, archived) if os.path.lexists(root / base)]
    if len(present) != 1:
        raise ChatError(2509, '迭代事实源缺失或不唯一', 409)
    base = present[0]
    content = _read_file(root, base + '/sprint.yaml')
    try:
        plan = yaml.safe_load(content)
        if not isinstance(plan, dict) or plan.get('sprint_id') != sprint_id:
            raise ValueError()
        if plan.get('status') not in ('planning', 'active', 'in_progress', 'completed', 'closed', 'archived'):
            raise ValueError()
    except (ValueError, yaml.YAMLError):
        raise ChatError(2509, '迭代事实源不可确认', 409) from None
    return {'id': sprint_id, 'title': str(plan.get('title') or sprint_id)[:200],
            'path': base, 'status': plan['status'], 'content': content, 'plan': plan}


def scope_ids(plan):
    result = {}
    for kind, pattern in (('requirements', r'REQ-\d{4}(?:-[A-Za-z0-9_-]+)?'),
                          ('bugs', r'BUG-\d{4}(?:-[A-Za-z0-9_-]+)?'),
                          ('changes', r'[a-z0-9]+(?:-[a-z0-9]+)*')):
        values = plan.get(kind, [])
        if not isinstance(values, list):
            raise ValueError('scope_unknown')
        ids = []
        for value in values:
            if isinstance(value, dict):
                value = value.get('id') or value.get('change') or value.get('change_id')
            if not isinstance(value, str) or not re.fullmatch(pattern, value):
                raise ValueError('scope_unknown')
            ids.append(value)
        result[kind] = set(ids)
    return result


def preparation_reason(root, sprint_id, plan, *, resolved_scope=None):
    """Full scope only; capacity, sign-off and deep final evidence are independent."""
    from app.chat.relations import _read_file
    from app.governance.candidates import frontmatter
    from app.governance.archive_admission import linked_changes
    from app.services import requirement_center as center
    try:
        if plan.get('sprint_id') != sprint_id:
            return 'scope_unknown'
        members = scope_ids(plan)
        if not any(members.values()):
            return 'empty_scope'
        if plan.get('status') in ('archived', 'closed', 'completed'):
            return 'already_archived'
        if plan.get('status') not in ('planning', 'active', 'in_progress'):
            return 'scope_unknown'
        for kind in ('requirements', 'bugs'):
            if not members[kind]:
                continue
            registry = yaml.safe_load(_read_file(root, f'issues/{kind}/_registry.yaml'))
            for oid in members[kind]:
                matches = [e for e in registry['entries'] if isinstance(e, dict) and e.get('id') == oid]
                if len(matches) != 1:
                    return 'scope_unknown'
                entry = matches[0]
                base = entry.get('path', '').rstrip('/')
                if not re.fullmatch(rf'issues/{kind}/(?:plan|review|archive)/{re.escape(oid)}', base):
                    return 'scope_unknown'
                meta, _ = frontmatter(_read_file(root, base + '/trace.md').encode())
                if meta.get('status') != entry.get('status'):
                    return 'scope_unknown'
                if meta.get('status') not in ('done', 'closed', 'archived'):
                    return 'unarchived_scope'
                members['changes'].update(linked_changes(entry, meta))
        for change in members['changes']:
            if not isinstance(change, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', change):
                return 'scope_unknown'
            active = root / 'openspec/changes' / change
            archives = list((root / 'openspec/archive').glob(f'????-??-??-{change}'))
            if len(archives) + int(os.path.lexists(active)) != 1:
                return 'scope_unknown'
            if os.path.lexists(active):
                return 'unarchived_scope'
            for name in ('trace.md', 'proposal.md', 'tasks.md'):
                _read_file(root, f'openspec/archive/{archives[0].name}/{name}')
        if resolved_scope is not None:
            resolved_scope.update({key: sorted(values) for key, values in members.items()})
        return None
    except (ChatError, ValueError, TypeError, KeyError, AttributeError, yaml.YAMLError):
        return 'scope_unknown'


REASONS = {'empty_scope': '迭代范围为空，暂不能发起归档。',
           'scope_unknown': '迭代完整范围待核实，暂不能发起归档。',
           'unarchived_scope': '迭代内仍有未完成对象。',
           'already_archived': '迭代已关闭或归档。'}


def require_final(root, sprint_id, *, allow_closing=False):
    from app.services import requirement_center as center
    item = resolve(root, sprint_id)
    from app.chat.relations import _read_file
    try:
        _read_file(root, item['path'] + '/acceptance-report.md')
    except ChatError as error:
        if error.status != 503:
            raise
        raise ChatError(2604, '缺少迭代验收签署，暂不能归档。', 409, kind='governance_validation_failed') from None
    full_scope = {}
    eligibility_plan = item['plan']
    if allow_closing and eligibility_plan['status'] in ('closed', 'completed', 'archived'):
        eligibility_plan = {**eligibility_plan, 'status': 'active'}
    reason = preparation_reason(root, sprint_id, eligibility_plan, resolved_scope=full_scope)
    if reason:
        raise ChatError(2604, REASONS[reason], 409, kind='governance_validation_failed')
    # This keeps the existing deep Change evidence and sign-off gates at send.
    with center.using_governance_root(root):
        blockers = center._sprint_archive_blockers(sprint_id, {**item['plan'], **full_scope})
    if blockers:
        raise ChatError(2604, center._archive_safe_summary(blockers), 409,
                        kind='governance_validation_failed', details={'archive_blockers': [b.model_dump() for b in blockers]})
    return item
