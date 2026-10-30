"""Explicit sustained HTTP resource test; synthetic identities, frozen documents."""
import importlib.util
import json
import os
from pathlib import Path
import resource
import statistics
import sys
import time
from threading import Event, Thread
from concurrent.futures import ThreadPoolExecutor

import pytest
import yaml
from sqlalchemy import event, text
from test_chat import chat
from test_governance_scope import bind
from app.governance import snapshot, read_snapshot, read_memo, reader
from app.services import requirement_center as legacy


@pytest.fixture
def sustained_client(chat):
    """Keep one server loop alive, as a deployed ASGI worker does.

    TestClient without a portal creates new loop/worker threads per request.
    Their allocator arenas contaminate sustained server RSS observations.
    The synthetic database is already initialized by chat; do not run the
    application's production lifespan against a real configured database.
    """
    from anyio.from_thread import start_blocking_portal
    client, factory = chat
    with start_blocking_portal() as portal:
        client.portal = portal
        try:
            yield client, factory
        finally:
            client.portal = None


def baseline_reader(directory, monkeypatch):
    def load(name, filename):
        spec = importlib.util.spec_from_file_location('app.governance.' + name, directory / filename)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    old = load('_context_baseline_reader', 'reader.py')
    old_snapshot = load('_context_baseline_snapshot', 'snapshot.py')
    old_execution = load('_context_baseline_execution', 'execution_context.py')
    old_titles = load('_context_baseline_titles', 'titles.py')
    old_legacy = load('_context_baseline_legacy', 'requirement_center.py')
    old_legacy._SCOPED_ROOT = legacy._SCOPED_ROOT
    old.stable = old_snapshot.stable
    old.legacy = old_legacy
    old_execution.legacy = old_legacy
    old.ProjectReader._baseline_stage_map = staticmethod(old_execution.stage_map)
    old.ProjectReader._baseline_read_title = staticmethod(old_titles.read_title)
    class CompatibleBaseline(old.ProjectReader):
        def call(self, name, *args, **kwargs):
            # The retained implementation predates the additive read selector.
            # Its workload remains the original full read, not a summary shim.
            kwargs.pop('summary', None)
            kwargs.pop('check_object_id', None)
            return super().call(name, *args, **kwargs)
    old.ProjectReader = CompatibleBaseline
    for name in ('_read_yaml', '_frontmatter', '_change_dir', '_change_tasks', '_change_document_names', '_change_spec_paths'):
        monkeypatch.setattr(legacy, name, getattr(old_legacy, name))
    return old.ProjectReader


def database_columns(factory):
    with factory() as db:
        for name, kind in [('code', 'TEXT'), ('description', 'TEXT'), ('member_count', 'INTEGER'), ('created_at', 'TEXT')]:
            db.execute(text(f'ALTER TABLE admin_spaces ADD COLUMN {name} {kind}'))
        for name in ('username', 'nickname'):
            db.execute(text(f'ALTER TABLE admin_users ADD COLUMN {name} TEXT'))
        db.execute(text('CREATE TABLE admin_space_products (space_id TEXT)'))
        db.commit()


