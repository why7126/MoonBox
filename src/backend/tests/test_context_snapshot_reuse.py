"""Byte reuse is never sufficient evidence without a complete second read."""
import os
from concurrent.futures import ThreadPoolExecutor

import pytest
from app.chat.service import ChatError
from app.governance import read_snapshot as cache, snapshot
from test_governance_scope import fixture_tree


@pytest.fixture(autouse=True)
def reset_cache():
    cache.clear()
    yield
    cache.clear()


def test_warm_reuses_first_pass_but_always_reads_second(tmp_path, monkeypatch):
    root = fixture_tree(tmp_path / 'repo')
    original = snapshot.read_body
    calls = []
    def opened(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)
    monkeypatch.setattr(snapshot, 'read_body', opened)
    first = cache.stable_read(root, 'binding')
    assert len(calls) == 4
    calls.clear()
    assert cache.stable_read(root, 'binding') == first
    assert len(calls) == 2
    calls.clear()
    assert cache.stable_read(root, 'binding', enabled=False) == first
    assert len(calls) == 4


@pytest.mark.parametrize('folder', snapshot.ROOTS)
def test_all_roots_same_size_change_rename_delete(tmp_path, folder):
    root = fixture_tree(tmp_path / 'repo')
    directory = root / folder
    directory.mkdir(exist_ok=True)
    doc = directory / 'sample.md'
    doc.write_text('first')
    first = cache.stable_read(root, 'binding')
    info = doc.stat()
    doc.write_text('other')
    os.utime(doc, ns=(info.st_atime_ns, info.st_mtime_ns))
    changed = cache.stable_read(root, 'binding')
    assert changed.revision != first.revision
    assert changed.files[f'{folder}/sample.md'] == b'other'
    doc.rename(directory / 'renamed.md')
    assert f'{folder}/sample.md' not in cache.stable_read(root, 'binding').files
    (directory / 'renamed.md').unlink()
    assert f'{folder}/renamed.md' not in cache.stable_read(root, 'binding').files


def test_even_identical_metadata_cannot_validate_stale_bytes(tmp_path, monkeypatch):
    root = fixture_tree(tmp_path / 'repo')
    doc = root / 'issues/sample.md'
    doc.write_text('first')
    # Simulate a filesystem that fails to advance metadata at all.
    monkeypatch.setattr(snapshot, 'file_identity', lambda info: ('coarse',))
    cache.stable_read(root, 'binding')
    doc.write_text('other')
    assert cache.stable_read(root, 'binding').files['issues/sample.md'] == b'other'


def test_warm_links_invalid_registry_recovery_and_limits(tmp_path, monkeypatch):
    root = fixture_tree(tmp_path / 'repo')
    cache.stable_read(root, 'binding')
    link = root / 'issues/link.md'
    link.symlink_to(tmp_path / 'secret')
    with pytest.raises(ChatError) as failure:
        cache.stable_read(root, 'binding')
    assert failure.value.kind == 'source_unavailable'
    link.unlink()
    registry = root / 'issues/bugs/_registry.yaml'
    registry.write_text('entries: [')
    with pytest.raises(ChatError) as failure:
        cache.stable_read(root, 'binding')
    assert failure.value.kind == 'source_invalid'
    registry.write_text('entries: []\n')
    cache.stable_read(root, 'binding')
    monkeypatch.setattr(snapshot, 'LIMIT_TOTAL', 1)
    with pytest.raises(ChatError):
        cache.stable_read(root, 'binding')


def test_bounds_binding_and_concurrent_projects(tmp_path, monkeypatch):
    roots = [fixture_tree(tmp_path / str(n)) for n in range(4)]
    for n, root in enumerate(roots):
        (root / 'issues/sample.md').write_text(str(n))
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda root: cache.stable_read(root, 'binding'), roots))
    assert [r.files['issues/sample.md'] for r in results] == [b'0', b'1', b'2', b'3']
    assert len(cache._versions) == 2
    assert sum(row[1] for row in cache._versions.values()) <= cache.MAX_BYTES
    monkeypatch.setattr(cache, 'MAX_BYTES', 1)
    cache.clear()
    cache.stable_read(roots[0], 'new-binding')
    assert not cache._versions


