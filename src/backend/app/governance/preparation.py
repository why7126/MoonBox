"""Prepare a governed personal session without sending a model prompt."""
import hashlib
import json
import re
import subprocess
import sys
import yaml
from datetime import datetime, timezone
from uuid import NAMESPACE_URL, uuid4, uuid5
from sqlalchemy import func, insert, select, update
from sqlalchemy.exc import IntegrityError
from app.chat import service, relations
from app.chat.schema import governance_applications as applications, governance_candidates as candidates, messages, turns, conversations, relations as chat_relations
from app.chat.workspace import git, snapshot as code_snapshot
from app.governance import scope, store
from app.governance.reader import ProjectReader
from app.governance.snapshot import safe_load, stable
from app.governance.candidates import frontmatter, validate, action_spec, display_prompt, execution_prompt

EXECUTOR_UNAVAILABLE_MARKERS=(
    'bwrap: Creating new namespace failed',
    'Creating new namespace failed',
    'Resource temporarily unavailable',
    'dry-run 未能启动',
    '执行环境连续报错',
)

READ_ONLY_OBJECT_ACTIONS={'open-chat','req-explore','bug-explore','explore'}
GOVERNANCE_FACT_ROOTS=('issues','iterations','openspec','docs','rules')

ISSUE_ACTION_RULES={
    'req-generate': {'prefix':'REQ-','statuses':{'captured','exploring'},'required':['capture.md'],'kind':'需求','next':'/req-generate'},
    'bug-generate': {'prefix':'BUG-','statuses':{'captured'},'required':['capture.md'],'kind':'缺陷','next':'/bug-generate'},
    'req-complete': {'prefix':'REQ-','statuses':{'draft','enriching'},'required':['requirement.md'],'kind':'需求','next':'/req-complete'},
    'bug-complete': {'prefix':'BUG-','statuses':{'draft','enriching'},'required':['bug.md'],'kind':'缺陷','next':'/bug-complete'},
    'req-review': {'prefix':'REQ-','statuses':{'pending_review'},'required':['requirement.md'],'kind':'需求','next':'/req-review'},
    'bug-review': {'prefix':'BUG-','statuses':{'pending_review'},'required':['bug.md'],'kind':'缺陷','next':'/bug-review'},
    'req-opsx': {'prefix':'REQ-','statuses':{'in_sprint'},'required':['requirement.md'],'kind':'需求','next':'/req-opsx'},
    'bug-opsx': {'prefix':'BUG-','statuses':{'in_sprint'},'required':['bug.md'],'kind':'缺陷','next':'/bug-opsx'},
}
ISSUE_ACTION_FALLBACKS={
    'sprint-propose': {'statuses':{'approved'},'required':[],'kind':'需求或缺陷','next':'/sprint-propose'},
    'opsx-apply': {'statuses':{'in_sprint','applied'},'required':[],'kind':'需求、缺陷或 Change','next':'/opsx-apply'},
    'opsx-modify': {'statuses':{'in_sprint','applied'},'required':[],'kind':'需求、缺陷或 Change','next':'/opsx-modify'},
    'opsx-archive': {'statuses':{'in_sprint','applied','done'},'required':[],'kind':'需求、缺陷或 Change','next':'/opsx-archive'},
}
CHANGE_ACTION_STATUSES={
    'opsx-apply': {'proposed','in_progress'},
    'opsx-modify': {'applied'},
    'opsx-archive': {'applied'},
}


def _action_name(action):
    value=(action or 'open-chat').strip().split()[0]
    return value[1:] if value.startswith('/') else value


def _workspace_standard_deployment_outdated():
    return service.ChatError(2606,'运行服务未更新到可读取完整仓库 Git 快照的标准部署，已阻断发送。',503,
        kind='workspace_fact_source_stale',
        details={'reason':'standard_deployment_outdated','suggested_action':'run_standard_deployment'})


def _ensure_executor_snapshot(project):
    if getattr(project,'source_root_unavailable',False):
        raise _workspace_standard_deployment_outdated()
    snapshot_root=getattr(project,'source_root',None) or project.root
    projected=stable(project.root)
    source = stable(snapshot_root)
    if source.revision != projected.revision:
        # The projection may have advanced while the source was being read.
        projected = stable(project.root)
    if source.revision != projected.revision:
        raise service.ChatError(2606,'治理目录与源工作区内容不一致，请同步事实源后重试。',
            409,kind='workspace_fact_source_stale',
            details={'reason':'manifest_mismatch','suggested_action':'sync_governance_facts'})
    return projected


def _object_session_snapshot(db, actor, project):
    """Read fresh source/projection bytes inside the reader's epoch/auth fence.

    Retained bytes are only candidates for an independent complete safe read.
    Never carry this result across reconciliation or another request boundary.
    """
    from app.governance.read_snapshot import stable_read
    reader = ProjectReader(db, actor, project)

    def load():
        if getattr(project, 'source_root_unavailable', False):
            raise _workspace_standard_deployment_outdated()
        source_root = getattr(project, 'source_root', None) or project.root
        # Identical authorized roots describe one tree, not two replicas.
        if source_root == project.root:
            return stable_read(project.root, project.binding_revision, parallel_cold=True)
        from app.governance.read_snapshot import stable_alias_read
        aliased = stable_alias_read(project.root, source_root, project.binding_revision, parallel_cold=True)
        if aliased is not None:
            return aliased
        from app.governance.read_snapshot import read_workers
        if read_workers() > 1:
            # Independent replicas can overlap on sufficiently provisioned
            # hosts. Every read still opens and validates all file bytes.
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=2) as pool:
                projected_read = pool.submit(stable_read, project.root, project.binding_revision)
                source = stable_read(source_root, project.binding_revision)
                projected = projected_read.result()
        else:
            projected = stable_read(project.root, project.binding_revision)
            source = stable_read(source_root, project.binding_revision)
        if source.revision != projected.revision:
            projected = stable_read(project.root, project.binding_revision)
        if source.revision != projected.revision:
            raise service.ChatError(2606, '治理目录与源工作区内容不一致，请同步事实源后重试。',
                409, kind='workspace_fact_source_stale',
                details={'reason': 'manifest_mismatch', 'suggested_action': 'sync_governance_facts'})
        return projected

    return reader, reader.snapshot(loader=load)


def _real_source_workspace(project, source, workspace):
    root=getattr(project,'source_root',None) or project.root
    try:
        return source == root and workspace == root
    except Exception:
        return False


