"""BUG-0056: request-local identity and archive lookup equivalence."""
from pathlib import Path
import json
from time import perf_counter

import pytest
import yaml

from app.chat.service import ChatError
from app.governance import execution_context as execution
from app.governance.snapshot import Snapshot
from app.services import requirement_center as legacy


def snapshot(ids):
    return Snapshot({f'issues/{folder}/_registry.yaml': yaml.safe_dump({'entries': [
        {'id': oid} for oid in ids if oid.startswith(prefix)
    ]}).encode() for folder, prefix in [('requirements', 'REQ-'), ('bugs', 'BUG-')]}, 'version')


def test_identity_equivalence_106_and_parse_count(monkeypatch):
    ids = [f'{kind}-{n:04d}-sample' for kind in ('REQ', 'BUG') for n in range(53)]
    source = snapshot(ids)
    started = perf_counter()
    expected = [execution.canonical_id(source, '-'.join(oid.split('-')[:2])) for oid in ids]
    baseline_ms = (perf_counter() - started) * 1000
    original = execution.safe_load
    calls = []
    def read(body):
        calls.append(1)
        return original(body)
    monkeypatch.setattr(execution, 'safe_load', read)
    started = perf_counter()
    index = execution.IdentityIndex(source)
    assert [index.resolve('-'.join(oid.split('-')[:2])) for oid in ids] == expected
    assert [index.resolve(oid) for oid in ids] == ids
    assert len(calls) == 2
    print('INDEX_BENCHMARK ' + json.dumps({'kind': 'identity', 'n': 106,
        'baseline_ms': baseline_ms, 'optimized_ms': (perf_counter()-started)*1000,
        'registry_parses': len(calls), 'equal': True}))


@pytest.mark.parametrize('ids,oid', [
    (['REQ-0001-one', 'REQ-0001-two'], 'REQ-0001'),
    (['REQ-0001', 'REQ-0001-two'], 'REQ-0001'),
    (['REQ-0001-one'], 'REQ-0002'),
])
def test_identity_ambiguity_and_deletion(ids, oid):
    source = snapshot(ids)
    for index in (None, execution.IdentityIndex(source)):
        with pytest.raises(ChatError) as error:
            execution.canonical_id(source, oid, index)
        assert (error.value.code, error.value.kind) == (2604, 'governance_validation_failed')


def test_identity_snapshot_isolation_and_invalid_recovery():
    old = snapshot(['BUG-0001-old'])
    new = snapshot(['BUG-0001-new'])
    index = execution.IdentityIndex(old)
    assert index.resolve('BUG-0001') == 'BUG-0001-old'
    with pytest.raises(ValueError):
        execution.canonical_id(new, 'BUG-0001', index)
    assert execution.IdentityIndex(new).resolve('BUG-0001') == 'BUG-0001-new'
    broken = Snapshot({'issues/bugs/_registry.yaml': b'entries: ['}, 'bad')
    with pytest.raises(yaml.YAMLError):
        execution.IdentityIndex(broken).resolve('BUG-0001')
    assert execution.IdentityIndex(new).resolve('plain-change') == 'plain-change'


def test_archive_171_equivalence_once_and_isolation(tmp_path, monkeypatch):
    archive = tmp_path / 'openspec/archive'
    archive.mkdir(parents=True)
    ids = [f'change-{n}' for n in range(171)]
    for cid in ids:
        (archive / f'2026-10-01-{cid}').mkdir()
    (archive / '2026-10-02-change-1').mkdir()
    active = tmp_path / 'openspec/changes/change-2'
    active.mkdir(parents=True)
    (archive / '2026-10-01-escape').symlink_to(tmp_path, target_is_directory=True)
    ids += ['missing', 'escape']
    started = perf_counter()
    with legacy.using_governance_root(tmp_path):
        expected = [legacy._change_dir(cid) for cid in ids]
    baseline_ms = (perf_counter()-started)*1000
    original = Path.glob
    scans = []
    def glob(path, pattern):
        if path == archive:
            scans.append(1)
        return original(path, pattern)
    monkeypatch.setattr(Path, 'glob', glob)
    started = perf_counter()
    with legacy.using_governance_root(tmp_path, immutable=True):
        assert [legacy._change_dir(cid) for cid in ids] == expected
        assert legacy._change_dir('change-2') == active
        with pytest.raises(PermissionError):
            legacy._change_dir('../../escape')
    assert len(scans) == 1
    print('INDEX_BENCHMARK ' + json.dumps({'kind': 'archive', 'n': 171,
        'baseline_ms': baseline_ms, 'optimized_ms': (perf_counter()-started)*1000,
        'directory_scans': len(scans), 'equal': True}))
    (archive / '2026-10-01-change-0').rename(archive / '2026-10-02-change-0')
    with legacy.using_governance_root(tmp_path, immutable=True):
        assert legacy._change_dir('change-0').name == '2026-10-02-change-0'


def test_read_only_projection_borrows_without_copying_or_leaking(tmp_path, monkeypatch):
    root = tmp_path
    registry = root / 'issues/bugs/_registry.yaml'
    registry.parent.mkdir(parents=True)
    issue = registry.parent / 'review/BUG-0001-sample'
    issue.mkdir(parents=True)
    registry.write_text('entries:\n- id: BUG-0001-sample\n  path: issues/bugs/review/BUG-0001-sample\n')
    sprint = root / 'iterations/change/sprint-001'
    sprint.mkdir(parents=True)
    (sprint / 'sprint.yaml').write_text('bugs: [BUG-0001-sample]\n')
    (sprint / 'sprint.md').write_text('# Sprint')
    entry = {'id': 'BUG-0001-sample', 'iteration': 'sprint-001'}
    with legacy.using_governance_root(root):
        expected = legacy._sprint_document(entry, {})
    copied = []
    original = legacy.deepcopy
    def copy(value):
        copied.append(1)
        return original(value)
    monkeypatch.setattr(legacy, 'deepcopy', copy)
    with legacy.using_governance_root(root, immutable=True):
        for _ in range(20):
            assert legacy._sprint_document(entry, {}) == expected
            assert legacy._find_issue_dir('BUG-0001-sample') == issue
        assert len(copied) == 2  # Populate once per file, no repeated full copies.
        public_copy = legacy._read_yaml(registry)
        public_copy['entries'].clear()
        assert legacy._find_issue_dir('BUG-0001-sample') == issue
    registry.write_text('entries: []\n')
    with legacy.using_governance_root(root, immutable=True):
        assert legacy._find_issue_dir('BUG-0001-sample') is None


def test_cold_validation_and_identity_share_each_registry_parse(tmp_path, monkeypatch):
    from app.governance import snapshot as snapshots, read_snapshot
    from test_governance_scope import fixture_tree
    root = fixture_tree(tmp_path / 'repo')
    snapshots._validated.clear()
    read_snapshot.clear()
    calls = []
    original = yaml.load
    def load(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)
    monkeypatch.setattr(yaml, 'load', load)
    for _ in range(2):
        calls.clear()
        source = read_snapshot.stable_read(root, 'registry-once')
        index = execution.IdentityIndex(source)
        index.registry('requirements')
        index.registry('bugs')
        assert len(calls) == 2  # Cold validation + identity, and warmed identity.
    assert all(record[2].registries is None for record in read_snapshot._versions.values())
    read_snapshot.clear()
