"""Bounded second-pass scheduling retains complete reads and global limits."""
import os
from concurrent.futures import ThreadPoolExecutor

import pytest
from app.governance import snapshot, read_snapshot
from test_governance_scope import fixture_tree


def tree(path, count=20):
    root = fixture_tree(path)
    for n in range(count):
        folder = root / 'openspec/archive' / f'group-{n}'
        folder.mkdir(parents=True)
        (folder / 'proof.md').write_text(f'document {n}')
    return root


@pytest.mark.parametrize('workers', [2, 4])
def test_parallel_complete_bytes_and_metadata_equal_serial(tmp_path, workers):
    root = tree(tmp_path / 'repo')
    first, second = {}, {}
    serial = snapshot.read_once(root, identities=first)
    parallel = snapshot.read_once(root, identities=second, workers=workers)
    assert parallel == serial and second == first


@pytest.mark.parametrize('kind', ['symlink', 'hardlink', 'fifo'])
def test_parallel_rejects_unsafe_entries(tmp_path, kind):
    root = tree(tmp_path / 'repo')
    target = root / 'openspec/archive/group-0/bad.md'
    source = root / 'openspec/archive/group-0/proof.md'
    if kind == 'symlink': target.symlink_to(source)
    elif kind == 'hardlink': os.link(source, target)
    else: os.mkfifo(target)
    with pytest.raises(ValueError): snapshot.read_once(root, workers=4)


@pytest.mark.parametrize('limit,value', [('LIMIT_COUNT', 10), ('LIMIT_TOTAL', 40), ('LIMIT_FILE', 3)])
def test_parallel_limits_are_shared_across_partitions(tmp_path, monkeypatch, limit, value):
    root = tree(tmp_path / 'repo')
    monkeypatch.setattr(snapshot, limit, value)
    with pytest.raises(ValueError): snapshot.read_once(root, workers=4)


def test_reader_only_parallelizes_warm_second_pass_and_retries_serially(tmp_path, monkeypatch):
    root = tree(tmp_path / 'repo', 260)
    read_snapshot.clear()
    monkeypatch.setattr(read_snapshot, 'read_workers', lambda: 4)
    original = snapshot.read_once
    calls = []
    def read(*args, **kwargs):
        calls.append(kwargs.get('workers', 1))
        return original(*args, **kwargs)
    monkeypatch.setattr(snapshot, 'read_once', read)
    read_snapshot.stable_read(root, 'binding')
    assert calls == [1, 1]
    calls.clear()
    read_snapshot.stable_read(root, 'binding')
    assert calls == [4]
    calls.clear()
    (root / 'openspec/archive/group-0/proof.md').write_text('changed')
    read_snapshot.stable_read(root, 'binding')
    assert calls == [4, 1, 1]
    calls.clear()
    snapshot.stable(root)
    assert calls == [1, 1]
    read_snapshot.clear()


def test_parallel_requests_keep_independent_maps_and_limits(tmp_path):
    roots = [tree(tmp_path / str(n), 30) for n in range(4)]
    for n, root in enumerate(roots): (root / 'docs').mkdir(exist_ok=True); (root / 'docs/owner.md').write_text(str(n))
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(lambda root: snapshot.read_once(root, workers=4), roots))
    assert [row['docs/owner.md'] for row in rows] == [b'0', b'1', b'2', b'3']


def test_worker_limit_cannot_expand(tmp_path):
    with pytest.raises(ValueError): snapshot.read_once(tmp_path, workers=8)


@pytest.mark.parametrize('quota,affinity,expected', [('max 100000',8,2),('200000 100000',8,1),('400000 100000',8,2),('800000 100000',2,1),('bad',8,1),('max 0',8,1)])
def test_read_workers_respects_actual_cpu_budget(monkeypatch, quota, affinity, expected):
    monkeypatch.setattr(os, 'sched_getaffinity', lambda _: set(range(affinity)), raising=False)
    monkeypatch.setattr(read_snapshot.Path, 'read_text', lambda _: quota)
    assert read_snapshot.read_workers() == expected


def test_unknown_capacity_keeps_serial_reader(monkeypatch):
    def missing(_): raise OSError('unavailable')
    monkeypatch.setattr(os, 'sched_getaffinity', missing, raising=False)
    assert read_snapshot.read_workers() == 1


def test_limit_failure_stops_queued_partitions(tmp_path, monkeypatch):
    from threading import Lock
    root = tree(tmp_path / 'repo', 260)
    monkeypatch.setattr(snapshot, 'LIMIT_COUNT', 3)
    original, calls, lock = snapshot.read_body, [], Lock()
    def read(*args):
        with lock: calls.append(1)
        return original(*args)
    monkeypatch.setattr(snapshot, 'read_body', read)
    with pytest.raises(ValueError): snapshot.read_once(root, workers=4)
    # At most the admitted files plus the four already-running bounded reads.
    assert len(calls) <= snapshot.LIMIT_COUNT + 4
