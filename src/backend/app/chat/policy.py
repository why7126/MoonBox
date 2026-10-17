"""Fail-closed write eligibility from current server-side space and governance facts."""
import re
import hashlib
import json
import yaml
from sqlalchemy import select, text
from app.chat import service
from app.chat.schema import relations, turns
from app.chat.relations import resolve_object, _entries, _read_file, _root

WRITE_SCOPE_READ_ONLY = 'read_only'
WRITE_SCOPE_GOVERNANCE = 'governance_write'
WRITE_SCOPE_IMPLEMENTATION = 'implementation_write'
WRITE_SCOPE_ARCHIVE = 'archive_write'


def write_allowed(db, actor, parent):
    return write_policy(db, actor, parent)['write_scope'] != WRITE_SCOPE_READ_ONLY


def write_policy(db, actor, parent, *, evidence=None):
    base = {'write_scope': WRITE_SCOPE_READ_ONLY, 'reason_code': 'default_read_only'}
    try:
        service.authorize_space(db,actor,parent['space_id'])
    except service.ChatError:
        return {**base, 'reason_code': 'space_forbidden'}
    if not _actor_can_write_space(db, actor, parent['space_id']):
        return {**base, 'reason_code': 'actor_not_writer'}
    oid=db.scalar(select(relations.c.object_id).where(relations.c.conversation_id==parent['id'],relations.c.role=='primary'))
    if not oid:
        return {**base, 'reason_code': 'primary_object_required'}
    # Captured requirements may edit only their isolated prepared workspace.
    # The trusted collector still validates the full workspace and exact four-file result.
    from app.governance.preparation import _candidate_for_turn, _current_workspace_candidate
    candidate=(_candidate_for_turn(db,parent['id'],parent.get('active_turn_id'))
        if parent.get('active_turn_id') else _current_workspace_candidate(db,parent['id']))
    if candidate:
        try:
            from app.governance import scope
            project=scope.authorize(db,actor,parent['space_id'],parent['repository_id'],write=True)
            allowed = (candidate['actor_id']==actor and candidate['object_id']==oid
                and candidate['action'] in ('req-generate','bug-generate','req-complete','bug-complete','req-review','bug-review') and candidate['state']=='running'
                and candidate['binding_revision']==project.binding_revision
                and scope.visible(db,actor,project,oid))
            return {'write_scope': WRITE_SCOPE_GOVERNANCE if allowed else WRITE_SCOPE_READ_ONLY,
                'reason_code': 'governance_candidate_running' if allowed else 'governance_candidate_invalid'}
        except service.ChatError:
            return {**base, 'reason_code': 'governance_candidate_forbidden'}
    try:
        if _legacy_archive_transition_ready(db, parent, oid, actor):
            return {'write_scope': WRITE_SCOPE_ARCHIVE, 'reason_code': 'archive_change_transition'}
        item=resolve_object(db,actor,parent['space_id'],parent['repository_id'],oid)
        entry=next(row for row in _entries(item['root'], item['id']) if row['id']==item['id'])
        if evidence is not None:
            evidence['object_id'] = item['id']
            evidence['entry_sha256'] = hashlib.sha256(json.dumps(entry, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()
        if item['id'].startswith(('REQ-', 'BUG-')) and str(entry.get('status') or '') in ('captured', 'exploring'):
            return {**base, 'reason_code': 'analysis_object_read_only'}
        if _archive_ready(db, parent, item, entry):
            return {'write_scope': WRITE_SCOPE_ARCHIVE, 'reason_code': 'archive_change_applied'}
        if _implementation_ready(item, entry, evidence=evidence):
            return {'write_scope': WRITE_SCOPE_IMPLEMENTATION, 'reason_code': 'implementation_change_in_sprint'}
        if _governance_writable(entry):
            return {'write_scope': WRITE_SCOPE_GOVERNANCE, 'reason_code': 'governance_object_writable'}
        return {**base, 'reason_code': 'governance_object_read_only'}
    except GovernanceFieldError as error:
        return {**base, 'reason_code': error.code}
    except (service.ChatError,ValueError,TypeError,KeyError,IndexError,StopIteration,yaml.YAMLError):
        return {**base, 'reason_code': 'governance_facts_invalid'}


def _actor_can_write_space(db, actor, space_id):
    service.authorize_space(db,actor,space_id)
    row=db.execute(text('''SELECT s.owner_id,m.role FROM admin_spaces s LEFT JOIN admin_space_members m
        ON m.space_id=s.id AND m.user_id=:actor WHERE s.id=:space'''),{'actor':actor,'space':space_id}).first()
    return bool(row and (row.owner_id==actor or row.role in ('管理员','编辑者')))


def _governance_writable(entry):
    status = str(entry.get('status') or '')
    return status not in ('archived','closed','done','completed','cancelled')


def _legacy_archive_transition_ready(db, parent, oid, actor):
    """Keep one archive turn alive while its complete legacy source is copied."""
    if not isinstance(oid, str) or not re.fullmatch(r'(?:[a-z0-9][a-z0-9-]{0,100}|(?:REQ|BUG)-\d{4}(?:-[A-Za-z0-9_-]+)?)', oid):
        return False
    primary = db.scalar(select(relations.c.object_id).where(
        relations.c.conversation_id == parent['id'], relations.c.role == 'primary'))
    if primary != oid:
        return False
    turn_id = parent.get('active_turn_id')
    prompt = db.scalar(select(turns.c.prompt).where(turns.c.id == turn_id)) if turn_id else None
    lines = str(prompt or '').splitlines()
    if not lines or lines[0].strip() != f'/opsx-archive {oid}':
        return False
    try:
        root = _root(parent['repository_id'], parent['space_id'])
        issue = oid.startswith(('REQ-', 'BUG-'))
        if issue:
            entries = [row for row in _entries(root, oid) if row['id'] == oid]
            if len(entries) != 1:
                return False
            entry = entries[0]
            if str(entry.get('status') or '') in ('captured', 'exploring'):
                return False
            change = entry.get('related_change')
            if (not isinstance(change, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,100}', change)
                    or entry.get('iteration') is None):
                return False
            # The Issue remains a valid, readable primary object while only
            # its linked Change is in the CLI legacy archive directory.
            resolve_object(db, actor, parent['space_id'], parent['repository_id'], oid)
        else:
            change = oid
        if (root / 'openspec/changes' / change).exists():
            return False
        legacy = root / 'openspec/changes/archive'
        matches = list(legacy.glob(f'????-??-??-{change}')) if legacy.is_dir() else []
        if len(matches) != 1 or not matches[0].is_dir() or matches[0].is_symlink():
            return False
        # Across mounts shutil.move creates the canonical directory before
        # copying trace.md. The validated legacy source remains complete until
        # the copy finishes, so permit only that exact partial destination.
        canonical = list((root / 'openspec/archive').glob(f'????-??-??-{change}'))
        if len(canonical) > 1 or any(
            target.name != matches[0].name or not target.is_dir() or target.is_symlink()
            for target in canonical
        ):
            return False
        source = _read_file(root, f'openspec/changes/archive/{matches[0].name}/trace.md')
        trace = yaml.safe_load(source.split('---', 2)[1]) if source.startswith('---\n') else None
        if not isinstance(trace, dict) or trace.get('status') not in ('applied', 'archived'):
            return False
        issue_pattern = r'(?:REQ|BUG)-\d{4}(?:-[A-Za-z0-9_-]+)?'
        requirement = _alias_value(trace, ('requirement', 'requirement_id', 'req_id', 'source_requirement'), issue_pattern)
        bug = _alias_value(trace, ('bug', 'bug_id', 'source_bug', 'related_bug'), issue_pattern)
        if issue:
            if (bug if oid.startswith('BUG-') else requirement) != oid:
                return False
        elif requirement or bug:
            return False
        sprint = _alias_value(trace, ('sprint', 'iteration'), r'sprint-\d{3}')
        if not sprint or (issue and entry['iteration'] != sprint):
            return False
        plan = yaml.safe_load(_read_file(root, f'iterations/change/{sprint}/sprint.yaml'))
        return (isinstance(plan, dict) and isinstance(plan.get('changes'), list)
                and change in plan['changes']
                and (not issue or oid in plan.get('bugs' if oid.startswith('BUG-') else 'requirements', [])))
    except (service.ChatError, GovernanceFieldError, OSError, ValueError, TypeError, KeyError, yaml.YAMLError):
        return False


class GovernanceFieldError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _alias_value(trace, names, pattern):
    values = []
    for name in names:
        value = trace.get(name)
        if value is None or value == '':
            continue
        if not isinstance(value, str) or not re.fullmatch(pattern, value):
            raise GovernanceFieldError('implementation_facts_invalid')
        values.append(value)
    if len(set(values)) > 1:
        raise GovernanceFieldError('implementation_facts_conflict')
    return values[0] if values else None


def _implementation_ready(item, entry, *, evidence=None):
    if entry.get('status') != 'in_sprint':
        return False
    change = entry.get('related_change')
    sprint = entry.get('iteration')
    if not isinstance(change, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,100}', change):
        return False
    if not isinstance(sprint, str) or not re.fullmatch(r'sprint-\d{3}', sprint):
        return False
    source = _read_file(item['root'], f'openspec/changes/{change}/trace.md')
    if not source.startswith('---\n'):
        return False
    trace = yaml.safe_load(source.split('---', 2)[1])
    plan_source = _read_file(item['root'], f'iterations/change/{sprint}/sprint.yaml')
    plan = yaml.safe_load(plan_source)
    if evidence is not None:
        evidence.update(change_id=change, sprint_id=sprint,
            change_sha256=hashlib.sha256(source.encode()).hexdigest(),
            sprint_sha256=hashlib.sha256(plan_source.encode()).hexdigest())
    if not isinstance(trace, dict) or not isinstance(plan, dict):
        return False
    issue_pattern = r'(?:REQ|BUG)-\d{4}(?:-[A-Za-z0-9_-]+)?'
    bug = _alias_value(trace, ('bug', 'bug_id', 'source_bug', 'related_bug'), issue_pattern)
    requirement = _alias_value(trace, ('requirement', 'requirement_id', 'req_id', 'source_requirement'), issue_pattern)
    linked_sprint = _alias_value(trace, ('sprint', 'iteration'), r'sprint-\d{3}')
    if (bug and not bug.startswith('BUG-')) or (requirement and not requirement.startswith('REQ-')):
        raise GovernanceFieldError('implementation_facts_invalid')
    # A BUG may also reference its parent REQ; the same-kind source must match.
    linked_issue = bug if item['id'].startswith('BUG-') else requirement
    if linked_issue is not None and linked_issue != item['id']:
        raise GovernanceFieldError('implementation_source_mismatch')
    if linked_sprint is not None and linked_sprint != sprint:
        raise GovernanceFieldError('implementation_sprint_mismatch')
    lists = [plan.get(key, []) for key in ('changes', 'requirements', 'bugs')]
    if any(not isinstance(values, list) or any(not isinstance(v, str) for v in values) for values in lists):
        raise GovernanceFieldError('implementation_facts_invalid')
    return (trace.get('status') in ('proposed', 'in_progress') and linked_sprint == sprint
            and linked_issue == item['id'] and change in lists[0]
            and item['id'] in lists[1] + lists[2])


def _archive_ready(db, parent, item, entry):
    try:
        active_turn_id = parent['active_turn_id']
    except (KeyError, TypeError):
        active_turn_id = None
    prompt = db.scalar(select(turns.c.prompt).where(turns.c.id == active_turn_id)) if active_turn_id else ''
    lines = str(prompt or '').splitlines()
    first = lines[0].strip() if lines else ''
    if not re.fullmatch(r'/opsx-archive\s+' + re.escape(item['id']), first):
        return False
    direct_change = item['path'].startswith(('openspec/changes/', 'openspec/archive/'))
    change = item['id'] if direct_change else entry.get('related_change')
    if not isinstance(change, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,100}', change):
        return False
    try:
        relative = f'openspec/changes/{change}/trace.md'
        if not (item['root'] / relative).exists():
            archive_root = item['root'] / 'openspec/archive'
            matches = list(archive_root.glob(f'????-??-??-{change}'))
            if len(matches) == 1:
                relative = f'openspec/archive/{matches[0].name}/trace.md'
            elif item['path'].startswith('openspec/changes/archive/'):
                relative = f'{item["path"]}/trace.md'
            else:
                return False
        source = _read_file(item['root'], relative)
        if not source.startswith('---\n'):
            return False
        trace = yaml.safe_load(source.split('---', 2)[1])
    except (service.ChatError, ValueError, TypeError, KeyError, yaml.YAMLError):
        return False
    if not isinstance(trace, dict):
        return False
    linked_requirement = trace.get('requirement') or trace.get('requirement_id') or trace.get('source_requirement')
    linked_bug = trace.get('bug') or trace.get('bug_id') or trace.get('source_bug')
    if direct_change:
        issue_pattern = r'(?:REQ|BUG)-\d{4}(?:-[A-Za-z0-9_-]+)?'
        try:
            requirement = _alias_value(trace, ('requirement', 'requirement_id', 'req_id', 'source_requirement'), issue_pattern)
            bug = _alias_value(trace, ('bug', 'bug_id', 'source_bug', 'related_bug'), issue_pattern)
            sprint = _alias_value(trace, ('sprint', 'iteration'), r'sprint-\d{3}')
        except GovernanceFieldError:
            return False
        if requirement or bug or trace.get('status') not in ('applied', 'archived'):
            return False
        if sprint is None:
            return False
        try:
            plan = yaml.safe_load(_read_file(item['root'], f'iterations/change/{sprint}/sprint.yaml'))
        except (service.ChatError, ValueError, TypeError, yaml.YAMLError):
            return False
        return isinstance(plan, dict) and isinstance(plan.get('changes'), list) and change in plan['changes']
    return trace.get('status') in ('applied', 'archived') and item['id'] in (linked_requirement, linked_bug)