def test_direct_reader_handles_short_reads_and_growth(tmp_path, monkeypatch):
    path = tmp_path / 'source.md'
    path.write_bytes(b'abcdefgh')
    original = os.read
    monkeypatch.setattr(os, 'read', lambda fd, count: original(fd, min(count, 2)))
    fd = os.open(path, os.O_RDONLY)
    try:
        # The advertised size may be stale; the reader must reach EOF.
        assert snapshot.read_body(fd, 3) == b'abcdefgh'
    finally:
        os.close(fd)


def test_digest_reuse_requires_complete_byte_equality(tmp_path, monkeypatch):
    root = fixture_tree(tmp_path / 'repo')
    first = cache.stable_read(root, 'binding')
    original = snapshot.digest
    calls = []
    def digest(files):
        calls.append(1)
        return original(files)
    monkeypatch.setattr(snapshot, 'digest', digest)
    assert cache.stable_read(root, 'binding') == first
    assert not calls
    (root / 'issues/new.md').write_text('new')
    assert cache.stable_read(root, 'binding').revision != first.revision
    assert len(calls) == 1


def test_returned_mapping_cannot_poison_cached_digest(tmp_path):
    root = fixture_tree(tmp_path / 'repo')
    doc = root / 'issues/sample.md'
    doc.write_text('first')
    first = cache.stable_read(root, 'binding')
    first.files['issues/sample.md'] = b'other'
    doc.write_text('other')
    second = cache.stable_read(root, 'binding')
    assert second.revision != first.revision
    assert second.revision == snapshot.digest(second.files)


@pytest.mark.parametrize('replacement', ['hardlink', 'fifo', 'symlink'])
def test_cached_candidate_never_bypasses_full_file_safety(tmp_path, replacement):
    root = fixture_tree(tmp_path / 'repo')
    doc = root / 'issues/sample.md'
    doc.write_text('same bytes')
    cache.stable_read(root, 'binding')
    doc.unlink()
    other = tmp_path / 'other.md'
    other.write_text('same bytes')
    if replacement == 'hardlink':
        os.link(other, doc)
    elif replacement == 'fifo':
        os.mkfifo(doc)
    else:
        doc.symlink_to(other)
    with pytest.raises(ChatError) as failure:
        cache.stable_read(root, 'binding')
    assert failure.value.kind == 'source_unavailable'


@pytest.mark.parametrize('folder', snapshot.ROOTS)
def test_cached_candidate_rejects_replaced_scan_root(tmp_path, folder):
    root = fixture_tree(tmp_path / 'repo')
    directory = root / folder
    directory.mkdir(exist_ok=True)
    (directory / 'sample.md').write_text('same bytes')
    cache.stable_read(root, 'binding')
    replacement = tmp_path / 'replacement'
    directory.rename(replacement)
    directory.symlink_to(replacement, target_is_directory=True)
    with pytest.raises(ChatError) as failure:
        cache.stable_read(root, 'binding')
    assert failure.value.kind == 'source_unavailable'


def test_changed_candidate_requires_two_equal_fresh_reads(tmp_path, monkeypatch):
    root = fixture_tree(tmp_path / 'repo')
    doc = root / 'issues/sample.md'
    doc.write_text('old')
    previous = cache.stable_read(root, 'binding')
    doc.write_text('new-a')
    original = snapshot.read_once
    reads = []
    def changing(*args, **kwargs):
        result = original(*args, **kwargs)
        reads.append(result['issues/sample.md'])
        doc.write_text('new-b' if len(reads) % 2 else 'new-a')
        return result
    monkeypatch.setattr(snapshot, 'read_once', changing)
    with pytest.raises(ChatError) as failure:
        cache.stable_read(root, 'binding')
    assert failure.value.kind == 'source_changing'
    assert len(reads) == 5  # one rejected fresh candidate, then two full pairs
    assert cache._versions[(str(root), 'binding')][2].revision == previous.revision
    monkeypatch.setattr(snapshot, 'read_once', original)
    recovered = cache.stable_read(root, 'binding')
    assert recovered.files['issues/sample.md'] == doc.read_bytes()
    assert recovered.revision != previous.revision