def _require_issue_fact_source(snapshot, object_id, action, root=None, *, target_change_id=None):
    rule=ISSUE_ACTION_RULES.get(action) or ISSUE_ACTION_FALLBACKS.get(action)
    if not rule:
        return None
    if action in ISSUE_ACTION_FALLBACKS and not object_id.startswith(('REQ-','BUG-')):
        return None
    if 'prefix' in rule and not object_id.startswith(rule['prefix']):
        raise service.ChatError(2604,f"{rule['next']} 只能用于{rule['kind']}对象",422,kind='governance_validation_failed')
    folder='requirements' if object_id.startswith('REQ-') else 'bugs'
    document='requirement.md' if object_id.startswith('REQ-') else 'bug.md'
    registry_name=f'issues/{folder}/_registry.yaml'
    try:
        import yaml
        registry=yaml.safe_load(snapshot.files[registry_name]) or {}
        matches=[entry for entry in registry.get('entries',[]) if isinstance(entry,dict) and entry.get('id')==object_id]
    except Exception:
        raise service.ChatError(2604,'项目注册表不可读取，已阻断发送',409,kind='governance_validation_failed')
    if len(matches)!=1:
        raise service.ChatError(2604,'未在当前执行器事实源中找到完整对象 ID，已阻断发送',409,kind='governance_validation_failed')
    entry=matches[0];base=str(entry.get('path') or '').rstrip('/')
    expected_prefix=f'issues/{folder}/'
    if not base.startswith(expected_prefix) or not base.endswith(object_id):
        raise service.ChatError(2604,'注册表路径与对象 ID 不一致，已阻断发送',409,kind='governance_validation_failed')
    try:
        trace_meta,_=frontmatter(snapshot.files[f'{base}/trace.md'])
    except (KeyError, ValueError):
        raise service.ChatError(2604,'缺少 trace.md，已阻断发送',409,kind='governance_validation_failed')
    trace_status=str(trace_meta.get('status') or '')
    registry_status=str(entry.get('status') or '')
    if trace_status not in rule['statuses'] or (registry_status and registry_status!=trace_status):
        expected=' / '.join(sorted(rule['statuses']))
        raise service.ChatError(2604,f"对象状态需为 {expected}，当前 registry={registry_status or 'unknown'}、trace={trace_status or 'unknown'}，已阻断发送",
            409,kind='governance_validation_failed')
    required={*rule.get('required',[])}
    if action in ISSUE_ACTION_FALLBACKS:
        required.add(document)
    for name in required:
        if not snapshot.files.get(f'{base}/{name}',b'').strip():
            raise service.ChatError(2604,f"缺少 {name}，已阻断发送",409,kind='governance_validation_failed')
    if action in {'req-opsx','bug-opsx'}:
        iteration=trace_meta.get('iteration')
        if not isinstance(iteration,str) or not re.fullmatch(r'sprint-\d{3}',iteration):
            raise service.ChatError(2604,'对象缺少有效迭代归属，已阻断发送',409,kind='governance_validation_failed')
        sprint_path=f'iterations/change/{iteration}/sprint.yaml'
        try:
            sprint=yaml.safe_load(snapshot.files[sprint_path]) or {}
        except (KeyError,ValueError,yaml.YAMLError):
            raise service.ChatError(2604,'迭代正式范围不可读取，已阻断发送',409,kind='governance_validation_failed')
        scope_key='requirements' if action=='req-opsx' else 'bugs'
        members=sprint.get(scope_key) if isinstance(sprint,dict) else None
        if (not isinstance(sprint,dict) or sprint.get('sprint_id')!=iteration
                or not isinstance(members,list) or object_id not in members
                or sprint.get('status') in {'completed','closed','archived'}):
            raise service.ChatError(2604,'对象未列入归属迭代的正式范围，已阻断发送',409,kind='governance_validation_failed')
    if action in CHANGE_ACTION_STATUSES:
        from app.governance.archive_admission import linked_changes
        links=linked_changes(entry, trace_meta)
        bound_record = None
        if target_change_id is not None and root is not None:
            from app.governance.change_index import ChangeIndex
            bound_record = ChangeIndex(root).records.get(target_change_id)
            if not bound_record or object_id not in bound_record.issue_ids or bound_record.invalid_source:
                raise service.ChatError(2604, '来源与交付目标不匹配，已阻断发送', 409, kind='delivery_target_mismatch')
            links = [target_change_id]
        # A source-only command cannot select one delivery from several, even
        # when only one happens to be eligible today. Retries must not drift.
        if len(set(links)) > 1:
            raise service.ChatError(2604, '来源关联多个 Change，请使用明确交付目标；当前入口不支持目标选择',
                                    409, kind='delivery_target_required')
        eligible=False
        for change_id in links:
            if not isinstance(change_id,str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',change_id):
                continue
            try:
                change_meta,_=frontmatter(snapshot.files[f'openspec/changes/{change_id}/trace.md'])
            except (KeyError,ValueError):
                continue
            if (bound_record is not None or _matches_change_source(change_meta, object_id)) and change_meta.get('status') in CHANGE_ACTION_STATUSES[action]:
                eligible=True
                break
        if not eligible and action == 'opsx-archive' and root is not None and len(links) == 1:
            from app.governance.direct_command_journal import archive_spec_drift
            change_id = links[0]
            if isinstance(change_id, str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', change_id):
                journal = root / 'openspec/archive/.archive-recovery' / f'{change_id}.json'
                archives = list((root / 'openspec/archive').glob(f'????-??-??-{change_id}'))
                if journal.is_file() and len(archives) == 1 and not archive_spec_drift(change_id, root):
                    relative = f'openspec/archive/{archives[0].name}/trace.md'
                    try:
                        change_meta, _ = frontmatter(snapshot.files[relative])
                    except (KeyError, ValueError):
                        change_meta = {}
                    eligible = _matches_change_source(change_meta, object_id) and change_meta.get('status') in ('applied', 'archived')
        if not eligible:
            raise service.ChatError(2604,'对象没有处于该动作阶段的关联活动 Change，已阻断发送',409,kind='governance_validation_failed')
    return {'id':object_id,'path':base,'title':str(entry.get('title') or object_id)[:200],'status':trace_status}


def _matches_change_source(metadata, object_id):
    from app.chat.policy import _alias_value, GovernanceFieldError
    keys = (('requirement', 'requirement_id', 'req_id', 'source_requirement')
            if object_id.startswith('REQ-') else ('bug', 'bug_id', 'source_bug', 'related_bug'))
    try:
        return _alias_value(metadata, keys, r'(?:REQ|BUG)-\d{4}(?:-[A-Za-z0-9_-]+)?') == object_id
    except GovernanceFieldError:
        return False


def _require_change_fact_source(snapshot, reader, object_id, action):
    if action not in ISSUE_ACTION_FALLBACKS or object_id.startswith(('REQ-','BUG-')):
        return None
    if action == 'opsx-archive' and f'openspec/changes/{object_id}/trace.md' not in snapshot.files:
        from app.governance.direct_command_journal import archive_spec_drift
        root = reader.scope.root
        journal = root / 'openspec/archive/.archive-recovery' / f'{object_id}.json'
        if journal.is_file() and not archive_spec_drift(object_id, root):
            item = relations.resolve_object(reader.db, reader.actor, reader.scope.space_id,
                                            reader.scope.repository_id, object_id)
            base = item['path']
            if base.startswith(('openspec/archive/', 'openspec/changes/archive/')):
                try:
                    metadata, _ = frontmatter(snapshot.files[f'{base}/trace.md'])
                except (KeyError, ValueError):
                    raise service.ChatError(2604, '归档恢复现场不可读取', 409,
                                            kind='governance_validation_failed') from None
                sprint = metadata.get('sprint') or metadata.get('iteration')
                try:
                    plan = safe_load(snapshot.files[f'iterations/change/{sprint}/sprint.yaml'])
                except (KeyError, ValueError, yaml.YAMLError):
                    plan = None
                if (metadata.get('status') in ('applied', 'archived')
                        and re.fullmatch(r'sprint-\d{3}', str(sprint))
                        and isinstance(plan, dict) and object_id in plan.get('changes', [])):
                    return {'id': object_id, 'path': base, 'title': item['title'],
                            'status': 'archive_pending'}
    reader.authorize_object(snapshot,object_id,change=True,write=True)
    if action in ('sprint-propose', 'opsx-apply'):
        from app.governance.change_index import ChangeIndex
        index = ChangeIndex(reader.scope.root)
        record = index.records.get(object_id)
        if action == 'sprint-propose' and (not record or record.issue_ids or record.invalid_source
                or record.stage != 'sprint-planning'
                or index.sprint_assignment(record)[0] != 'unassigned'):
            raise service.ChatError(2604, 'Change 不处于待纳入迭代状态，请核对归属', 409, kind='governance_validation_failed')
        if (action == 'opsx-apply' and record and not record.issue_ids
                and record.stage in ('ready-dev', 'sprint-planning')
                and index.sprint_assignment(record)[0] != 'valid'):
            raise service.ChatError(2604, '缺少唯一有效的 Sprint 归属，请先核对迭代', 409, kind='governance_validation_failed')
    base=f'openspec/changes/{object_id}'
    trace=snapshot.files.get(f'{base}/trace.md') or snapshot.files.get(f'{base}/proposal.md')
    if not trace:
        raise service.ChatError(2604,'活动 Change 不可读取，已阻断发送',409,kind='governance_validation_failed')
    if action in CHANGE_ACTION_STATUSES:
        try:
            change_meta,_=frontmatter(snapshot.files[f'{base}/trace.md'])
        except (KeyError,ValueError):
            raise service.ChatError(2604,'缺少活动 Change 追踪文件，已阻断发送',409,kind='governance_validation_failed')
        if change_meta.get('status') not in CHANGE_ACTION_STATUSES[action]:
            raise service.ChatError(2604,'Change 未处于该动作阶段，已阻断发送',409,kind='governance_validation_failed')
    title=object_id
    if trace:
        try:
            meta,_=frontmatter(trace)
            title=str(meta.get('title') or meta.get('change_id') or object_id)[:200]
        except Exception:
            title=object_id
    return {'id':object_id,'path':base,'title':title,'status':'change'}


def _preflight_object_session(db, actor, project, object_id, action):
    from .controlled_successor import authority
    with authority(db, project, actor):
        return _preflight_object_session_authorized(db, actor, project, object_id, action)


def _preflight_object_session_authorized(db, actor, project, object_id, action):
    name=_action_name(action)
    if name in READ_ONLY_OBJECT_ACTIONS:
        if not object_id.startswith(('REQ-', 'BUG-', 'sprint-')):
            reader = ProjectReader(db, actor, project)
            reader.authorize_object(reader.snapshot(summary=True), object_id, change=True)
        return relations.resolve_object(db,actor,project.space_id,project.repository_id,object_id)
    reader, snapshot = _object_session_snapshot(db, actor, project)
    if object_id.startswith('sprint-') or name == 'sprint-archive':
        if name != 'sprint-archive':
            raise service.ChatError(2604, '该动作不适用于 Sprint 对象', 422)
        from app.governance.sprint_object import resolve, preparation_reason, REASONS
        item = resolve(project.root, object_id)
        if item['path'] != f'iterations/change/{object_id}':
            raise service.ChatError(2604, '迭代已归档，不能再次准备归档', 409)
        relations._authorize_object(db, actor, project.space_id, project.repository_id, object_id)
        reason = preparation_reason(project.root, object_id, item['plan'])
        if reason:
            raise service.ChatError(2604, REASONS[reason], 409, kind='governance_validation_failed')
        return {**item, 'root': project.root, 'version': snapshot.revision}
    if object_id.startswith(('REQ-','BUG-')):
        entry=reader.authorize_object(snapshot,object_id,write=True)[0]
        full_id=entry['id']
        item=_require_issue_fact_source(snapshot,full_id,name,project.root)
        if item:
            if name == 'opsx-archive':
                from app.governance.archive_admission import issue_acceptance, linked_changes
                trace_meta, _ = frontmatter(snapshot.files[item['path'] + '/trace.md'])
                links = linked_changes(entry, trace_meta)
                admission = issue_acceptance(project.root, project.root / item['path'], links, source_root=getattr(project, "source_root", None))
                if not admission['ready']:
                    raise service.ChatError(2604, admission['reason'], 409, kind='governance_validation_failed')
                from app.governance.change_index import ChangeIndex
                index = ChangeIndex(project.root)
                for cid in links:
                    record = index.records.get(cid)
                    reason = index.acceptance_source_reason(record, source_root=getattr(project, 'source_root', None)) if record else '关联 Change 不可读取'
                    if reason:
                        raise service.ChatError(2604, reason, 409, kind='governance_validation_failed')
            return {'id':full_id,'title':item['title'],'version':snapshot.revision,'content':'','status':item['status'],'path':item['path'],'root':project.root}
    change_item=_require_change_fact_source(snapshot,reader,object_id,name)
    if change_item:
        if name == 'opsx-archive':
            from app.governance.archive_admission import change_acceptance
            admission = change_acceptance(project.root, change_item['id'], source_root=getattr(project, "source_root", None))
            if not admission['ready']:
                details = None
                if admission.get('recovery_reason') == 'archive_requirement_conflict':
                    from app.governance.rule_change import conflicts
                    try:
                        if conflicts(project, change_item['id']):
                            details = {'archive_blockers': [{
                                'type': 'change', 'id': change_item['id'],
                                'status': 'archive_requirement_conflict',
                                'message': '规则内容已修改，需检查后继续',
                                'action_hint': '查看修改并补齐当前验收与历史证据后重新检查归档',
                                'visible': True,
                            }]}
                    except (OSError, ValueError, KeyError, TypeError):
                        pass
                raise service.ChatError(2604, admission['reason'], 409,
                                        kind='governance_validation_failed', details=details)
            from app.governance.change_index import ChangeIndex
            index = ChangeIndex(project.root)
            record = index.records.get(change_item['id'])
            reason = index.acceptance_source_reason(record, source_root=getattr(project, 'source_root', None)) if record else '关联 Change 不可读取'
            if reason:
                raise service.ChatError(2604, reason, 409, kind='governance_validation_failed')
        return {'id':change_item['id'],'title':change_item['title'],'version':snapshot.revision,'content':'','status':change_item['status'],'path':change_item['path'],'root':project.root}
    return {**relations.resolve_object(db,actor,project.space_id,project.repository_id,object_id),'version':snapshot.revision}


def _candidate_id(actor, scope_key, object_id, action, request_id):
    stamp = datetime.now(timezone.utc).isoformat(timespec='microseconds')
    if not request_id:
        return {'id': service.identity()['id'], 'created_at': stamp, 'updated_at': stamp}
    stable = uuid5(NAMESPACE_URL, f'moonbox.governance.prepare.v1:{actor}:{scope_key}:{object_id}:{action}:{request_id}')
    return {'id': str(stable), 'created_at': stamp, 'updated_at': stamp}


def _latest_object_conversation(db, actor, space_id, repository_id, object_id):
    latest_turn = select(turns.c.conversation_id, func.max(turns.c.updated_at).label('latest_turn_at')).group_by(turns.c.conversation_id).subquery()
    latest_message = select(turns.c.conversation_id, func.max(messages.c.updated_at).label('latest_message_at')).select_from(
        turns.join(messages, messages.c.turn_id == turns.c.id)
    ).group_by(turns.c.conversation_id).subquery()
    row = db.execute(select(conversations)
        .join(chat_relations, chat_relations.c.conversation_id == conversations.c.id)
        .outerjoin(latest_turn, latest_turn.c.conversation_id == conversations.c.id)
        .outerjoin(latest_message, latest_message.c.conversation_id == conversations.c.id)
        .where(conversations.c.owner_id == actor, conversations.c.space_id == space_id,
            conversations.c.repository_id == repository_id, conversations.c.archived == 0,
            conversations.c.deleted_at.is_(None),
            chat_relations.c.object_id == object_id, chat_relations.c.role == 'primary')
        .order_by(conversations.c.active_turn_id.is_(None),
            latest_turn.c.latest_turn_at.is_(None), latest_turn.c.latest_turn_at.desc(),
            latest_message.c.latest_message_at.is_(None), latest_message.c.latest_message_at.desc(),
            conversations.c.updated_at.desc(), conversations.c.created_at.desc(), conversations.c.id.desc())
        .limit(1)).mappings().first()
    return dict(row) if row else None


def _candidate_for_turn(db, cid, turn_id):
    if not turn_id:
        return None
    return db.execute(select(candidates).where(candidates.c.conversation_id == cid,
        (candidates.c.prepared_turn_id == turn_id) | (candidates.c.turn_id == turn_id))
        .order_by(candidates.c.created_at.desc(), candidates.c.id.desc())).mappings().first()


def _current_prepared_candidate(db, cid):
    row = db.execute(select(candidates).where(candidates.c.conversation_id == cid)
        .order_by(candidates.c.created_at.desc(), candidates.c.id.desc()).limit(1)).mappings().first()
    if row and row['state'] == 'prepared' and row['prepared_turn_id'] is None:
        return row
    return None


def _current_workspace_candidate(db, cid, turn_id=None):
    if turn_id is not None:
        bound = _candidate_for_turn(db, cid, turn_id)
        if bound:
            return bound
        return db.execute(select(candidates).where(candidates.c.conversation_id == cid,
            candidates.c.prepared_turn_id.is_(None), candidates.c.turn_id.is_(None),
            candidates.c.state.in_(('prepared', 'running')))
            .order_by(candidates.c.created_at.desc(), candidates.c.id.desc()).limit(1)).mappings().first()
    return db.execute(select(candidates).where(candidates.c.conversation_id == cid,
        candidates.c.state.in_(('prepared', 'running')))
        .order_by(candidates.c.created_at.desc(), candidates.c.id.desc()).limit(1)).mappings().first()


def prepare(db,actor,space_id,repository_id,object_id,action='req-generate',request_id=None,idempotency_key=None,*,conversation_id=None):
    project=scope.authorize(db,actor,space_id,repository_id,write=True)
    _ensure_executor_snapshot(project)
    store.root()  # Fail before creating a conversation if private storage is unavailable.
    from app.governance.execution_context import visible_state, reconcile
    reconcile(db, actor, project)
    db.commit()
    resolved = relations.resolve_object(db, actor, space_id, repository_id, object_id)
    busy = visible_state(db, actor, project, resolved['id'])
    if not busy['can_send']:
        return {'preparation_id': None, 'conversation_id': busy.get('view_conversation_id'),
                'object_id': resolved['id'], 'prompt': '', 'state': 'busy',
                'reused_conversation': bool(busy.get('view_conversation_id')), **busy}
    spec=action_spec(action)
    reader=ProjectReader(db,actor,project);baseline=reader.snapshot()
    entry=reader.authorize_object(baseline,object_id)[0];object_id=entry['id'];base=entry['path'].rstrip('/')
    if not object_id.startswith(spec['prefix']) or base!=f"{spec['folder']}/plan/{object_id}":
        raise service.ChatError(2604,f"当前仅支持采集池{spec['kind_cn']}的 {action}",422)
    # Execution sees the project governance context. Do not copy objects hidden from this actor.
    if any(not scope.visible(db,actor,project,item['id']) for item in reader.entries(baseline)):
        raise service.ChatError(2601,'当前权限不足以准备完整项目治理上下文',403)
    try:
        metadata,_=frontmatter(baseline.files[f'{base}/trace.md'])
        allowed_stages = ('captured', 'exploring') if action == 'req-generate' else ('captured',)
        if metadata.get('status') not in allowed_stages or not baseline.files[f'{base}/capture.md'].strip(): raise ValueError()
    except (KeyError,ValueError): raise service.ChatError(2604,f"{spec['kind_cn']}需处于采集池且 capture、trace 完整",409)
    parent=(service.conversation(db,actor,conversation_id) if conversation_id
            else _latest_object_conversation(db,actor,space_id,repository_id,object_id))
    if conversation_id:
        primary=db.scalar(select(chat_relations.c.object_id).where(
            chat_relations.c.conversation_id==conversation_id,chat_relations.c.role=='primary'))
        if (parent['space_id']!=space_id or parent['repository_id']!=repository_id
                or primary!=object_id or parent['archived']):
            raise service.ChatError(2604,'生成命令必须匹配当前会话主对象',409)
    reused=bool(parent)
    from app.governance.execution_context import reconcile, visible_state
    reconcile(db, actor, project)
    state = visible_state(db, actor, project, object_id)
    if not state['can_send'] or (parent and parent['active_turn_id']):
        cid = state.get('view_conversation_id') if not state['can_send'] else parent['id']
        db.commit()
        return {'preparation_id': None, 'conversation_id': cid, 'object_id': object_id,
                'prompt': '', 'state': 'busy', 'reused_conversation': bool(cid),
                'execution_state': state['execution_state'] if not state['can_send'] else 'running',
                'can_send': False, 'reason_code': state.get('reason_code') or 'object_running',
                'view_conversation_id': cid}
    if not parent:
        parent=service.create_conversation(db,actor,space_id,repository_id,f"{object_id} · {spec['title']}")
        relations.set_relations(db,actor,parent['id'],object_id,[])
    row={**_candidate_id(actor,project.key,object_id,action,idempotency_key),'actor_id':actor,'space_id':space_id,'repository_id':repository_id,
         'scope_key':project.key,'conversation_id':parent['id'],'object_id':object_id,'action':action,
         'binding_revision':project.binding_revision,'baseline_hash':baseline.revision,'state':'prepared','revision':1}
    existing=db.execute(select(candidates).where(candidates.c.id==row['id'])).mappings().first()
    if existing:
        db.commit()
        return {'preparation_id':existing['id'],'conversation_id':existing['conversation_id'],'object_id':existing['object_id'],
                'prompt':display_prompt(existing['action'],existing['object_id']),'state':existing['state'],
                'reused_conversation': True}
    store.write(row['id'],'baseline',{'files':{name:body.decode() for name,body in baseline.files.items()},'base_path':base,
        'candidate_revision':row['revision']})
    try:
        db.execute(insert(candidates).values(**row))
    except IntegrityError:
        db.rollback()
        existing=db.execute(select(candidates).where(candidates.c.id==row['id'])).mappings().one()
        return {'preparation_id':existing['id'],'conversation_id':existing['conversation_id'],'object_id':existing['object_id'],
                'prompt':display_prompt(existing['action'],existing['object_id']),'state':existing['state'],
                'reused_conversation': True}
    from app.governance.observability import trace
    trace(db,row['id'],'prepared',actor=actor,request_id=request_id,
        metadata={'object_id':object_id,'action_type':action,'conversation_id':parent['id'],'candidate_id':row['id'],
            'result':'reused_conversation' if reused else 'new_conversation'})
    db.commit()
    return {'preparation_id':row['id'],'conversation_id':parent['id'],'object_id':object_id,
            'prompt':display_prompt(action,object_id),'state':'prepared','reused_conversation':reused}


def prepare_object_session(db,actor,space_id,repository_id,object_id,action='open-chat',request_id=None,idempotency_key=None):
    action=_action_name(action)
    if action not in READ_ONLY_OBJECT_ACTIONS | ISSUE_ACTION_RULES.keys() | ISSUE_ACTION_FALLBACKS.keys() | {'req-generate','bug-generate','sprint-archive'}:
        raise service.ChatError(2604,'该治理命令尚未接入产品链路',422,kind='governance_validation_failed')
    project=scope.authorize(db,actor,space_id,repository_id,write=action not in READ_ONLY_OBJECT_ACTIONS)
    from app.governance.execution_context import reconcile, visible_state
    if action not in READ_ONLY_OBJECT_ACTIONS:
        _object_session_snapshot(db, actor, project)
    try:
        resolved = relations.resolve_object(db, actor, space_id, repository_id, object_id)
    except service.ChatError:
        # Preserve the write preflight's actionable fact-source errors. Busy
        # objects still bypass action-stage validation once identity resolves.
        if action not in READ_ONLY_OBJECT_ACTIONS:
            _preflight_object_session(db, actor, project, object_id, action)
        raise
    object_id = resolved['id']
    from app.governance.read_snapshot import stable_read
    # Opening is read admission only. Final write admission and recovery run
    # against fresh facts when the user actually submits a command.
    if action != 'open-chat':
        reconcile(db, actor, project,
                  snapshot_loader=lambda: stable_read(project.root, project.binding_revision, parallel_cold=True))
    if object_id.startswith('sprint-') and action != 'open-chat':
        from app.governance.execution_context import reconcile_external
        sprint_snapshot = ProjectReader(db, actor, project).snapshot()
        stage = 'done' if f'iterations/archive/{object_id}/sprint.yaml' in sprint_snapshot.files else 'sprint-planning'
        reconcile_external(db, project, object_id, stage, sprint_snapshot, actor=actor)
    state = visible_state(db, actor, project, object_id)
    if not state['can_send']:
        from app.governance.observability import trace
        trace(db, request_id or str(uuid4()), 'conflict', actor=actor, request_id=request_id, serialize_sqlite=True,
              metadata={'object_id': object_id, 'action_type': action,
                        'result': state.get('reason_code') or 'object_busy'})
        db.commit()
        return {'conversation_id': state.get('view_conversation_id'),
                'object_id': object_id, 'action': action,
                'reused_conversation': bool(state.get('view_conversation_id')), **state}
    item=_preflight_object_session(db,actor,project,object_id,action)
    object_id=item['id']
    parent=_latest_object_conversation(db,actor,space_id,repository_id,object_id)
    reused=bool(parent)
    if not parent and object_id.startswith('sprint-'):
        parent = _create_sprint_conversation(db, actor, project, item)
    if not parent:
        token = str(uuid5(NAMESPACE_URL, f'moonbox.object-session.v1:{actor}:{project.key}:{object_id}:{idempotency_key}')) if idempotency_key else None
        parent=service.create_conversation(db,actor,space_id,repository_id,f"{object_id} · {item['title']}",client_request_id=token)
        relations.set_relations(db,actor,parent['id'],object_id,[])
    from app.governance.observability import trace
    trace(db,parent['id'],'prepared',actor=actor,request_id=request_id,serialize_sqlite=True,
        metadata={'object_id':object_id,'action_type':action,'conversation_id':parent['id'],
            'result':'reused_conversation' if reused else 'new_conversation'})
    db.commit()
    return {'conversation_id':parent['id'],'object_id':object_id,'object_type':'REQ' if object_id.startswith('REQ-') else 'BUG' if object_id.startswith('BUG-') else 'SPRINT' if object_id.startswith('sprint-') else 'CHANGE',
            'title':item['title'],'action':action,'reused_conversation':reused,
            'execution_state':'running' if parent['active_turn_id'] else 'idle',
            'can_send':not bool(parent['active_turn_id']),
            'reason_code':'object_running' if parent['active_turn_id'] else None,
            'view_conversation_id':parent['id'] if parent['active_turn_id'] else None}


def _create_sprint_conversation(db, actor, project, item):
    # The object epoch, not the click key, arbitrates simultaneous preparations.
    latest = db.execute(select(conversations).join(chat_relations,
        chat_relations.c.conversation_id == conversations.c.id).where(
        conversations.c.owner_id == actor, conversations.c.space_id == project.space_id,
        conversations.c.repository_id == project.repository_id,
        chat_relations.c.object_id == item['id'], chat_relations.c.role == 'primary')
        .order_by(conversations.c.created_at.desc(), conversations.c.id.desc()).limit(1)).mappings().first()
    if latest and not latest['archived'] and not latest['deleted_at']:
        return dict(latest)
    latest_id = latest['id'] if latest else 'initial'
    cid = str(uuid5(NAMESPACE_URL, f'moonbox.sprint-session.v1:{actor}:{project.key}:{item["id"]}:{latest_id}'))
    row = {**service.identity(), 'id': cid, 'owner_id': actor,
           'space_id': project.space_id, 'repository_id': project.repository_id,
           'branch_name': service.normalize_branch(project.repository_id, project.space_id),
           'title': item['id'] + ' · ' + item['title'], 'pinned': 0, 'archived': 0,
           'active_turn_id': None, 'generation': 0}
    try:
        db.execute(insert(conversations).values(**row))
        db.execute(insert(chat_relations).values(conversation_id=cid, object_id=item['id'],
                                               title=item['title'], role='primary'))
        db.commit()
        return row
    except IntegrityError:
        db.rollback()
        parent = _latest_object_conversation(db, actor, project.space_id, project.repository_id, item['id'])
        if parent:
            return parent
        raise service.ChatError(2604, '会话状态已变化，请重试', 409) from None


def for_conversation(db,cid):
    return db.execute(select(candidates).where(candidates.c.conversation_id==cid)
        .order_by(candidates.c.created_at.desc(),candidates.c.id.desc())).mappings().first()


def prepare_send(db, actor, parent, prompt, client_id, request_id=None):
    """Final write checks; a fast-open response never grants execution rights."""
    command = bound_write_command(db, actor, parent, prompt)
    if not command:
        return parent
    action, object_id = command
    project = scope.authorize(db, actor, parent['space_id'], parent['repository_id'], write=True)
    from app.governance.execution_context import reconcile, visible_state
    reconcile(db, actor, project)
    resolved = relations.resolve_object(db, actor, parent['space_id'], parent['repository_id'], object_id)
    state = visible_state(db, actor, project, resolved['id'])
    if not state['can_send']:
        raise service.ChatError(2504, '对象正在执行或结果待核对，请查看原执行', 409,
                                kind=state.get('reason_code') or 'object_busy')
    parent = service.conversation(db, actor, parent['id'])
    if parent['archived'] or parent['active_turn_id']:
        raise service.ChatError(2504, '会话只读或原运行尚未终止', 409)
    if action in ('req-generate', 'bug-generate'):
        candidate = _current_prepared_candidate(db, parent['id'])
        if candidate and (candidate['object_id'] != resolved['id'] or candidate['action'] != action):
            raise service.ChatError(2604, '当前会话存在其他待发送治理动作，请先处理原动作', 409)
        if not candidate:
            result = prepare(db, actor, parent['space_id'], parent['repository_id'], resolved['id'],
                             action=action, request_id=request_id, idempotency_key=client_id,
                             conversation_id=parent['id'])
            if result.get('can_send') is False or result.get('conversation_id') != parent['id']:
                raise service.ChatError(2504, '对象状态已变化，请查看原执行', 409)
    return parent


def check_send(db,actor,parent):
    row=_current_prepared_candidate(db,parent['id'])
    if not row: return None
    project=scope.authorize(db,actor,row['space_id'],row['repository_id'],write=True)
    if project.binding_revision!=row['binding_revision'] or stable(project.root).revision!=row['baseline_hash']:
        raise service.ChatError(2606,'项目文件已变化，请重新准备治理动作',409,
            kind='workspace_fact_source_stale')
    from app.chat.isolated import allowed
    if not allowed(db,actor,row['space_id'],row['repository_id']):
        db.execute(update(candidates).where(candidates.c.id==row['id']).values(error_code='executor_unavailable',updated_at=service.now()))
        db.commit()
        raise service.ChatError(2505,'执行器 sandbox/dry-run 预检未通过，暂不能生成文档，请稍后重试',503,kind='executor_unavailable')
    return row


def execution_prompt_for_turn(db,parent,stored_prompt):
    command = _write_command(stored_prompt)
    primary = db.scalar(select(chat_relations.c.object_id).where(chat_relations.c.conversation_id == parent['id'], chat_relations.c.role == 'primary')) if command and command[0] in CHANGE_ACTION_STATUSES else None
    if command and command[0] in CHANGE_ACTION_STATUSES and command[1].startswith(('REQ-', 'BUG-')) and primary and not primary.startswith(('REQ-', 'BUG-', 'sprint-')) and parent.get('active_turn_id'):
        turn = db.execute(select(turns).where(turns.c.id == parent['active_turn_id'])).mappings().first()
        if turn:
            baseline = store.read(_command_baseline_id(parent['id'], turn['client_request_id']), 'baseline')
            source_id = baseline.get('source_issue_id')
            if source_id:
                effective = bound_write_command(db, parent['owner_id'], parent, stored_prompt)
                if effective != (baseline['action'], baseline['object_id']) or command[1] != source_id:
                    raise service.ChatError(2604, '交付执行上下文已变化', 409, kind='delivery_target_mismatch')
                # Use the already-supported explicit Change command internally;
                # no new CLI flag and no sibling selection delegated to the model.
                suffix = (stored_prompt or '').strip().split(None, 2)
                detail = ' ' + suffix[2] if len(suffix) > 2 else ''
                return f"/{baseline['action']} {baseline['object_id']}{detail}\n\n来源命令：/{baseline['action']} {source_id}。" \
                    f"服务端已绑定交付目标 {baseline['object_id']}；仅处理此 Change，保留来源 Issue 完整身份，不操作兄弟 Change。"
    if re.fullmatch(r'/sprint-archive\s+sprint-\d{3}', (stored_prompt or '').strip()):
        return stored_prompt + '\n\n执行约束：遵循 sprint-archive 技能，重新检查完整范围、权限、验收签署和文档门禁。' \
            '不得代替用户签署，不得使用 --force；已归档 Change 只核验，不重复合并。' \
            '完成后运行标准 sync-workflow-status.py --event sprint.archive --sprint 加本次 Sprint ID，' \
            '等待结构化同步成功；检查或同步失败时保留原成果并如实报告，不宣称成功。'
    if re.fullmatch(r'/opsx-archive\s+(?:REQ|BUG)-\d{4}-[A-Za-z0-9_-]+', (stored_prompt or '').strip()):
        return stored_prompt + '\n\n归档执行约束：解析真实 Change ID 后，优先运行 bash scripts/archive-change.sh CHANGE_ID --finalize。' \
            '目录迁移禁止使用 Path.rename；跨挂载必须使用 shutil.move 或经过校验的 copy+remove。' \
            '若 active 目录已不存在且唯一 archive 目录存在，重跑同一脚本恢复，不重复合并规格。' \
            '必须等待命令完成事件并检查退出码；验证通过后串行完成 Workflow Sync、Issue promote 和 AI Usage hook，最后输出归档结果。' \
            'CLI 不可用时仅允许按技能自检并合并 delta 后用 shutil.move 迁移，再运行标准脚本完成验证和同步；验收未通过时明确报告阻塞。'
    row=_candidate_for_turn(db,parent['id'],parent.get('active_turn_id')) or _current_prepared_candidate(db,parent['id'])
    if not row: return stored_prompt
    visible=display_prompt(row['action'],row['object_id'])
    if (stored_prompt or '').strip()!=visible: return stored_prompt
    return execution_prompt(row['action'],row['object_id'])


def bind_prepared_turn(db,cid,turn_id):
    row=_current_prepared_candidate(db,cid)
    if not row: return None
    return bind_candidate_turn(db,row['id'],turn_id)


def bind_candidate_turn(db,candidate_id,turn_id):
    row=db.execute(select(candidates).where(candidates.c.id==candidate_id)).mappings().first()
    if not row: return None
    db.execute(update(candidates).where(candidates.c.id==row['id'],candidates.c.state=='prepared',
        candidates.c.prepared_turn_id.is_(None)).values(prepared_turn_id=turn_id,updated_at=service.now()))
    from app.governance.recovery_schema import operations
    db.execute(update(operations).where(operations.c.candidate_id == candidate_id,
        operations.c.origin_turn_id.is_(None)).values(origin_turn_id=turn_id, stage='generation',
            version=operations.c.version + 1, updated_at=service.now()))
    return row


def _write_command(prompt):
    parts=(prompt or '').split()
    if not parts or not parts[0].startswith('/'):
        return None
    action=parts[0][1:]
    if action == 'sprint-archive' and (len(parts) != 2 or not re.fullmatch(r'sprint-\d{3}', parts[1])):
        raise service.ChatError(2604, '请使用完整的 /sprint-archive sprint-xxx 命令', 422)
    if action not in {*ISSUE_ACTION_RULES,*ISSUE_ACTION_FALLBACKS,'req-generate','bug-generate','sprint-archive'}:
        return None
    args=[part for part in parts[1:] if part not in ('--req','--bug','--change')]
    if not args:
        raise service.ChatError(2604,'治理命令缺少对象标识',422,kind='governance_validation_failed')
    return action,args[0]


def _command_baseline_id(cid,client_id):
    return str(uuid5(NAMESPACE_URL,f'moonbox.command-baseline.v1:{cid}:{client_id}'))


def bound_write_command(db, actor, parent, prompt):
    """Resolve a source command only through the authorized primary delivery.

    The visible command retains its Issue identity. The durable command journal,
    guards and workspace baseline use the explicit primary Change identity.
    """
    command = _write_command(prompt)
    if not command or command[0] not in CHANGE_ACTION_STATUSES:
        return command
    primary = db.scalar(select(chat_relations.c.object_id).where(
        chat_relations.c.conversation_id == parent['id'], chat_relations.c.role == 'primary'))
    if not primary or primary.startswith(('REQ-', 'BUG-', 'sprint-')):
        return command
    action, source_id = command
    if not source_id.startswith(('REQ-', 'BUG-')):
        if source_id != primary:
            raise service.ChatError(2604, '命令与会话交付目标不一致', 409, kind='delivery_target_mismatch')
        return command
    project = scope.authorize(db, actor, parent['space_id'], parent['repository_id'], write=True)
    reader, snapshot = _object_session_snapshot(db, actor, project)
    reader.authorize_object(snapshot, primary, change=True, write=True)
    reader.authorize_object(snapshot, source_id, write=True)
    from app.governance.snapshot import materialize
    from app.services.requirement_center import using_governance_root
    with materialize(snapshot) as root, using_governance_root(root):
        _require_issue_fact_source(snapshot, source_id, action, root, target_change_id=primary)
    return action, primary


def assert_delivery_replay_identity(db, parent, turn):
    """Returning a prior receipt must not present A as the current target B."""
    command = _write_command(turn['prompt'])
    if not command or command[0] not in CHANGE_ACTION_STATUSES:
        return
    primary = db.scalar(select(chat_relations.c.object_id).where(chat_relations.c.conversation_id == parent['id'], chat_relations.c.role == 'primary'))
    try:
        baseline = store.read(_command_baseline_id(parent['id'], turn['client_request_id']), 'baseline')
    except (OSError, ValueError):
        if primary and not primary.startswith(('REQ-', 'BUG-', 'sprint-')) and command[1].startswith(('REQ-', 'BUG-')):
            raise service.ChatError(2604, '原交付执行上下文缺失', 409, kind='delivery_target_required') from None
        return
    if baseline.get('source_issue_id') and (primary != baseline['object_id'] or command[1] != baseline['source_issue_id']):
        raise service.ChatError(2604, '原执行与当前交付目标不一致', 409, kind='delivery_target_mismatch')


def _send_baseline(db, actor, parent, object_id, action):
    """Retry only read-side races, before creating any durable command record."""
    last_reason = 'concurrent_update'
    for attempt in range(3):
        project = scope.authorize(db, actor, parent['space_id'], parent['repository_id'], write=True)
        try:
            item = _preflight_object_session(db, actor, project, object_id, action)
            reader = ProjectReader(db, actor, project)
            baseline = reader.snapshot()
            if item['version'] == baseline.revision:
                return project, item, reader, baseline
            last_reason = 'concurrent_update'
        except service.ChatError as exc:
            if exc.kind == 'workspace_fact_source_stale' and exc.details.get('reason') == 'manifest_mismatch':
                last_reason = 'manifest_mismatch'
            elif exc.kind == 'source_changing':
                last_reason = 'concurrent_update'
            else:
                raise
    message = ('治理目录与源工作区持续不一致，请同步事实源后重试。'
               if last_reason == 'manifest_mismatch' else
               '治理文件持续更新，自动重试后仍未稳定；请等待当前修改完成后重试。')
    raise service.ChatError(2606, message, 409, kind='workspace_fact_source_stale',
                            details={'reason': last_reason, 'phase': 'send_preflight', 'attempts': 3})


def prepare_command_snapshot(db,actor,parent,prompt,client_id):
    command=bound_write_command(db,actor,parent,prompt)
    if not command:
        return
    action,object_id=command
    project=scope.authorize(db,actor,parent['space_id'],parent['repository_id'],write=True)
    from app.governance.recovery_service import prepare_explicit_regeneration
    prepare_explicit_regeneration(db, actor, parent, project, action, object_id, client_id)
    prepared = _current_prepared_candidate(db, parent['id'])
    project, item, reader, baseline = _send_baseline(db, actor, parent, object_id, action)
    if action == 'sprint-archive':
        primary = db.scalar(select(chat_relations.c.object_id).where(chat_relations.c.conversation_id == parent['id'], chat_relations.c.role == 'primary'))
        if primary != item['id']:
            raise service.ChatError(2604, '归档命令必须匹配当前 Sprint 主对象', 409)
        from app.governance.sprint_object import require_final
        from .controlled_successor import authority
        with authority(db, project, actor):
            require_final(project.root, item['id'])
    if any(not scope.visible(db,actor,project,entry['id']) for entry in reader.entries(baseline)):
        raise service.ChatError(2601,'当前权限不足以准备完整项目治理上下文',403)
    rid = _command_baseline_id(parent['id'], client_id)
    expected = {
        'action': action, 'object_id': item['id'], 'revision': baseline.revision,
        'binding_revision': project.binding_revision,
        'files': {name: body.decode() for name, body in baseline.files.items()},
    }
    visible_command = _write_command(prompt)
    if visible_command and visible_command[1] != item['id']:
        expected['source_issue_id'] = visible_command[1]
    try:
        if (store.root() / rid).exists():
            # A failed enqueue can leave durable evidence without a DB turn.
            # Never replace its baseline when the same request is retried.
            _check_command_record(parent['id'], client_id, action, item['id'], baseline.revision)
            if store.read(rid, 'baseline') != expected:
                raise service.ChatError(2606, '治理基准已变化，保留原操作记录', 409,
                    kind='direct_command_identity_mismatch', details={'phase': 'preparation'})
        else:
            store.write(rid, 'baseline', expected)
            from app.governance.direct_command_journal import prepare as prepare_direct_journal
            prepare_direct_journal(parent['id'], client_id, action, item['id'], baseline.revision)
            _check_command_record(parent['id'], client_id, action, item['id'], baseline.revision)
    except (OSError, ValueError):
        raise service.ChatError(2604, '治理操作记录准备失败，已保留现场', 409,
            kind='direct_command_preparation_failed', details={'phase': 'preparation'}) from None
    if not prepared and action in ('req-complete','bug-complete','req-review','bug-review'):
        from app.governance.completion_recovery import prepare_completion
        prepare_completion(db,actor,parent,project,item,baseline,client_id,action)
    if action in ('req-review', 'bug-review'):
        from app.governance.durable_recovery import create, fingerprint
        candidate = _current_prepared_candidate(db, parent['id'])
        create(db, actor=actor, project=project, parent=parent, action=action,
               object_id=item['id'], request_key=client_id,
               request_hash=fingerprint({'prompt': prompt, 'revision': baseline.revision}),
               source_hash=baseline.revision, candidate_id=candidate['id'] if candidate else None)


def _check_command_record(cid, client_id, action, object_id, revision):
    from app.governance.direct_command_journal import record_block_reason
    reason = record_block_reason(cid, client_id, action=action, object_id=object_id, revision=revision)
    if reason:
        raise service.ChatError(2604, '治理操作记录不完整，已保留成果，请核查原执行', 409,
                                kind=reason, details={'phase': 'preparation'})


def _initialize_command_workspace(db,parent,source,workspace):
    turn=db.execute(select(turns).where(turns.c.id==parent['active_turn_id'])).mappings().first()
    if not turn or not _write_command(turn['prompt']):
        return
    baseline=store.read(_command_baseline_id(parent['id'],turn['client_request_id']),'baseline')
    if baseline.get('source_issue_id'):
        effective = bound_write_command(db, parent['owner_id'], parent, turn['prompt'])
        if effective != (baseline['action'], baseline['object_id']) or _write_command(turn['prompt'])[1] != baseline['source_issue_id']:
            raise service.ChatError(2604, '交付恢复目标已变化', 409, kind='delivery_target_mismatch')
    project=scope.authorize(db,parent['owner_id'],parent['space_id'],parent['repository_id'],write=True)
    _preflight_object_session(db,parent['owner_id'],project,baseline['object_id'],baseline['action'])
    reader=ProjectReader(db,parent['owner_id'],project)
    if any(not scope.visible(db,parent['owner_id'],project,entry['id']) for entry in reader.entries(reader.snapshot())):
        raise service.ChatError(2601,'当前权限不足以准备完整项目治理上下文',403)
    if (project.binding_revision!=baseline['binding_revision'] or
        stable(project.root).revision!=baseline['revision'] or stable(source).revision!=baseline['revision']):
        raise service.ChatError(2606,'治理文件版本已变化，请重新发送命令',409,kind='workspace_fact_source_stale')
    if _real_source_workspace(project, source, workspace):
        return
    if git(workspace,'status','--porcelain').strip():
        _checkpoint_applied_workspace(db,parent,workspace)
    from app.chat.relations import _read_file
    control=f".agents/skills/{baseline['action']}/SKILL.md"
    skill=_read_file(source,control)
    controls = {control: skill}
    if baseline['action'] in ('req-review', 'bug-review'):
        names = ['scripts/promote-issue-stage.py', 'scripts/sync-workflow-status.py',
                 '.agents/skills/workflow-sync/SKILL.md', 'scripts/validate-document-titles.py',
                 'src/backend/app/governance/titles.py', 'src/backend/app/governance/lifecycle.py']
        names += [str(path.relative_to(source)) for path in (source/'scripts/workflow_sync').glob('*.py')]
        controls.update({name: _read_file(source, name) for name in names})
        if controls != {name: _read_file(source, name) for name in controls}:
            raise service.ChatError(2606,'治理控制文件正在变化，请重新准备',409)
    import shutil
    for folder in GOVERNANCE_FACT_ROOTS:
        target=workspace/folder
        if target.is_symlink():
            raise service.ChatError(2604,'工作区路径不安全',409)
        if target.exists(): shutil.rmtree(target)
    for relative,body in {**baseline['files'],**controls}.items():
        from app.chat.workspace import trusted_directory
        target=workspace/relative
        for ancestor in (target,*target.parents):
            if ancestor==workspace: break
            if ancestor.is_symlink(): raise service.ChatError(2604,'工作区路径不安全',409)
        target.parent.mkdir(parents=True,exist_ok=True)
        trusted_directory(target.parent)
        target.write_text(body)
    if stable(workspace).revision!=baseline['revision'] or stable(source).revision!=baseline['revision']:
        raise service.ChatError(2606,'同步期间治理文件版本变化，请重新发送命令',409,kind='workspace_fact_source_stale')
    git(workspace,'add','--',*controls,*[name for name in GOVERNANCE_FACT_ROOTS if (workspace/name).exists()])
    git(workspace,'-c','user.name=MoonBox','-c','user.email=moonbox@invalid','commit','--allow-empty','-m','治理命令当前事实源基准')


def _applied_workspace_result(db,parent,workspace):
    # Only checkpoint the exact result already applied by the controller.
    previous=db.execute(select(candidates).where(candidates.c.conversation_id==parent['id'],
        candidates.c.state=='applied').order_by(candidates.c.updated_at.desc()).limit(1)).mappings().first()
    if previous:
        baseline=store.read(previous['id'],'baseline');result=store.read(previous['id'],'result')
        expected=dict(baseline['workspace_manifest'])
        for name,body in result['after'].items():
            if body is None:
                expected.pop(name,None)
                continue
            expected[name]={'kind':'file','sha256':hashlib.sha256(body.encode()).hexdigest(),
                            'executable':expected.get(name,{}).get('executable',False)}
        actual={name:{key:value for key,value in item.items() if key in ('kind','sha256','executable')}
                for name,item in code_snapshot(workspace)['files'].items()}
        if actual==expected:
            return result
    raise service.ChatError(2604,'会话工作区存在未应用成果，不能覆盖',409,kind='workspace_unapplied_changes')


def _checkpoint_applied_workspace(db,parent,workspace):
    result=_applied_workspace_result(db,parent,workspace)
    git(workspace,'-c','core.hooksPath=/dev/null','add','--',*result['after'])
    git(workspace,'-c','core.hooksPath=/dev/null','-c','user.name=MoonBox','-c','user.email=moonbox@invalid','commit','--only','--allow-empty','-m','已应用治理成果基准','--',*result['after'])


def initialize_workspace(db,parent,source,workspace):
    turn = db.execute(select(turns).where(turns.c.id == parent['active_turn_id'])).mappings().first()
    command = _write_command(turn['prompt']) if turn else None
    if command:
        _check_command_record(parent['id'], turn['client_request_id'], command[0], None, None)
        from app.governance.recovery_capabilities import require as require_capabilities
        require_capabilities(command[0])
        if command[0] in ('req-review', 'bug-review'):
            from app.governance.recovery_schema import operations
            operation = db.execute(select(operations).where(operations.c.origin_turn_id == parent['active_turn_id'])).mappings().first()
            if (not operation or operation['schema_version'] != 1 or operation['action'] != command[0]
                    or operation['conversation_id'] != parent['id'] or not operation['candidate_id']):
                raise service.ChatError(2604, '治理持久化记录不完整，生成未开始', 409,
                                        kind='recovery_operation_incomplete')
    row=_current_workspace_candidate(db,parent['id'],parent['active_turn_id'])
    if not row:
        return _initialize_command_workspace(db,parent,source,workspace)
    if row['state']!='prepared': raise service.ChatError(2604,'治理基准不可重复覆盖',409)
    project=scope.authorize(db,parent['owner_id'],row['space_id'],row['repository_id'],write=True)
    if command and command[0] in ('req-review', 'bug-review'):
        if (operation['candidate_id'] != row['id'] or operation['object_id'] != row['object_id']
                or operation['binding_revision'] != project.binding_revision
                or operation['source_hash'] != row['baseline_hash']
                or operation['request_key'] != turn['client_request_id']):
            raise service.ChatError(2604, '治理持久化身份或绑定不匹配，生成未开始', 409,
                                    kind='recovery_operation_incomplete')
    baseline=store.read(row['id'],'baseline')
    if stable(project.root).revision!=row['baseline_hash'] or stable(source).revision!=row['baseline_hash']:
        raise service.ChatError(2606,'源仓库与治理目录不一致或基准已过期',409,
            kind='workspace_fact_source_stale')
    if row['action'] in ('req-complete','bug-complete','req-review','bug-review') and not _real_source_workspace(project, source, workspace):
        if baseline.get('recovery_hash'):
            if code_snapshot(workspace)['hash']!=baseline['recovery_hash']:
                raise service.ChatError(2606,'保留成果在续接前已变化，请重新准备',409,kind='workspace_fact_source_stale')
        else:
            _initialize_command_workspace(db,parent,source,workspace)
            before=code_snapshot(workspace)
            baseline['workspace_manifest']={name:{k:v for k,v in item.items() if k in ('kind','sha256','executable')} for name,item in before['files'].items()}
        store.write(row['id'],'baseline',baseline)
        db.execute(update(candidates).where(candidates.c.id==row['id'],candidates.c.state=='prepared').values(state='running',updated_at=service.now()))
        db.commit()
        return
    if _real_source_workspace(project, source, workspace):
        before=code_snapshot(workspace)
        baseline['workspace_manifest']={name:{k:v for k,v in item.items() if k in ('kind','sha256','executable')} for name,item in before['files'].items()}
        baseline['code_revision']=git(source,'rev-parse','HEAD').decode().strip()
        baseline['workspace_mode']='source'
        store.write(row['id'],'baseline',baseline)
        db.execute(update(candidates).where(candidates.c.id==row['id'],candidates.c.state=='prepared').values(state='running',updated_at=service.now()))
        from app.governance.observability import trace
        trace(db,row['id'],'running',actor=parent['owner_id'],
            metadata={'object_id':row['object_id'],'action_type':row['action'],'conversation_id':parent['id'],
                'turn_id':row['prepared_turn_id'],'candidate_id':row['id'],'workspace_mode':'source'})
        db.commit()
        return
    if git(workspace,'status','--porcelain').strip(): raise service.ChatError(2604,'工作区已有修改，拒绝覆盖',409,kind='workspace_unapplied_changes')
    # Explicit control-file whitelist: current working-tree skills and sync implementation,
    # read without following links. Never bring in local env/auth/runtime files.
    from app.chat.relations import _read_file
    row_action=row['action'];spec=action_spec(row_action)
    control_names=['AGENTS.md','openspec/project.md',f".agents/skills/{row_action}/SKILL.md",
        '.agents/skills/workflow-sync/SKILL.md','scripts/sync-workflow-status.py','scripts/ai_usage.py',
        'scripts/validate-document-titles.py','src/backend/app/governance/titles.py']
    control_names += [str(path.relative_to(source)) for path in (source/'scripts/workflow_sync').glob('*.py')]
    controls={name:_read_file(source,name) for name in sorted(control_names)}
    if controls!={name:_read_file(source,name) for name in controls}:
        raise service.ChatError(2606,'治理控制文件正在变化，请重新准备',409)
    # New clean workspace only. Overlay the stable uncommitted governance tree.
    for folder in ('issues','iterations','openspec','docs','rules'):
        import shutil
        target=workspace/folder
        if target.exists(): shutil.rmtree(target)
    for relative,body in baseline['files'].items():
        target=workspace/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(body)
    for relative,body in controls.items():
        target=workspace/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(body)
    baseline['control_manifest']={name:hashlib.sha256(body.encode()).hexdigest() for name,body in controls.items()}
    git(workspace,'add','--',*controls.keys())
    git(workspace,'add','--',*[name for name in ('issues','iterations','openspec','docs','rules') if (workspace/name).exists()])
    git(workspace,'-c','user.name=MoonBox','-c','user.email=moonbox@invalid','commit','--allow-empty','-m','治理动作隔离基准')
    before=code_snapshot(workspace)
    baseline['workspace_manifest']={name:{k:v for k,v in item.items() if k in ('kind','sha256','executable')} for name,item in before['files'].items()}
    baseline['code_revision']=git(source,'rev-parse','HEAD').decode().strip()
    store.write(row['id'],'baseline',baseline)
    db.execute(update(candidates).where(candidates.c.id==row['id'],candidates.c.state=='prepared').values(state='running',updated_at=service.now()))
    from app.governance.observability import trace
    trace(db,row['id'],'running',actor=parent['owner_id'],
        metadata={'object_id':row['object_id'],'action_type':row['action'],'conversation_id':parent['id'],
            'turn_id':row['prepared_turn_id'],'candidate_id':row['id']})
    db.commit()


def _verify_source_workflow_sync(project, action, object_id, expected):
    """A source-mode candidate is complete only when the formal sync has no drift."""
    from app.governance.snapshot import read_once
    from app.governance.writer import project_lock
    event={
        'req-generate':'req.generate', 'bug-generate':'bug.generate',
        'req-complete':'req.complete', 'bug-complete':'bug.complete',
        'req-review':'req.review', 'bug-review':'bug.review',
    }[action]
    flag='--req' if object_id.startswith('REQ-') else '--bug'
    source=getattr(project, 'source_root', None) or project.root
    script=source/'scripts'/'sync-workflow-status.py'
    with project_lock(project):
        if read_once(project.root)!=expected or read_once(source)!=expected:
            raise service.ChatError(2606,'治理事实源已变化，无法确认候选成果',409,kind='workspace_fact_source_stale')
        if not script.is_file():
            raise service.ChatError(2604,'Workflow Sync 校验不可用，成果未确认',409,kind='governance_validation_failed')
        try:
            result=subprocess.run([sys.executable,str(script),'--event',event,flag,object_id,'--sprint','auto','--check'],
                cwd=source,capture_output=True,timeout=120)
        except (OSError,subprocess.TimeoutExpired):
            raise service.ChatError(2604,'Workflow Sync 校验失败，成果未确认',409,kind='governance_validation_failed') from None
        if result.returncode or read_once(project.root)!=expected or read_once(source)!=expected:
            raise service.ChatError(2604,'Workflow Sync 校验失败，成果未确认',409,kind='governance_validation_failed')

    from app.governance.snapshot import digest
    return {'event':event,'object_id':object_id,'source_hash':digest(expected)}


def collect(db,parent,turn_id,workspace,terminal):
    row=_current_workspace_candidate(db,parent['id'],turn_id)
    if not row: return
    if row['state']!='running': return
    baseline = None
    current = None
    try:
        actual=db.execute(select(turns).where(turns.c.id==turn_id,turns.c.conversation_id==parent['id'])).mappings().one()
        if terminal not in ('completed','failed','stopped') or actual['status'] != terminal:
            # An unknown/stale notification is not permission to validate or
            # restore source files: the executor may still be writing them.
            # Keep the candidate for authoritative terminal recovery.
            return
        baseline=store.read(row['id'],'baseline');before={n:b.encode() for n,b in baseline['files'].items()}
        if row['revision']!=baseline.get('candidate_revision',1):
            raise service.ChatError(2606,'候选版本已变化，成果未确认',409,kind='workspace_fact_source_stale')
        # A failed/stopped executor can leave valid governed output. Validate
        # the exact artifacts and sync before recovering; keep its turn status.
        current=code_snapshot(workspace,text_bytes=1024*1024,max_text_bytes=32*1024*1024)
        old=baseline['workspace_manifest']
        changed={n for n in old.keys()|current['files'].keys() if old.get(n)!={k:v for k,v in current['files'].get(n,{}).items() if k in ('kind','sha256','executable')}}
        after=dict(before)
        for name in changed:
            item=current['files'].get(name)
            if item is None: after.pop(name,None)
            elif item['kind']!='file' or item['text'] is None: raise service.ChatError(2604,'成果包含不可应用文件',409)
            else: after[name]=item['text'].encode()
        observed = after
        if row['action'] in ('req-review', 'bug-review'):
            from app.governance.review_finalization import finalize_review
            after = finalize_review(before, observed, row['object_id'], baseline['base_path'], row['action'])
        result=validate(before,after,row['object_id'],baseline['base_path'],row['action'])
        # Include non-governance changes in the rejection: never discard a forbidden delta.
        repaired = {name for name in after if after.get(name) != observed.get(name)}
        if changed | repaired != {file['path'] for file in result['files']}: raise service.ChatError(2604,'成果包含越界改动',409)
        if repaired or baseline.get('workspace_mode') == 'source':
            project=scope.authorize(db,parent['owner_id'],row['space_id'],row['repository_id'],write=True)
            if project.binding_revision != row['binding_revision'] or not scope.visible(db,parent['owner_id'],project,row['object_id']):
                raise service.ChatError(2604,'治理权限或项目绑定已变化',409)
            from app.governance.writer import project_lock, replace_file
            with project_lock(project):
                if code_snapshot(workspace)['hash'] != current['hash']:
                    raise service.ChatError(2606,'评审成果已变化，保留成果并阻断收尾',409)
                for name in sorted(repaired):
                    replace_file(workspace,name,observed[name],after[name],row['id'])
                verified=code_snapshot(workspace,text_bytes=1024*1024,max_text_bytes=32*1024*1024)
                expected = {name: {key: value for key, value in item.items() if key in ('kind','sha256','executable')}
                            for name, item in current['files'].items()}
                for name in repaired:
                    expected[name] = {**expected[name], 'sha256': hashlib.sha256(after[name]).hexdigest()}
                actual_files = {name: {key: value for key, value in item.items() if key in ('kind','sha256','executable')}
                                for name, item in verified['files'].items()}
                if actual_files != expected:
                    raise service.ChatError(2606,'评审收尾回读不一致，已保留成果',409)
        changed |= repaired
        result['after']={f['path']:after[f['path']].decode() if f['path'] in after else None for f in result['files']}
        store.write(row['id'],'result',result)
        if not changed:
            # A no-op is a verified read, never a fabricated write/application.
            project=scope.authorize(db,parent['owner_id'],row['space_id'],row['repository_id'],write=True)
            if project.binding_revision!=row['binding_revision'] or not scope.visible(db,parent['owner_id'],project,row['object_id']):
                raise service.ChatError(2604,'治理权限或项目绑定已变化',409)
            current_source=ProjectReader(db,parent['owner_id'],project).snapshot()
            if current_source.revision!=row['baseline_hash'] or current_source.files!=before:
                raise service.ChatError(2606,'事实源已变化，无法确认无需更新',409)
            db.execute(update(candidates).where(candidates.c.id==row['id']).values(turn_id=turn_id,state='unchanged',manifest_hash=result['manifest_hash'],error_code=None,updated_at=service.now()))
        elif baseline.get('workspace_mode') == 'source':
            sync_proof=_verify_source_workflow_sync(project,row['action'],row['object_id'],after)
            request={'candidate_id':row['id'],'manifest_hash':result['manifest_hash'],'revision':row['revision'],'workspace_mode':'source'}
            app={**service.identity(),'actor_id':parent['owner_id'],'space_id':row['space_id'],'repository_id':row['repository_id'],
                 'scope_key':row['scope_key'],'idempotency_key':hashlib.sha256(f"source-{row['id']}".encode()).hexdigest(),
                 'request_hash':hashlib.sha256(json.dumps(request,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
                 'candidate_id':row['id'],'state':'applied','phase':'verified','error_code':None}
            store.write(app['id'],'operation',{'workflow_sync':sync_proof,'workspace_mode':'source'})
            db.execute(insert(applications).values(**app))
            db.execute(update(candidates).where(candidates.c.id==row['id']).values(turn_id=turn_id,state='applied',manifest_hash=result['manifest_hash'],updated_at=service.now()))
            from app.governance.observability import trace as governance_trace
            governance_trace(db,app['id'],'applied',actor=parent['owner_id'],metadata={'candidate_id':row['id'],'workspace_mode':'source'})
        else:
            db.execute(update(candidates).where(candidates.c.id==row['id']).values(turn_id=turn_id,state='pending',manifest_hash=result['manifest_hash'],updated_at=service.now()))
            from app.governance.writer import apply_candidate
            try:
                if terminal != 'stopped' or row['action'] not in ('req-review', 'bug-review'):
                    apply_candidate(db,parent['owner_id'],row['id'],result['manifest_hash'],row['revision'],f"auto-{row['id']}",True)
            except service.ChatError as error:
                db.rollback()
                code='executor_unavailable' if error.status>=500 else 'governance_validation_failed'
                db.execute(update(candidates).where(candidates.c.id==row['id']).values(turn_id=turn_id,state='rejected',error_code=code,updated_at=service.now()))
    except (service.ChatError,ValueError,KeyError,OSError) as error:
        code=collect_error_code(db,turn_id,terminal)
        if baseline and baseline.get('workspace_mode') == 'source':
            try:
                _restore_rejected_source(db,parent,row,workspace,baseline,current)
            except (service.ChatError,ValueError,KeyError,OSError):
                code='source_recovery_blocked'
        if code!='source_recovery_blocked' and row['action'] in ('req-review','bug-review') and isinstance(error,service.ChatError):
            from app.governance.review import REVIEW_REASONS
            reason=(error.details or {}).get('reason')
            if reason in REVIEW_REASONS | {'document_format'}:
                code=f'review_{reason}'
        if code!='source_recovery_blocked' and row['action'] in ('req-complete','bug-complete') and isinstance(error,service.ChatError):
            from app.governance.requirement_completion import COMPLETION_REASONS
            reason=(error.details or {}).get('reason')
            if reason in COMPLETION_REASONS:
                code=f'completion_{reason}'
        db.execute(update(candidates).where(candidates.c.id==row['id']).values(turn_id=turn_id,state='rejected',error_code=code,updated_at=service.now()))
    from app.governance.observability import trace
    state=db.scalar(select(candidates.c.state).where(candidates.c.id==row['id']))
    error_code=db.scalar(select(candidates.c.error_code).where(candidates.c.id==row['id']))
    trace(db,row['id'],state,actor=parent['owner_id'],
        metadata={'object_id':row['object_id'],'action_type':row['action'],'conversation_id':parent['id'],
            'turn_id':turn_id,'candidate_id':row['id'],'result':state,'error_code':error_code})
    from app.governance.recovery_service import checkpoint
    checkpoint(db, row['id'], 'validation', terminal=terminal, terminal_at=actual['updated_at'])
    db.commit()


def _restore_rejected_source(db,parent,row,workspace,baseline,current):
    """Undo a rejected source-mode turn only while its observed files are unchanged."""
    if current is None:
        raise ValueError('unverified_source_observation')
    from app.governance.writer import project_lock, replace_file
    project=scope.authorize(db,parent['owner_id'],row['space_id'],row['repository_id'],write=True)
    if project.binding_revision!=row['binding_revision']:
        raise ValueError('binding_changed')
    before={name:body.encode() for name,body in baseline['files'].items()}
    with project_lock(project):
        observed=code_snapshot(workspace,text_bytes=1024*1024,max_text_bytes=32*1024*1024)
        if current is not None and observed['hash']!=current['hash']:
            raise ValueError('external_change')
        old=baseline['workspace_manifest']
        changed=sorted(name for name in old.keys()|observed['files'].keys()
                       if old.get(name)!={key:value for key,value in observed['files'].get(name,{}).items()
                                             if key in ('kind','sha256','executable')})
        if any(name.split('/',1)[0] not in GOVERNANCE_FACT_ROOTS for name in changed):
            raise ValueError('non_governance_change')
        for name in changed:
            item=observed['files'].get(name)
            if item is not None and (item['kind']!='file' or item['text'] is None):
                raise ValueError('unsafe_file')
        for name in changed:
            item=observed['files'].get(name)
            actual=item['text'].encode() if item else None
            replace_file(workspace,name,actual,before.get(name),row['id'],create_parents=name in before)
        if stable(workspace).files!=before:
            raise ValueError('restore_mismatch')


def collect_error_code(db,turn_id,terminal):
    original = db.scalar(select(turns.c.error_code).where(turns.c.id == turn_id))
    if original in {
        'direct_command_recovery_blocked', 'direct_command_preparation_failed', 'direct_command_operation_missing',
        'direct_command_operation_invalid', 'direct_command_identity_mismatch',
        'direct_command_baseline_missing', 'direct_command_baseline_invalid',
        'archive_recovery_blocked', 'sprint_source_invalid',
    }:
        return original
    if terminal!='completed':
        return 'executor_unavailable'
    content='\n'.join(row[0] for row in db.execute(select(messages.c.content).where(messages.c.turn_id==turn_id,messages.c.role=='assistant')).all() if row[0])
    if any(marker in content for marker in EXECUTOR_UNAVAILABLE_MARKERS):
        return 'executor_unavailable'
    return 'governance_validation_failed'


def list_candidates(db,actor,cid):
    service.conversation(db,actor,cid)
    rows=list(db.execute(select(candidates).where(candidates.c.conversation_id==cid)
        .order_by(candidates.c.created_at.desc(),candidates.c.id.desc())).mappings())
    items=[]
    for row in rows:
        project=scope.authorize(db,actor,row['space_id'],row['repository_id'])
        if not scope.visible(db,actor,project,row['object_id']): raise service.ChatError(2601,'对象不可访问',403)
        public={k:row[k] for k in ('id','object_id','action','state','manifest_hash','revision','error_code','turn_id','prepared_turn_id','created_at','updated_at')}
        from app.governance.recovery_schema import operations
        public['recovery_operation_id'] = db.scalar(select(operations.c.id).where(operations.c.candidate_id == row['id']))
        public['current']=row['state']=='prepared' and not row['prepared_turn_id']
        public['files']=store.read(row['id'],'result')['files'] if row['manifest_hash'] else []
        app=db.execute(select(applications).where(applications.c.candidate_id==row['id']).order_by(applications.c.created_at.desc(),applications.c.id).limit(1)).mappings().first()
        if app:
            public['application']={k:app[k] for k in ('id','state','phase','error_code','created_at','updated_at')}
        items.append(public)
    return {'items':items}
