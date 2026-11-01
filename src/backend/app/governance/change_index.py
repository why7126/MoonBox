"""Request-local Change identity and association index over a complete snapshot.

Resolve relationships before applying visibility. Unknown references are never
reclassified as independent objects, and archived copies never fill active gaps.
"""
from app.governance.change_time import card_time
from app.governance.change_classification import classification
from app.governance.card_metadata import estimate_metadata, root_cause_metadata
from app.governance.titles import read_title
from dataclasses import dataclass, field
from pathlib import Path
import re
from collections.abc import Callable

import yaml

from app.governance.lifecycle import change_state
from app.services import requirement_center as legacy
from app.schemas.requirement_center import (
    RequirementCenterAction, RequirementCenterChangeSummary, RequirementCenterDocument,
    RequirementCenterDocumentCapability, RequirementCenterIssue, RequirementCenterSource,
)

CHANGE_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
SOURCE_KEYS = ('requirement', 'requirement_id', 'source_requirement', 'requirements',
               'bug', 'bug_id', 'source_bug', 'bugs', 'source_issue', 'source_issues')
DELIVERY_EVIDENCE_HEADINGS = {
    '验证记录',
    '验收记录',
    '验收结果',
    '验证结果',
    '验证摘要',
    'Validation Log',
    '实施与验证记录',
}


@dataclass
class ChangeRecord:
    id: str
    directories: list[Path] = field(default_factory=list)
    directory: Path | None = None
    issue_ids: set[str] = field(default_factory=set)
    invalid_source: bool = False
    trace: dict = field(default_factory=dict)
    stage: str = 'unknown'
    source_kind: str = 'missing'
    title: str | None = None

    def visible(self, can_read: Callable[[str], bool]) -> bool:
        return not self.invalid_source and can_read(self.id) and all(can_read(i) for i in self.issue_ids)


def chinese_title(directory: Path, trace: dict) -> str | None:
    return read_title(directory / 'proposal.md')


@legacy._memoized_read
def _root_cause_fields(issue_dir: Path) -> dict:
    """Pure document facts, shared only inside a verified immutable snapshot."""
    path = issue_dir / 'root-cause.md'
    if path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(issue_dir.resolve()):
        return root_cause_metadata(path.read_text(encoding='utf-8'), legacy._frontmatter(path))
    return {}


