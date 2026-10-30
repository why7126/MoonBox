"""Opt-in cold/warm HTTP observations at the approved existing hard limits."""
import json
import math
import os
from pathlib import Path
import statistics
import time

import pytest
from test_chat import chat
from test_governance_scope import bind
from test_context_resources import database_columns, expand_to_limits
from context_browser_fixture import clear_caches
from app.governance import snapshot


@pytest.mark.skipif(os.environ.get('CONTEXT_EXPANDED_LATENCY') != '1', reason='explicit frozen upper-limit run')
def test_expanded_cold_warm(chat, tmp_path, monkeypatch):
    client, factory = chat
    database_columns(factory)
    source = snapshot.stable(Path(os.environ['BUG_READ_SOURCE']))
    root = tmp_path / 'expanded'
    for name, body in source.files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    bind(monkeypatch, root)
    view = os.environ.get('CONTEXT_RESOURCE_VIEW', 'full')
    assert view in ('full', 'summary')
    def request():
        started = time.perf_counter()
        response = client.get('/api/v1/requirement-center/context',
                              params={'space_id': 'space', 'repository_id': 'repo', 'view': view})
        elapsed = (time.perf_counter() - started) * 1000
        assert response.status_code == 200
        cards = response.json()['data']['issues']
        return (tuple(sorted((card['id'], card['stage']) for card in cards)),
                {'ms': elapsed, 'request_id': response.headers['X-Request-ID'],
                 'server_timing': response.headers['Server-Timing'],
                 'status': response.status_code, 'cards': len(cards)})
    reference, _ = request()
    expand_to_limits(root, source)
    fixed = snapshot.stable(root)
    expected, initialization = request()
    assert len(expected) == len(reference) + (snapshot.LIMIT_COUNT - len(source.files)) // 3
    rows = []
    for cold in (True, False):
        for _ in range(30):
            if cold:
                clear_caches()
            actual, row = request()
            assert actual == expected
            rows.append({**row, 'cold': cold})
    summary = {}
    for cold in (True, False):
        values = sorted(row['ms'] for row in rows if row['cold'] == cold)
        summary['cold' if cold else 'warm'] = {'median_ms': statistics.median(values),
            'p95_ms': values[math.ceil(len(values)*.95)-1], 'max_ms': max(values)}
    assert snapshot.stable(root).revision == fixed.revision
    result = {'view': view, 'samples': rows, 'summary': summary, 'initialization': initialization,
              'files': len(fixed.files), 'bytes': sum(map(len, fixed.files.values())),
              'reference_cards': len(reference), 'cards': len(expected),
              'snapshot_revision': fixed.revision, 'os_page_cache_cleared': False,
              'boundary': 'Real ASGI route with synthetic account; HTTP trend, not browser first-card latency. No expanded-scale SLA is claimed.'}
    Path(os.environ['CONTEXT_EXPANDED_OUTPUT']).write_text(json.dumps(result, indent=2))
