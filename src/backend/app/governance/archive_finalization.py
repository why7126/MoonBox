"""Read-only document completion gate shared by CLI and archive coordinators.

This is deliberately not an archive authorization or a replacement for acceptance.
Historical evidence is never rewritten; ambiguous current claims require review.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

import yaml


CURRENT = re.compile(r'当前(?:交付|验收|实施|开发)?状态|目前(?:交付|验收|实施)?状态|当前摘要')
STALE = re.compile(r'\b(?:in_sprint|pending|proposed|applied|not_started|todo|blocked|failed)\b|尚未实施|未(?:正式)?归档|待开发|待实现|待验收')
HISTORY = re.compile(r'历史|当时|首次|曾经|原始|复盘|变更记录|迁移记录')
CONDITION = re.compile(r'如果|若|当.+时|不得|不应|不覆盖|不修改|不代表|例如|示例')
REPO_PATH = re.compile(r'(?<![\w/])(?:openspec|issues|iterations|docs)/[^\s`<>\[\]()，。；：、]+')


def safe_path(root: Path, path: Path) -> bool:
    return path.is_relative_to(root) and not any(
        item.is_symlink() for item in (path, *path.parents) if item.is_relative_to(root))


def metadata(path: Path) -> dict:
    text = path.read_text(encoding='utf-8')
    parts = text.split('---', 2)
    if len(parts) != 3 or parts[0].strip():
        return {}
    data = yaml.safe_load(parts[1])
    return data if isinstance(data, dict) else {}


def paragraphs(text: str):
    """Keep heading provenance and paragraph line numbers; never inspect code samples."""
    headings = []
    buffer = []
    start = 0
    fence = None
    frontmatter = text.startswith('---\n')
    for number, line in enumerate(text.splitlines(), 1):
        if frontmatter:
            if number > 1 and line.strip() == '---':
                frontmatter = False
            continue
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            if buffer:
                yield start, ' '.join(buffer), ' / '.join(headings)
                buffer = []
            if fence is None:
                fence = marker[1]
            elif marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
            continue
        if fence:
            continue
        if line.lstrip().startswith('|'):
            if buffer:
                yield start, ' '.join(buffer), ' / '.join(headings)
                buffer = []
            yield number, line.strip(), ' / '.join(headings)
            continue
        heading = re.match(r'^(#{1,6})\s+(.*)', line)
        if not line.strip() or heading:
            if buffer:
                yield start, ' '.join(buffer), ' / '.join(headings)
                buffer = []
            if heading:
                level = len(heading[1])
                headings = headings[:level - 1] + [heading[2]]
            continue
        if not buffer:
            start = number
        buffer.append(line.strip())
    if buffer:
        yield start, ' '.join(buffer), ' / '.join(headings)


def current_claims(text: str, *, completed: bool) -> list[dict]:
    if not completed:
        return []
    hits = []
    for line, paragraph, heading in paragraphs(text):
        # Evaluate individual assertions, so a negated sentence cannot exempt its neighbour.
        for sentence in re.split(r'[。；;]', paragraph):
            current_section = re.search(r'(?:^| / )(?:实施验证摘要|验收结论)$', heading)
            if not (CURRENT.search(sentence + ' ' + heading) or current_section) or not STALE.search(sentence):
                continue
            if CONDITION.search(sentence) or re.search(r'生产|上线|部署', sentence):
                continue
            prose = re.sub(r'\[[^\]]*\]\([^)]*\)|`[^`]*`', '', sentence)
            historical = HISTORY.search(heading + prose) or re.search(r'\d{4}-\d{2}-\d{2}', prose)
            hits.append({'line': line, 'kind': 'current-state-review' if historical else 'current-state-conflict',
                         'severity': 'review' if historical else 'blocker'})
    return list({(h['line'], h['kind']): h for h in hits}.values())


def navigation(text: str):
    """Actual links remain navigation even under a historical heading."""
    definitions = {m[1].strip().casefold(): m[2] or m[3] for m in re.finditer(
        r'^\s{0,3}\[([^\]]+)\]:\s*(?:<([^>]+)>|(\S+))', text, re.M)}
    for line, paragraph, heading in paragraphs(text):
        values = []
        values.extend(m[1] or m[2] for m in re.finditer(
            r'!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[\'"][^\n]*?[\'"])?\s*\)', paragraph))
        for match in re.finditer(r'!?\[([^\]]+)\](?:\[([^\]]*)\])?', paragraph):
            key = (match[2] or match[1]).strip().casefold()
            if key in definitions:
                values.append(definitions[key])
        if not HISTORY.search(heading + paragraph) and not CONDITION.search(paragraph):
            values.extend(m[0].rstrip('.,') for m in REPO_PATH.finditer(paragraph)
                          if not any(m[0] in value for value in values))
        for value in dict.fromkeys(values):
            yield line, value


def inspect_document(root: Path, path: Path, *, completed: bool = False) -> list[dict]:
    relative = str(path.relative_to(root))
    if not safe_path(root, path):
        return [{'file': relative, 'line': 0, 'kind': 'unsafe-document', 'severity': 'blocker'}]
    text = path.read_text(encoding='utf-8')
    hits = [dict(hit, file=relative) for hit in current_claims(text, completed=completed)]
    if completed:
        field = 'acceptance_status' if path.name == 'acceptance.md' else 'status'
        value = metadata(path).get(field)
        if path.name == 'acceptance.md' and path.parent.parent == root / 'openspec/archive':
            from .archive_metadata import restored_acceptance_status
            try:
                value = restored_acceptance_status(root, path.parent) or value
            except (OSError, ValueError, TypeError, KeyError):
                hits.append({'file': relative, 'line': 1, 'kind': 'metadata-restoration-invalid',
                             'severity': 'blocker'})
        legacy_change_trace = path.name == 'trace.md' and path.parent.parent == root / 'openspec/archive'
        if value in {'in_sprint', 'pending', 'pending_review', 'proposed', 'applied', 'todo', 'open', 'blocked', 'failed', 'not_started'} and not (legacy_change_trace and value == 'applied'):
            hits.append({'file': relative, 'line': 1, 'kind': 'current-metadata-conflict', 'severity': 'blocker'})
    for line, value in navigation(text):
        parts = urlsplit(value)
        if parts.scheme or parts.netloc or not parts.path:
            continue
        raw = unquote(parts.path)
        if any(token in raw for token in ('<', '>', '*', '${')):
            hits.append({'file': relative, 'line': line, 'kind': 'dynamic-reference-review', 'severity': 'review'})
            continue
        base = root if re.match(r'^(openspec|issues|iterations|docs)/', raw) else path.parent
        target = Path(os.path.abspath(base / raw))
        if not target.exists():
            from .archive_issue_reference import resolve
            target = resolve(root, path, target) or target
        kind = 'unsafe-reference' if not safe_path(root, target) else 'missing-reference' if not target.exists() else None
        if kind:
            hits.append({'file': relative, 'line': line, 'kind': kind, 'severity': 'blocker'})
    return hits


def document_scope(root: Path, change: str, archive: Path) -> dict[Path, bool]:
    # Only top-level governance documents; evidence packages are immutable inputs.
    documents = {p: True for p in archive.glob('*.md')}
    for domain in ('requirements', 'bugs'):
        for stage in ('', 'plan', 'review', 'archive'):
            base = root / 'issues' / domain / stage
            for directory in base.glob('*'):
                if not safe_path(root, directory) or not directory.is_dir():
                    continue
                if not directory.name.startswith(('REQ-', 'BUG-')):
                    continue
                files = list(directory.glob('*.md'))
                if not any(safe_path(root, p) and re.search(rf'(?<![\w-]){re.escape(change)}(?![\w-])',
                           p.read_text(encoding='utf-8')) for p in files):
                    continue
                principal = directory / ('requirement.md' if domain == 'requirements' else 'bug.md')
                done = principal.is_file() and safe_path(root, principal) and metadata(principal).get('status') == 'done'
                trace = directory / 'trace.md'
                acceptance = directory / 'acceptance.md'
                partial = acceptance.is_file() and safe_path(root, acceptance) and metadata(acceptance).get('acceptance_status') == 'partial'
                if trace.is_file() and safe_path(root, trace):
                    meta = metadata(trace)
                    links = [item.get('change_id') if isinstance(item, dict) else item
                             for item in meta.get('openspec_changes', [])]
                    links += meta.get('related_changes') or []
                    if meta.get('related_change'):
                        links.append(meta['related_change'])
                    if links and change not in links:
                        # A historical cross-reference is not ownership of this archive.
                        continue
                    # Match existing derive_issue semantics without writing a status:
                    # partial acceptance or an outstanding sibling stays open.
                    if links:
                        done = all(isinstance(cid, str) and re.fullmatch(r'[a-z0-9][a-z0-9-]{0,100}', cid)
                                   and len(list((root / 'openspec/archive').glob(f'????-??-??-{cid}'))) == 1
                                   and not (root / 'openspec/changes' / cid).exists() for cid in links)
                if partial:
                    done = False
                documents.update({p: bool(done) for p in files})
    for stage in ('change', 'archive'):
        for path in (root / 'iterations' / stage).glob('sprint-*/sprint.yaml'):
            if not safe_path(root, path):
                continue
            data = yaml.safe_load(path.read_text(encoding='utf-8'))
            if isinstance(data, dict) and change in (data.get('changes') or []):
                documents.update({p: False for name in ('sprint.md', 'release-note.md', 'acceptance-report.md')
                                  if (p := path.parent / name).is_file()})
    return documents


def build_report(root: Path, change: str) -> dict:
    root = root.resolve()
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,100}', change):
        raise ValueError('invalid_change_id')
    archives = list((root / 'openspec/archive').glob(f'????-??-??-{change}'))
    hits = []
    documents = {}
    if (len(archives) != 1 or not archives[0].is_dir() or not safe_path(root, archives[0])
            or (root / 'openspec/changes' / change).exists()
            or (root / 'openspec/changes' / change).is_symlink()
            or list((root / 'openspec/changes/archive').glob(f'????-??-??-{change}'))):
        hits.append({'file': 'openspec', 'line': 0, 'kind': 'archive-identity', 'severity': 'blocker'})
    else:
        trace = archives[0] / 'trace.md'
        from .archive_recovery import completed_archive
        if not trace.is_file() or not safe_path(root, trace) or not completed_archive(archives[0], change):
            hits.append({'file': str(trace.relative_to(root)), 'line': 0,
                         'kind': 'archive-sync-incomplete', 'severity': 'blocker'})
        documents = document_scope(root, change, archives[0])
        for path, completed in sorted(documents.items()):
            hits.extend(inspect_document(root, path, completed=completed))
            if completed and path.name in {'requirement.md', 'bug.md'} and path.parent.parent.name != 'archive':
                hits.append({'file': str(path.relative_to(root)), 'line': 0,
                             'kind': 'issue-promotion-incomplete', 'severity': 'blocker'})
    return {'change': change, 'status': 'blocked' if hits else 'finalized',
            'checked_files': len(documents), 'findings': hits,
            'delivery': 'unchanged', 'usage': 'not_checked'}


def require_finalized(root: Path, change: str) -> dict:
    report = build_report(root, change)
    if report['status'] != 'finalized':
        from .archive_diagnostics import ArchiveDiagnosticError
        raise ArchiveDiagnosticError('archive_finalization_blocked', report)
    return report


def needs_finalize(root: Path, change: str) -> bool:
    archives = list((root / 'openspec/archive').glob(f'????-??-??-{change}'))
    missing_sync = (len(archives) != 1 or not safe_path(root, archives[0] / 'trace.md')
            or not (archives[0] / 'trace.md').is_file()
            or metadata(archives[0] / 'trace.md').get('status') != 'archived')
    if missing_sync:
        return True
    return any(done and p.name in {'requirement.md', 'bug.md'} and p.parent.parent.name != 'archive'
               for p, done in document_scope(root, change, archives[0]).items())