def expand_to_limits(root, source):
    """Legal archives and documents at both existing snapshot hard limits."""
    extra = []
    count = snapshot.LIMIT_COUNT - len(source.files)
    for n in range(count // 3):
        directory = root / f'openspec/archive/2026-10-27-scale-{n}'
        directory.mkdir(parents=True)
        for name, body in [('trace.md', '---\nstatus: archived\n---\n'),
                           ('proposal.md', '---\ntitle: 扩容合成样本\n---\n# 扩容合成样本\n'),
                           ('tasks.md', '- [x] 合成任务\n')]:
            target = directory / name
            target.write_text(body)
            extra.append(target)
    for n in range(count % 3):
        target = root / f'docs/scale-{n}.md'
        target.parent.mkdir(exist_ok=True)
        target.write_text('')
        extra.append(target)
    remaining = snapshot.LIMIT_TOTAL - sum(map(len, source.files.values())) - sum(p.stat().st_size for p in extra)
    for target in extra:
        size = min(remaining, snapshot.LIMIT_FILE - target.stat().st_size)
        with target.open('ab') as stream:
            stream.write(b'x' * size)
        remaining -= size
    assert remaining == 0
    return extra


@pytest.mark.skipif(os.environ.get('CONTEXT_RESOURCE_TEST') != '1', reason='explicit 30 minute isolated resource run')
def test_sustained(sustained_client, tmp_path, monkeypatch):
    client, factory = sustained_client
    database_columns(factory)
    source = snapshot.stable(Path(os.environ['BUG_READ_SOURCE']))
    root = tmp_path / 'source'
    for name, body in source.files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
    expanded = os.environ.get('CONTEXT_RESOURCE_SCALE') == 'expanded'
    if expanded:
        expand_to_limits(root, source)
    fixed = snapshot.stable(root)
    bind(monkeypatch, root)
    mode = os.environ.get('CONTEXT_RESOURCE_MODE', 'optimized')
    if mode == 'baseline':
        from app.api.v1 import requirement_center as api
        from app.governance import execution_context, titles, change_index
        baseline = baseline_reader(Path(os.environ['BUG_READ_BASELINE_DIR']), monkeypatch)
        monkeypatch.setattr(api, 'ProjectReader', baseline)
        monkeypatch.setattr(execution_context, 'stage_map', baseline._baseline_stage_map)
        monkeypatch.setattr(titles, 'read_title', baseline._baseline_read_title)
        monkeypatch.setattr(change_index, 'read_title', baseline._baseline_read_title)
    concurrency = int(os.environ.get('CONTEXT_RESOURCE_CONCURRENCY', '1'))
    seconds = int(os.environ.get('CONTEXT_RESOURCE_SECONDS', '1800'))
    queries = [0]
    view = os.environ.get('CONTEXT_RESOURCE_VIEW', 'full')
    assert view in ('full', 'summary')
    def sql(*args):
        queries[0] += 1
    event.listen(factory.kw['bind'], 'before_cursor_execute', sql)
    def request(_):
        start = time.perf_counter()
        response = client.get('/api/v1/requirement-center/context', params={'space_id': 'space', 'repository_id': 'repo', 'view': view})
        assert response.status_code == 200
        data = response.json()['data']
        return (tuple(sorted((card['id'], card['stage']) for card in data['issues'])),
                len(response.content), (time.perf_counter() - start) * 1000)
    expected, _, _ = request(0)
    # Prime the actual concurrency level before comparing steady-state windows.
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        assert all(row[0] == expected for row in pool.map(request, range(concurrency)))
    counters = {'snapshot_content_reads': 0, 'yaml_parses': 0}
    original_fdopen, original_load = os.fdopen, yaml.load
    original_body = snapshot.read_body
    def opened(*args, **kwargs):
        counters['snapshot_content_reads'] += 1
        return original_fdopen(*args, **kwargs)
    def loaded(*args, **kwargs):
        counters['yaml_parses'] += 1
        return original_load(*args, **kwargs)
    def read_body(*args, **kwargs):
        counters['snapshot_content_reads'] += 1
        return original_body(*args, **kwargs)
    monkeypatch.setattr(os, 'fdopen', opened)
    monkeypatch.setattr(snapshot, 'read_body', read_body)
    monkeypatch.setattr(yaml, 'load', loaded)
    started, cpu = time.monotonic(), time.process_time()
    samples = []
    completed = 0
    memory_samples = []
    stop_sampling = Event()
    def sample_memory():
        while True:
            memory_samples.append({
                'elapsed_s': round(time.monotonic() - started, 2),
                'rss': int(Path('/proc/self/statm').read_text().split()[1]) * os.sysconf('SC_PAGE_SIZE')})
            if stop_sampling.wait(5):
                return
    sampler = Thread(target=sample_memory, daemon=True)
    sampler.start()
    try:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            while time.monotonic() - started < seconds:
                rows = list(pool.map(request, range(concurrency)))
                assert all(row[0] == expected for row in rows)
                completed += len(rows)
                # Linux RSS samples from the current process, plus process peak.
                rss = int(Path('/proc/self/statm').read_text().split()[1]) * os.sysconf('SC_PAGE_SIZE')
                samples.append({'elapsed_s': round(time.monotonic()-started, 2), 'rss': rss,
                                'max_ms': round(max(row[2] for row in rows), 2)})
                if len(samples) == 1 or samples[-1]['elapsed_s'] // 60 != samples[-2]['elapsed_s'] // 60:
                    Path(os.environ['CONTEXT_RESOURCE_OUTPUT'] + '.progress').write_text(json.dumps({
                        'mode': mode, 'expanded': expanded, 'concurrency': concurrency,
                        'completed': completed, **samples[-1]}))
                byte_cache = sum(row[1] for row in read_snapshot._versions.values())
                memo_cache = sum(row[1] for row in read_memo._versions.values())
                cache_bytes = byte_cache + memo_cache
                assert len(read_snapshot._versions) <= 2 and byte_cache <= read_snapshot.MAX_BYTES
                assert len(read_memo._versions) <= 2 and memo_cache <= read_memo.MAX_BYTES
                assert cache_bytes <= 64 * 1024**2
        elapsed = time.monotonic() - started
        stop_sampling.set()
        sampler.join()
        first = [s['rss'] for s in memory_samples if s['elapsed_s'] <= 300]
        last = [s['rss'] for s in memory_samples if s['elapsed_s'] >= elapsed - 300]
        assert first and last
        result = {'mode': mode, 'expanded': expanded, 'concurrency': concurrency,
                  'server_lifecycle': 'persistent_event_loop',
                  'duration_s': elapsed, 'completed': completed, 'errors': 0,
                  'files': len(fixed.files), 'bytes': sum(map(len, fixed.files.values())),
                  'cards': len(expected), 'sql': queries[0], 'response_bytes': rows[0][1],
                  'cpu_s_per_request': (time.process_time()-cpu)/completed,
                  'peak_rss': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                  'first_5m_rss_median': statistics.median(first),
                  'last_5m_rss_median': statistics.median(last), 'samples': samples,
                  'memory_samples': memory_samples,
                  'cache_bytes': cache_bytes, 'snapshot_revision': fixed.revision}
        result.update(counters)
        result['view'] = view
        Path(os.environ['CONTEXT_RESOURCE_OUTPUT']).write_text(json.dumps(result, indent=2))
        # The budget governs the delivered implementation. A historical control
        # may exceed it; retain its measured growth rather than changing it.
        if mode == 'optimized':
            assert result['last_5m_rss_median'] <= result['first_5m_rss_median'] + 32 * 1024**2
    finally:
        stop_sampling.set()
        sampler.join()
        event.remove(factory.kw['bind'], 'before_cursor_execute', sql)
