"""Resolve retained archive references across a proven Issue lifecycle move."""
from pathlib import Path
import re
import yaml

from .archive_recovery import archive_paths, recovery_admission


def safe(root: Path, path: Path) -> bool:
    return path.is_relative_to(root) and not any(p.is_symlink() for p in (path, *path.parents))


def resolve(root: Path, document: Path, original: Path, *, source: Path | None = None,
            target: Path | None = None) -> Path | None:
    """Only immutable archived documents may retain old-stage references.

    Mutable Issue/active Change links still need correction. A planned move is
    checked against the same source bytes; post-move resolution requires a unique
    archived Issue, done status and reciprocal ownership of the originating Change.
    """
    if not all(safe(root, p) for p in (document, original)):
        return None
    parts = document.relative_to(root).parts
    if len(parts) < 4 or parts[:2] != ('openspec', 'archive') or not re.fullmatch(r'\d{4}-\d{2}-\d{2}-.+', parts[2]):
        return None
    change = parts[2][11:]
    folder = root.joinpath(*parts[:3])
    if archive_paths(root, change) != [folder]:
        return None
    ref = original.relative_to(root).parts
    if len(ref) < 4 or ref[0] != 'issues' or ref[1] not in {'requirements', 'bugs'} or ref[2] not in {'plan', 'review'}:
        return None
    if not re.fullmatch(r'(?:REQ|BUG)-\d+-[a-z0-9-]+', ref[3]):
        return None
    base = root / 'issues' / ref[1]
    old = base / ref[2] / ref[3]
    destination = base / 'archive' / ref[3]
    planning = source == old and target == destination
    present = [p for p in [base / ref[3], *(base / stage / ref[3] for stage in ('plan', 'review', 'archive'))]
               if p.exists() or p.is_symlink()]
    actual_issue = old if planning else destination
    if present != [actual_issue] or not safe(root, actual_issue):
        return None
    trace = actual_issue / 'trace.md'
    if not safe(root, trace) or not trace.is_file():
        return None
    chunks = trace.read_text().split('---', 2)
    meta = yaml.safe_load(chunks[1]) if len(chunks) == 3 and not chunks[0].strip() else {}
    if not isinstance(meta, dict) or meta.get('status') != 'done':
        return None
    if meta.get('lifecycle_stage') != ('review' if planning and ref[2] == 'review' else 'plan' if planning else 'archive'):
        return None
    links = [v.get('change_id') if isinstance(v, dict) else v for v in meta.get('openspec_changes', [])]
    links += meta.get('related_changes') or []
    if meta.get('related_change'): links.append(meta['related_change'])
    if change not in links:
        return None
    for cid in links:
        if not isinstance(cid, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,100}', cid):
            return None
        if len(archive_paths(root, cid)) != 1 or (root / 'openspec/changes' / cid).exists():
            return None
    proof = recovery_admission(root, change)
    if not proof.get('ready') or proof.get('mode') != 'archived':
        return None
    actual = actual_issue.joinpath(*ref[4:])
    if not safe(root, actual) or not actual.exists():
        return None
    return destination.joinpath(*ref[4:])
