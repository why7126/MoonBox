"""Request-local Change identity and association index over a complete snapshot.

Resolve relationships before applying visibility. Unknown references are never
reclassified as independent objects, and archived copies never fill active gaps.
"""
from dataclasses import dataclass, field
from pathlib import Path
import re
from collections.abc import Callable

import yaml

from app.governance.lifecycle import change_state, aggregate_states
from app.services import requirement_center as legacy
from app.schemas.requirement_center import (
    RequirementCenterAction, RequirementCenterChangeSummary, RequirementCenterDocument,
    RequirementCenterDocumentCapability, RequirementCenterIssue,
)

CHANGE_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
SOURCE_KEYS = ('requirement', 'requirement_id', 'source_requirement', 'requirements',
               'bug', 'bug_id', 'source_bug', 'bugs', 'source_issue', 'source_issues')


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
        return not self.invalid_source and all(can_read(i) for i in self.issue_ids) and (
            bool(self.issue_ids) or can_read(self.id))


def chinese_title(directory: Path, trace: dict) -> str | None:
    generic = {'变更提案', '设计', '技术设计', '任务清单', '实施任务', '追溯', 'Change 追溯', '背景', '目标', '需求', '概述', '验证记录', '验收记录', '验收结果', '验证结果', '变更追溯', '背景与动机', '变更内容', '能力范围', '目标与非目标', '设计决策'}
    for value in (trace.get('chinese_title'), trace.get('title')):
        if isinstance(value, str) and value.strip() not in generic and re.search(r'[\u4e00-\u9fff]', value):
            return value.strip()
    for filename in ('proposal.md', 'design.md', 'trace.md'):
        path = directory / filename
        if not path.is_file():
            continue
        try:
            metadata = legacy._frontmatter(path)
        except yaml.YAMLError:
            metadata = {}
        value = metadata.get('title')
        if isinstance(value, str) and value.strip() not in generic and re.search(r'[\u4e00-\u9fff]', value):
            return value.strip()
        for line in path.read_text(encoding='utf-8').splitlines():
            if not line.startswith('# '):
                continue
            value = re.sub(r'^(?:Change|变更提案|提案|设计)\s*[:：-]\s*', '', line[2:].strip())
            if value not in generic and re.search(r'[\u4e00-\u9fff]', value):
                return value
    return None


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
            registry = yaml.load((root / 'issues' / folder / '_registry.yaml').read_text(), Loader=getattr(yaml, 'CSafeLoader', yaml.SafeLoader))
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
        members = self.sprint_memberships.get(record.id, set())
        explicit = record.trace.get('iteration')
        if explicit not in (None, ''):
            return explicit if isinstance(explicit, str) and explicit in members else None
        return next(iter(members)) if len(members) == 1 else None

    def sprint_document(self, record: ChangeRecord) -> Path | None:
        sprint_id = self.sprint_id(record)
        if sprint_id is None:
            return None
        target = self.sprint_directories[sprint_id] / 'sprint.md'
        return target if target.is_file() else None

    def documents(self, record: ChangeRecord) -> list[RequirementCenterDocument]:
        if not record.directory:
            return []
        existing = legacy._change_document_names(record.id)
        names = [name for name in ('proposal.md', 'spec.md', 'design.md', 'tasks.md', 'trace.md') if name in existing]
        if self.sprint_document(record):
            names.append('sprint.md')
        return [RequirementCenterDocument(name=name, type='markdown', open_mode='drawer', label=name,
            url=f'/api/v1/requirement-center/changes/{record.id}/documents/{name}',
            capability=RequirementCenterDocumentCapability(reason='Change 追溯入口只读')) for name in names]

    def acceptance_source_reason(self, record: ChangeRecord) -> str | None:
        """Locate delivery evidence; never infer test success from file presence."""
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
            if title.strip() in ('验证记录', '验收记录', '验收结果', '验证结果') and body.strip():
                return None
        return '验收来源待核实：未找到交付验证记录'

    def action(self, record: ChangeRecord) -> RequirementCenterAction | None:
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

    def cards(self, can_read: Callable[[str], bool]) -> list[RequirementCenterIssue]:
        visible = {cid: record for cid, record in self.records.items() if record.visible(can_read)}
        cards = []
        for oid, (kind, entry) in self.entries.items():
            if not can_read(oid):
                continue
            related = [record for record in visible.values() if oid in record.issue_ids]
            # No evidence in current data model selects among multiple Changes.
            current = related[0] if len(related) == 1 else None
            issue_dir = legacy._safe_issue_dir(entry.get('path'))
            trace = legacy._frontmatter(issue_dir / 'trace.md') if issue_dir else {}
            status = trace.get('status') or entry.get('status')
            if related and status not in ('done', 'archived'):
                states = [{'ready-dev': 'proposed', 'development': 'in_progress', 'acceptance': 'applied', 'done': 'archived'}.get(r.stage, 'unknown') for r in related]
                status = 'unknown' if 'unknown' in states else aggregate_states(states)
            card = legacy._build_issue(kind, entry, changes_override=[current.id] if current else [], status_override=status)
            card.related_changes = [self.summary(r) for r in related]
            card.current_change = self.summary(current) if current else None
            card.change_warning = '多个 Change，当前项待核实' if len(related) > 1 else None
            if current:
                # Keep terminal Issue facts; otherwise Change status is explicit.
                issue_dir = legacy._safe_issue_dir(entry.get('path'))
                trace = legacy._frontmatter(issue_dir / 'trace.md') if issue_dir else {}
                if (trace.get('status') or entry.get('status')) not in ('done', 'archived'):
                    card.stage = current.stage
                card.drift_warnings.extend(self.warnings(current))
            cards.append(card)
        for record in visible.values():
            if record.issue_ids:
                continue
            documents = self.documents(record)
            tasks = legacy._change_tasks([record.id]) if record.directory else None
            cards.append(RequirementCenterIssue(id=record.id, type='change', title=record.title or record.id,
                priority='', owner=legacy._owner_name(record.trace.get('owner')), source=record.source_kind,
                stage=record.stage, documents=[d.name for d in documents], document_entries=documents,
                detail_url='', updated_at=legacy._updated_at(record.trace.get('updated_at') or record.trace.get('created_at')),
                tasks=tasks, task_progress=(tasks.done, tasks.total) if tasks else None,
                sprint_id=self.sprint_id(record), action=self.action(record),
                drift_warnings=self.warnings(record)))
        return cards
