"""Read-only, scoped static prototype references across an Issue directory move."""
from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

TEXT_SUFFIXES = {'.md', '.html', '.htm', '.css', '.yaml', '.yml'}
HISTORY = re.compile(r'^(?:\d+[.、 ]+)?(?:变更记录|历史记录|迁移记录|历史验收|历史验收记录|历史验收轮次)(?:\s|（|\(|$)')
PATH = re.compile(r'(?:https?://)?(?:[\w.%+@~:-]+/)*prototype(?:/[\w./%+@~-]*)?(?![\w.])')


@dataclass(frozen=True)
class Reference:
    line: int
    value: str
    context: str = 'active'


@dataclass(frozen=True)
class Finding:
    file: str
    line: int
    reference: str
    target: str
    reason: str
    blocking: bool = False

    def describe(self) -> str:
        return f'{self.file}:{self.line}: {self.reason}: {self.reference} -> {self.target}'


class HTMLReferences(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs: list[Reference] = []
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        self.in_style = tag == 'style' or self.in_style
        for key, value in attrs:
            if not value:
                continue
            context = 'unsupported-base' if tag == 'base' else 'active'
            if key in {'src', 'href', 'poster', 'data'}:
                self.refs.append(Reference(self.getpos()[0], value, context))
            elif key == 'srcset':
                if value.startswith('data:'):
                    self.refs.append(Reference(self.getpos()[0], value))
                else:
                    self.refs.extend(Reference(self.getpos()[0], part.strip().split()[0])
                                     for part in value.split(',') if part.strip())
            elif key == 'style':
                self.refs.extend(css_refs(value, self.getpos()[0] - 1))

    def handle_endtag(self, tag):
        if tag == 'style':
            self.in_style = False

    def handle_data(self, data):
        if self.in_style:
            self.refs.extend(css_refs(data, self.getpos()[0] - 1))


def css_refs(text: str, offset: int = 0) -> list[Reference]:
    text = re.sub(r'/\*.*?\*/', lambda m: '\n' * m[0].count('\n'), text, flags=re.S)
    pattern = r'url\(\s*([\'"]?)(.*?)\1\s*\)|@import\s+[\'"]([^\'"]+)[\'"]'
    return [Reference(offset + text.count('\n', 0, m.start()) + 1, m[2] or m[3])
            for m in re.finditer(pattern, text, re.S)]


def references(path: Path, text: str) -> list[Reference]:
    if path.suffix.lower() in {'.html', '.htm'}:
        parser = HTMLReferences()
        parser.feed(text)
        if any(ref.context == 'unsupported-base' for ref in parser.refs):
            return [Reference(ref.line, ref.value, 'unsupported-base') for ref in parser.refs]
        return parser.refs
    if path.suffix.lower() == '.css':
        return css_refs(text)
    refs: list[Reference] = []
    history_level = None
    fence = None
    definitions = {}
    for line in text.splitlines():
        match = re.match(r'^\s{0,3}\[([^\]]+)\]:\s*(?:<([^>]+)>|(\S+))', line)
        if match:
            definitions[match[1].casefold()] = match[2] or match[3]
    for number, line in enumerate(text.splitlines(), 1):
        heading = re.match(r'^(#{1,6})\s+(.+)', line)
        if heading and not fence:
            level = len(heading[1])
            if history_level is not None and level <= history_level:
                history_level = None
            if HISTORY.match(heading[2].strip()):
                history_level = level
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            if fence is None:
                fence = marker[1]
            elif marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
            continue
        context = 'history' if history_level else ('example' if fence else 'active')
        values = []
        # Explicit links including angle-delimited paths containing spaces.
        values.extend(m[1] or m[2] for m in re.finditer(
            r'!?\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[\'"][^\n]*?[\'"])?\s*\)', line))
        for m in re.finditer(r'!?\[([^\]]+)\](?:\[([^\]]*)\])?', line):
            key = (m[2] or m[1]).casefold()
            if key in definitions:
                values.append(definitions[key])
        # Do not extract truncated copies of paths already present in links.
        for m in PATH.finditer(line):
            if not any(m[0] in value for value in values):
                values.append(m[0].rstrip('.'))
        refs.extend(Reference(number, value, context) for value in dict.fromkeys(values))
    return refs


def lexical(path: Path) -> Path:
    return Path(os.path.abspath(path))


def safe_path(path: Path, root: Path) -> bool:
    if not path.is_relative_to(root):
        return False
    return not any(p.is_symlink() for p in [path, *path.parents] if p.is_relative_to(root))


def documents(directory: Path, root: Path):
    if not safe_path(directory, root) or not directory.is_dir():
        return
    for base, dirs, files in os.walk(directory, followlinks=False):
        dirs[:] = [d for d in sorted(dirs) if d not in {'.git', 'node_modules', 'assets-generated'}
                   and not (Path(base) / d).is_symlink()]
        for name in sorted(files):
            path = Path(base) / name
            if path.suffix.lower() in TEXT_SUFFIXES and safe_path(path, root):
                yield path


def related_documents(root: Path, issue: Path, change_ids: list[str]) -> set[Path]:
    result: set[Path] = set()
    for change in change_ids:
        if not re.fullmatch(r'[\w.-]+', change):
            continue
        active = root / 'openspec/changes' / change
        dirs = [active, *sorted((root / 'openspec/archive').glob(f'*-{change}'))]
        for directory in dirs:
            result.update(documents(directory, root))
    for stage in ('change', 'archive'):
        for sprint in sorted((root / 'iterations' / stage).glob('sprint-*/sprint.yaml')):
            if safe_path(sprint, root) and re.search(
                rf'(?<![\w-]){re.escape(issue.name)}(?![\w-])', sprint.read_text(encoding='utf-8')):
                for name in ('sprint.yaml', 'sprint.md', 'release-note.md', 'acceptance-report.md'):
                    p = sprint.parent / name
                    if p.is_file() and safe_path(p, root):
                        result.add(p)
    return result


def check_references(root: Path, source: Path, target: Path,
                     change_ids: list[str] | None = None) -> list[Finding]:
    """Simulate source -> target without writes; source == target checks actual state."""
    root, source, target = map(lexical, (root, source, target))
    moving = source != target
    findings: list[Finding] = []

    def display(path: Path) -> str:
        return path.relative_to(root).as_posix() if path.is_relative_to(root) else '[outside-repository]'

    def mapped(path: Path) -> Path:
        return target / path.relative_to(source) if path.is_relative_to(source) else path

    def physical_after(path: Path) -> Path | None:
        if moving and path.is_relative_to(target):
            return source / path.relative_to(target)
        if moving and path.is_relative_to(source):
            return None
        return path

    pending = sorted(set(documents(source, root)) | related_documents(root, source, change_ids or []))
    visited: set[Path] = set()
    resource_paths: set[Path] = set()
    while pending:
        path = pending.pop(0)
        if path in visited:
            continue
        visited.add(path)
        is_resource = 'prototype' in path.relative_to(source).parts if path.is_relative_to(source) else False
        # Only recursively queued HTML/CSS outside prototype are resource contexts.
        is_resource = is_resource or path.suffix.lower() in {'.html', '.htm', '.css'}
        try:
            text = path.read_text(encoding='utf-8')
        except (OSError, UnicodeError):
            findings.append(Finding(display(path), 1, '[unreadable]', display(path), 'unreadable', True))
            continue
        extracted = references(path, text)
        for ref in extracted:
            value = unescape(ref.value).strip()
            try:
                url = urlsplit(value)
            except ValueError:
                findings.append(Finding(display(path), ref.line, '[invalid-url]', '', 'invalid-reference', True))
                continue
            decoded = unquote(url.path)
            base = root if decoded.startswith(('issues/', 'openspec/', 'iterations/')) else path.parent
            resolved = lexical(base / decoded)
            relevant = is_resource or 'prototype' in decoded.split('/')
            if not path.is_relative_to(source):
                # Include old stage paths on retries/post-checks, but not other Issues.
                parts = resolved.relative_to(root).parts if resolved.is_relative_to(root) else ()
                owned = any(parts[i:i + 2] == (source.name, 'prototype') for i in range(len(parts) - 1))
                relevant = relevant and owned
                # Resources reached from prototype are handled below through queue ownership.
                if path in resource_paths:
                    relevant = True
            if not relevant:
                continue
            shown = decoded if not decoded.startswith('/') else '[absolute-reference]'
            if ref.context != 'active':
                findings.append(Finding(display(path), ref.line, shown, display(resolved), ref.context))
                continue
            if url.scheme or url.netloc:
                findings.append(Finding(display(path), ref.line, '[external-reference]', '', 'external-skipped'))
                continue
            if not decoded or value.startswith('#'):
                continue
            if any(token in value for token in ('${', '{{', '<%', '*')):
                findings.append(Finding(display(path), ref.line, '[dynamic-reference]', '', 'dynamic-skipped'))
                continue
            if decoded.startswith('/'):
                findings.append(Finding(display(path), ref.line, '[root-relative-reference]', '', 'root-relative-unresolved'))
                continue
            after_base = root if base == root else mapped(path).parent
            after = lexical(after_base / decoded)
            actual = physical_after(after)
            if not safe_path(resolved, root) or (actual is not None and not safe_path(actual, root)):
                findings.append(Finding(display(path), ref.line, shown, display(after), 'unsafe-path', True))
                continue
            if actual is None or not actual.exists():
                reason = 'migration-break' if resolved.exists() and moving else 'existing-missing'
                findings.append(Finding(display(path), ref.line, shown, display(after), reason, True))
            elif actual.is_file() and actual.suffix.lower() in {'.html', '.htm', '.css'}:
                resource_paths.add(actual)
                pending.append(actual)
    return list(dict.fromkeys(findings))
