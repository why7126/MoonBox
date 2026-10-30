"""Explicit frozen-input HTTP measurement; never a browser first-card claim."""
import json
import math
import os
from pathlib import Path
import time

import pytest
from test_chat import chat
from test_governance_scope import bind
from test_context_resources import database_columns
from context_browser_fixture import clear_caches
from app.governance import snapshot


@pytest.mark.skipif(os.environ.get('BUG_SUMMARY_BENCHMARK') != '1', reason='explicit frozen summary benchmark')
def test_summary_cold_and_warm_http(chat, monkeypatch):
    client, factory = chat
    database_columns(factory)
    root = Path(os.environ['BUG_READ_SOURCE'])
    frozen = snapshot.stable(root)
    bind(monkeypatch, root)
    samples = []
    expected = None
    for cold in (True, False):
        for n in range(30):
            if cold:
                clear_caches()
            start = time.perf_counter()
            response = client.get('/api/v1/requirement-center/context', params={
                'space_id': 'space', 'repository_id': 'repo', 'view': 'summary'})
            elapsed = (time.perf_counter() - start) * 1000
            row = {'n': n, 'cold': cold, 'http_ms': elapsed, 'status': response.status_code,
                   'request_id': response.headers.get('X-Request-ID'),
                   'server_timing': response.headers.get('Server-Timing')}
            samples.append(row)
            if response.status_code == 200:
                data = response.json()['data']
                row['revision'] = data['snapshot_revision']
                row['cards'] = len(data['issues'])
                actual = sorted((c['id'], c['stage']) for c in data['issues'])
                expected = actual if expected is None else expected
                row['same_cards'] = actual == expected
                row['all_checks_deferred'] = all(c['checks_deferred'] for c in data['issues'])
    p95 = {label: sorted(r['http_ms'] for r in samples if r['cold'] == cold)[math.ceil(30*.95)-1]
           for label, cold in [('cold', True), ('warm', False)]}
    report = {'kind': 'ASGI HTTP with isolated account; not browser latency',
              'source_revision': frozen.revision, 'files': len(frozen.files),
              'bytes': sum(map(len, frozen.files.values())), 'samples': samples,
              'p95_ms': p95, 'os_page_cache_cleared': False}
    Path(os.environ['BUG_SUMMARY_OUTPUT']).write_text(json.dumps(report, indent=2)+'\n')
    assert snapshot.stable(root).revision == frozen.revision
    assert all(r['status'] == 200 and r['same_cards'] and r['all_checks_deferred'] for r in samples)
    assert len({r['revision'] for r in samples}) == 1
    assert p95['cold'] <= 5000 and p95['warm'] <= 3000