class ChangeIndex:
    def __init__(self, root: Path):
        self.root = root
        self.entries: dict[str, tuple[str, dict]] = {}
        self.records: dict[str, ChangeRecord] = {}
        self.sprint_directories: dict[str, Path] = {}
        self.sprint_memberships: dict[str, set[str]] = {}
        for location in ('change', 'archive'):
            for directory in sorted((root / 'iterations' / location).glob('sprint-*')):
                sid = directory.name
                if (not re.fullmatch(r'sprint-\d{3,}', sid) or not directory.is_dir()
                        or directory.is_symlink() or sid in self.sprint_directories):
                    continue
                self.sprint_directories[sid] = directory
                try:
                    members = legacy._read_yaml(directory / 'sprint.yaml').get('changes')
                except yaml.YAMLError:
                    continue
                if isinstance(members, list):
                    for cid in members:
                        if isinstance(cid, str):
                            self.sprint_memberships.setdefault(cid, set()).add(sid)
        for folder, kind in (('requirements', 'requirement'), ('bugs', 'bug')):
            registry_path = root / 'issues' / folder / '_registry.yaml'
            # Only immutable adapters have validated and seeded registry data.
            memo = legacy._READ_MEMO.get()
            registry = (legacy._read_yaml(registry_path) if memo is not None and ('_read_yaml', (registry_path,)) in memo
                        else yaml.load(registry_path.read_text(), Loader=getattr(yaml, 'CSafeLoader', yaml.SafeLoader)))
            for entry in registry['entries']:
                self.entries[entry['id']] = (kind, entry)
        for location in ('changes', 'archive'):
            for directory in sorted((root / 'openspec' / location).glob('*')):
                if not directory.is_dir() or directory.is_symlink():
                    continue
                cid = directory.name
                if location == 'archive':
                    match = re.fullmatch(r'\d{4}-\d{2}-\d{2}-(.+)', cid)
                    if not match:
                        continue
                    cid = match[1]
                if CHANGE_ID.fullmatch(cid):
                    self.records.setdefault(cid, ChangeRecord(cid)).directories.append(directory)
        for oid, (_, entry) in self.entries.items():
            issue_dir = legacy._safe_issue_dir(entry.get('path'))
            trace = legacy._frontmatter(issue_dir / 'trace.md') if issue_dir else {}
            for cid in legacy._linked_changes(entry, trace):
                if CHANGE_ID.fullmatch(cid):
                    self.records.setdefault(cid, ChangeRecord(cid)).issue_ids.add(oid)
        for record in self.records.values():
            active = [p for p in record.directories if p.parent.name == 'changes']
            record.directory = active[0] if active else (record.directories[0] if len(record.directories) == 1 else None)
            # Conservatively include source associations of all physical versions.
            # A stale archive cannot turn a linked object into an independent one.
            for directory in record.directories:
                try:
                    trace = legacy._frontmatter(directory / 'trace.md')
                except yaml.YAMLError:
                    record.invalid_source = True
                    continue
                if trace.get('change_id') and trace['change_id'] != record.id:
                    record.invalid_source = True
                for key in SOURCE_KEYS:
                    if key not in trace or trace[key] in (None, '', []):
                        continue
                    refs = trace[key] if isinstance(trace[key], list) else [trace[key]]
                    for ref in refs:
                        matches = self.resolve_issue(ref)
                        if len(matches) != 1:
                            record.invalid_source = True
                        record.issue_ids.update(matches)
            if record.directory:
                try:
                    record.trace = legacy._frontmatter(record.directory / 'trace.md')
                except yaml.YAMLError:
                    record.invalid_source = True
                    continue
                record.source_kind = 'active' if record.directory.parent.name == 'changes' else 'archive'
                record.title = chinese_title(record.directory, record.trace)
                if record.source_kind == 'archive':
                    record.stage = 'done'
                else:
                    # Task checkboxes are progress, never completion evidence.
                    state = record.trace.get('status')
                    if 'execution' in record.trace:
                        try:
                            state = change_state(record.trace, 0, 0)
                        except (ValueError, TypeError):
                            state = None
                    record.stage = {'proposed': 'ready-dev', 'in_progress': 'development', 'applied': 'acceptance'}.get(state, 'unknown')
                    if record.stage == 'ready-dev' and self.sprint_assignment(record)[0] != 'valid':
                        record.stage = 'sprint-planning'
            elif record.directories:
                record.source_kind = 'conflict'

    def resolve_issue(self, ref) -> list[str]:
        if not isinstance(ref, str):
            return []
        if ref in self.entries:
            return [ref]
        if re.fullmatch(r'(REQ|BUG)-\d+', ref):
            return [oid for oid in self.entries if oid.startswith(ref + '-')]
        return []

    def warnings(self, record: ChangeRecord) -> list[str]:
        result = []
        if record.trace.get('iteration') in (None, '') and len(self.sprint_memberships.get(record.id, set())) > 1:
            result.append('多个 Sprint 成员关系，所属迭代待核实')
        if record.stage == 'unknown':
            result.append('Change 状态或归档版本待核实')
        if record.source_kind == 'active' and len(record.directories) > 1:
            result.append('活动与归档同 ID，当前读取活动版本')
        if record.source_kind == 'archive' and record.trace.get('status') != 'archived':
            result.append('已按归档目录识别完成，历史 trace 状态未同步')
        if record.directory and not (record.directory / 'proposal.md').is_file():
            result.append('缺少 proposal.md，可读取其他现有文档')
        if not record.title:
            result.append('缺少 Change 中文业务标题，保留原标题')
        return result

    def summary(self, record: ChangeRecord) -> RequirementCenterChangeSummary:
        progress = legacy._change_task_progress([record.id]) if record.directory else None
        return RequirementCenterChangeSummary(id=record.id, title=record.title, stage=record.stage,
            source_kind=record.source_kind, task_progress=progress, document_entries=self.documents(record), warnings=self.warnings(record))

    def sprint_id(self, record: ChangeRecord) -> str | None:
        if not record.issue_ids and record.stage in ('ready-dev', 'sprint-planning'):
            return self.sprint_assignment(record)[1]
        members = self.sprint_memberships.get(record.id, set())
        explicit = record.trace.get('iteration')
        if explicit not in (None, ''):
            return explicit if isinstance(explicit, str) and explicit in members else None
        return next(iter(members)) if len(members) == 1 else None

    def sprint_assignment(self, record: ChangeRecord) -> tuple[str, str | None, str]:
        """Classify proposed standalone membership without changing lifecycle facts."""
        members = self.sprint_memberships.get(record.id, set())
        explicit = record.trace.get('iteration')
        if not members and explicit in (None, ''):
            return 'unassigned', None, '待纳入迭代'
        if len(members) > 1:
            return 'conflict', None, '多个 Sprint 成员关系，所属迭代待核实'
        if len(members) != 1 or (explicit not in (None, '') and (not isinstance(explicit, str) or explicit not in members)):
            return 'invalid', None, 'Sprint 声明与成员关系不一致或已失效'
        sid = next(iter(members))
        directory = self.sprint_directories[sid]
        plan = legacy._read_yaml(directory / 'sprint.yaml')
        if (directory.parent.name != 'change' or plan.get('sprint_id', sid) != sid
                or plan.get('status') not in ('planning', 'active', 'in_progress')):
            return 'invalid', None, 'Sprint 已关闭或状态无效'
        return 'valid', sid, ''

    def sprint_document(self, record: ChangeRecord, document_name: str = 'sprint.md') -> Path | None:
        if document_name not in legacy.SPRINT_DOCUMENT_NAMES:
            return None
        sprint_id = self.sprint_id(record)
        if sprint_id is None:
            return None
        directory = legacy._snapshot_resolve(self.sprint_directories[sprint_id])
        target = legacy._snapshot_resolve(directory / document_name)
        return target if legacy._snapshot_is_file(target) and target.is_relative_to(directory) else None

    def documents(self, record: ChangeRecord) -> list[RequirementCenterDocument]:
        if not record.directory:
            return []
        existing = legacy._change_document_names(record.id)
        names = existing
        names.extend(name for name in legacy.SPRINT_DOCUMENT_NAMES if self.sprint_document(record, name))
        return [RequirementCenterDocument(name=name, type='markdown', open_mode='drawer', label=name,
            url=f'/api/v1/requirement-center/changes/{record.id}/documents/{name}',
            capability=legacy.compute_document_capability(issue_type='change', stage=record.stage,
                document_name=name, path_category='change', exists=True)) for name in names]

    def acceptance_source_reason(self, record: ChangeRecord, *, source_root: Path | None = None) -> str | None:
        """Locate delivery evidence; never infer test success from file presence."""
        if legacy._SUMMARY_READ.get():
            return '验收待检查'
        directory = record.directory
        if directory is None:
            return '验收来源待核实：Change 目录不唯一'
        explicit = record.trace.get('acceptance_refs')
        if explicit is not None:
            if not isinstance(explicit, list) or not explicit:
                return '验收来源待核实：acceptance_refs 无效'
            for ref in explicit:
                if not isinstance(ref, str) or not ref or Path(ref).is_absolute() or '..' in Path(ref).parts:
                    return '验收来源待核实：引用路径无效'
                target = directory / ref
                if target.suffix != '.md' or not target.resolve().is_relative_to(directory.resolve()):
                    return '验收来源待核实：引用路径无效'
                if not target.is_file():
                    return '验收来源待核实：声明的证据文件缺失'
                if not target.read_text(encoding='utf-8').strip():
                    return '验收来源待核实：声明的证据文件为空'
        plan = directory / 'acceptance-plan.json'
        if plan.exists() or plan.is_symlink():
            if plan.is_symlink() or not plan.is_file():
                return '验收来源待核实：逐项验收计划无效'
            from app.governance.acceptance_evidence import archived_readiness, readiness, readiness_reason
            try:
                evidence = (readiness(self.root, record.id, source_root=source_root)
                            if directory.parent.name == 'changes' else archived_readiness(self.root, directory))
            except (OSError, ValueError, KeyError, TypeError):
                return '验收来源待核实：逐项验收证据无效'
            return readiness_reason(evidence)
        if explicit is not None:
            return None
        for name in ('acceptance.md', 'verification.md'):
            target = directory / name
            if target.is_file() and target.resolve().is_relative_to(directory.resolve()):
                return None if target.read_text(encoding='utf-8').strip() else f'文档内容为空：{name}'
        trace_path = directory / 'trace.md'
        text = trace_path.read_text(encoding='utf-8') if trace_path.is_file() else ''
        sections = re.split(r'(?m)^#{1,6} +', text)
        for section in sections[1:]:
            title, _, body = section.partition('\n')
            if title.strip() in DELIVERY_EVIDENCE_HEADINGS and body.strip():
                return None
        return '验收来源待核实：未找到交付验证记录'

    def action(self, record: ChangeRecord) -> RequirementCenterAction | None:
        if record.stage == 'sprint-planning':
            kind, _, reason = self.sprint_assignment(record)
            if kind == 'unassigned':
                return RequirementCenterAction(command=f'/sprint-propose --change {record.id}', label='加入迭代')
            return RequirementCenterAction(command=f'核对归属 {record.id}', label='核对归属', disabled_reason=reason)
        if record.stage == 'development':
            return RequirementCenterAction(command=f'查看进度 {record.id}', label='查看进度')
        if record.stage not in ('ready-dev', 'acceptance'):
            return None
        command, label = ('opsx-apply', '开始开发') if record.stage == 'ready-dev' else ('opsx-archive', '完成 / 归档')
        names = [p.name for p in record.directory.glob('*.md')] if record.directory else []
        reason = (self.acceptance_source_reason(record) if record.stage == 'acceptance'
                  else legacy._blocked_reason(record.stage, 'change', names, [], record.directory))
        if not self.sprint_id(record):
            reason = reason or '缺少唯一有效的 Sprint 归属'
        return RequirementCenterAction(command=f'/{command} {record.id}', label=label, disabled_reason=reason)

    def delivery_acceptance_progress(self, record: ChangeRecord):
        """Only current evidence for this delivery can contribute passed counts."""
        if legacy._SUMMARY_READ.get() or record.directory is None:
            return None
        if not (record.directory / 'acceptance-plan.json').is_file():
            return None
        from app.governance.acceptance_evidence import read_plan
        try:
            plan = read_plan(record.directory)
            if self.acceptance_source_reason(record) is None:
                total = len(plan['checks'])
                return total, total
        except (OSError, ValueError, KeyError, TypeError):
            pass
        # Missing/stale evidence is unknown, never copied from the parent
        # signoff or inferred from task checkboxes.
        return None

    def source_card(self, oid):
        kind, entry = self.entries[oid]
        issue_dir = legacy._safe_issue_dir(entry.get('path'))
        trace = legacy._frontmatter(issue_dir / 'trace.md') if issue_dir else {}
        card = legacy._build_issue(kind, entry, changes_override=[],
                                   status_override=trace.get('status') or entry.get('status'))
        main = issue_dir / ('requirement.md' if kind == 'requirement' else 'bug.md') if issue_dir else None
        card.title = (read_title(main) if main else None) or card.title
        card.display_title = card.title
        card.object_id = oid
        return card, issue_dir, trace

    def cards(self, can_read: Callable[[str], bool], *, selected_object=None) -> list[RequirementCenterIssue]:
        visible = {cid: record for cid, record in self.records.items() if record.visible(can_read)}
        cards = []
        source_data = {}
        def source_for(oid):
            if oid not in source_data:
                source_data[oid] = self.source_card(oid)
            return source_data[oid]
        for oid, (kind, entry) in self.entries.items():
            if selected_object is not None and oid != selected_object:
                continue
            if not can_read(oid):
                continue
            related = [r for r in visible.values() if oid in r.issue_ids]
            # Explicit Issue detail keeps whole-scope facts. The board never
            # duplicates an Issue aggregate beside its valid delivery cards.
            if selected_object is None and any(r.directory and r.stage != 'unknown' for r in related):
                continue
            card, issue_dir, trace = source_for(oid)
            if selected_object is None and any(oid in r.issue_ids for r in self.records.values()):
                card.change_warning = '关联交付待核实，请核对来源和权限'
                card.title_warning = card.change_warning
                card.action = RequirementCenterAction(command='', label='核对关联', disabled_reason=card.change_warning)
            sid = trace.get('iteration') or entry.get('target_iteration') or entry.get('iteration')
            self.apply_card_metadata(card, oid, sid, [], issue_dir)
            cards.append(card)
        for record in visible.values():
            if selected_object is not None and record.id != selected_object:
                continue
            # Missing/conflicting linked records stay in source diagnostics.
            if record.issue_ids and (not record.directory or record.stage == 'unknown'):
                continue
            documents = self.documents(record)
            tasks = legacy._change_tasks([record.id]) if record.directory else None
            classified = legacy._classified_change_tasks([record.id])
            warnings = self.warnings(record)
            sources = []
            source_cards = []
            for oid in sorted(record.issue_ids):
                source, _, _ = source_for(oid)
                source_cards.append(source)
                sources.append(RequirementCenterSource(id=oid, type=source.type, title=source.title,
                    status=source.status, document_entries=[d.model_copy(deep=True) for d in source.document_entries
                        if d.name not in legacy.SPRINT_DOCUMENT_NAMES and d.url and '/issues/' in d.url]))
            if record.stage == 'sprint-planning':
                warnings.append(self.sprint_assignment(record)[2])
            action = self.action(record)
            if sources and action and record.stage != 'development':
                # Chat keeps this Change as its primary object. The server
                # validates the source and binds its command to that identity.
                if record.stage == 'sprint-planning':
                    action.disabled_reason = '请从来源事项核对 Sprint 归属'
                if len(sources) == 1:
                    action.command = action.command.replace(record.id, sources[0].id)
                else:
                    action.command = ''
                    action.requires_choice = 'source_issue'
            card = RequirementCenterIssue(id=record.id, type='change', card_kind='delivery',
                target_change_id=record.id, source_issues=sources, title=record.title or record.id,
                display_title=record.title or record.id, title_source='proposal.md' if record.title else 'change_id',
                current_change=self.summary(record),
                priority=(record.trace.get('priority') if record.trace.get('priority') in ('P0', 'P1', 'P2', 'P3') else ''), owner=legacy._owner_name(record.trace.get('owner')),
                owner_key=legacy._owner_key(record.trace.get('owner')), source=record.source_kind,
                stage=record.stage, documents=[d.name for d in documents], document_entries=documents,
                detail_url='', updated_at=legacy._updated_at(record.trace.get('updated_at') or record.trace.get('created_at')),
                tasks=tasks, task_progress=(classified.development.progress if record.stage == 'acceptance' and classified.has_progress else (tasks.done, tasks.total) if tasks else None),
                test_progress=classified.test.progress if classified.has_progress else None,
                manual_acceptance_progress=self.delivery_acceptance_progress(record) if record.stage in ('acceptance', 'done') else None,
                sprint_id=self.sprint_id(record), action=action,
                acceptance_blocked_reason=self.acceptance_source_reason(record) if record.stage == 'acceptance' else None,
                blocked=(self.sprint_assignment(record)[2] if record.stage == 'sprint-planning'
                         and self.sprint_assignment(record)[0] != 'unassigned' else None),
                drift_warnings=warnings)
            if not record.issue_ids:
                for key, value in card_time(record.trace).items():
                    setattr(card, key, value)
                level = classification(record.id, record.trace)
                for key, value in level.items():
                    setattr(card, key, value)
                card.priority_state = level['classification_state']
                card.can_edit_priority = False
            # Shared source metadata is allowed only when unanimous; never use
            # sorting order to choose an owner, classification or action source.
            for name in ('priority', 'severity', 'owner', 'owner_key'):
                values = {getattr(source, name) for source in source_cards}
                if len(values) == 1:
                    setattr(card, name, values.pop())
                elif len(values) > 1:
                    card.drift_warnings.append('来源元信息不一致：' + name)
            if len(source_cards) == 1 and source_cards[0].type == 'bug':
                issue_dir = legacy._safe_issue_dir(self.entries[sources[0].id][1].get('path'))
                if issue_dir:
                    for name, value in _root_cause_fields(issue_dir).items():
                        setattr(card, name, value)
            if record.stage == 'done' and any(source.status not in ('done', 'archived') for source in sources):
                card.completion_hint = '子交付已完成；来源仍有未交付范围'
            self.apply_card_metadata(card, card.id, card.sprint_id, [], None)
            cards.append(card)
        return cards

    def apply_card_metadata(self, card, object_id, sprint_id, changes, issue_dir):
        directory = self.sprint_directories.get(sprint_id) if isinstance(sprint_id, str) else None
        if directory:
            sprint = legacy._borrow_yaml(directory / 'sprint.yaml')
            key = {'requirement': 'requirements', 'bug': 'bugs', 'change': 'changes'}[card.type]
            if object_id in (sprint.get(key) or []):
                source_issue_id = None
                record = self.records.get(object_id) if card.type == 'change' else None
                if record and not record.invalid_source and len(record.issue_ids) == 1:
                    oid = next(iter(record.issue_ids))
                    source_key = 'requirements' if oid.startswith('REQ-') else 'bugs'
                    related = {r.id for r in self.records.values() if oid in r.issue_ids}
                    if related == {object_id} and oid in (sprint.get(source_key) or []):
                        source_issue_id = oid
                for name, value in estimate_metadata(sprint.get('scope_estimates'), object_id, changes,
                                                     source_issue_id=source_issue_id).items():
                    setattr(card, name, value)
        if card.type == 'bug' and issue_dir:
            for name, value in _root_cause_fields(issue_dir).items():
                setattr(card, name, value)
