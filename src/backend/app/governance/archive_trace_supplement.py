"""Immutable supplements for a closed source trace's appended bug index."""
import json
import re
import os
import tempfile
from pathlib import Path


def location(root, change):
    from .archive_closure_restoration import receipt_path
    return receipt_path(root, change).parent / 'trace-supplements' / (change + '.json')


def validate(root, change, receipt, expected, record):
    from .archive_closure_restoration import digest, safe_file
    from .archive_finalization import metadata
    from .archive_recovery import archive_paths, completed_archive
    if record.get('receipt_sha256') != digest(receipt):
        raise ValueError('trace supplement receipt changed')
    original = json.loads(receipt)['proof']
    changed = [p for p in set(original['sources']) | set(expected['sources'])
               if original['sources'].get(p) != expected['sources'].get(p)]
    path = record.get('source', '')
    if changed != [path] or not re.fullmatch(r'issues/requirements/archive/REQ-\d{4}-[a-z0-9-]+/trace.md', path):
        raise ValueError('trace supplement source mismatch')
    old = record.get('original_text', '')
    current = safe_file(root, root / path)
    if digest(old.encode()) != original['sources'][path] or digest(current) != record.get('current_sha256'):
        raise ValueError('trace supplement source hash mismatch')
    projected = dict(expected, sources=dict(expected['sources']))
    projected['sources'][path] = original['sources'][path]
    if projected != original:
        raise ValueError('trace supplement other proof changed')
    text = current.decode()
    marker = '\n\n## 关联缺陷\n\n'
    if marker in old or text.count(marker) != 1:
        raise ValueError('trace supplement requires appended index')
    body, table = text.split(marker)
    old_time = re.findall(r'^updated_at:.*$', old, re.M)
    if len(old_time) != 1:
        raise ValueError('trace supplement original timestamp missing')
    restored = re.sub(r'^updated_at:.*$', lambda _: old_time[0], body, flags=re.M) + '\n'
    if restored != old:
        raise ValueError('trace supplement unknown prose change')
    rows = table.strip().splitlines()
    if rows[:2] != ['| BUG | 严重等级 | 状态 | 关联 Change | 说明 |', '|---|---|---|---|---|'] or len(rows) < 3:
        raise ValueError('trace supplement invalid index')
    seen = set()
    for row in rows[2:]:
        cells = [v.strip() for v in row.split('|')]
        if len(cells) != 7 or cells[0] or cells[-1]:
            raise ValueError('trace supplement invalid row')
        bug, severity, status, cid, title = cells[1:-1]
        if not re.fullmatch(r'BUG-\d{4}-[a-z0-9-]+', bug) or bug in seen or status != 'done':
            raise ValueError('trace supplement bug not closed')
        seen.add(bug)
        trace = root / 'issues/bugs/archive' / bug / 'trace.md'
        safe_file(root, trace)
        meta = metadata(trace)
        if meta.get('status') != 'done' or meta.get('related_requirement') != Path(path).parent.name:
            raise ValueError('trace supplement bug ownership mismatch')
        links = [v.get('change_id') if isinstance(v, dict) else v for v in meta.get('openspec_changes', [])]
        links += [meta.get('related_change')]
        folders = archive_paths(root, cid)
        if cid not in links or len(folders) != 1 or not completed_archive(folders[0], cid):
            raise ValueError('trace supplement bug archive invalid')
    return expected


def verify(root, change, receipt, expected):
    from .archive_closure_restoration import safe_file
    try:
        raw = safe_file(root, location(root, change))
    except FileNotFoundError as exc:
        raise ValueError("closure restoration binding differs; supplement missing") from exc
    if len(raw) > 256 * 1024:
        raise ValueError('oversized trace supplement')
    return validate(root, change, receipt, expected, json.loads(raw))


def create(root, change, original_text, apply=False):
    from .archive_closure_restoration import safe_file, receipt_path, digest, proof
    receipt = safe_file(root, receipt_path(root, change))
    expected = proof(root, change)
    old = json.loads(receipt)['proof']
    changed = [p for p in old['sources'] if old['sources'][p] != expected['sources'].get(p)]
    if len(changed) != 1:
        raise ValueError('trace supplement requires one changed source')
    record = dict(schema_version=1, receipt_sha256=digest(receipt), source=changed[0],
                  original_text=original_text, current_sha256=expected['sources'][changed[0]])
    validate(root, change, receipt, expected, record)
    target = location(root, change)
    if target.exists() or target.is_symlink():
        verify(root, change, receipt, expected)
        return {'status': 'unchanged'}
    if not apply:
        return {'status': 'ready'}
    if any(p.is_symlink() for p in (target.parent, *target.parents)):
        raise ValueError('unsafe supplement path')
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=target.parent, delete=False) as handle:
        temporary = Path(handle.name)
        json.dump(record, handle, ensure_ascii=False, sort_keys=True)
        handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
    try:
        if safe_file(root, receipt_path(root, change)) != receipt or proof(root, change) != expected:
            raise ValueError('trace supplement inputs changed')
        os.link(temporary, target)
    finally:
        temporary.unlink()
    verify(root, change, receipt, expected)
    return {'status': 'created', 'path': target.relative_to(root).as_posix()}
