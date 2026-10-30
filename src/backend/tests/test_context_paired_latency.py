"""Interleaved successful HTTP samples control time-varying host contention."""
import json
import math
import os
from pathlib import Path
import statistics
import time

import pytest
from test_chat import chat
from test_governance_scope import bind
from test_context_resources import baseline_reader, database_columns
from app.governance import reader, snapshot, execution_context, titles, change_index
from app.services import requirement_center as legacy


@pytest.mark.skipif(os.environ.get('CONTEXT_PAIRED_TEST') != '1', reason='explicit frozen-input performance run')
def test_paired(chat, monkeypatch):
    from app.api.v1 import requirement_center as api
    client, factory = chat
    database_columns(factory)
    root = Path(os.environ['BUG_READ_SOURCE'])
    frozen = snapshot.stable(root)
    bind(monkeypatch, root)
    names = ('_read_yaml', '_frontmatter', '_change_dir', '_change_tasks', '_change_document_names', '_change_spec_paths')
    modern = {name: getattr(legacy, name) for name in names}
    stage_map = execution_context.stage_map
    read_title = titles.read_title
    old = baseline_reader(Path(os.environ['BUG_READ_BASELINE_DIR']), monkeypatch)
    prior = {name: getattr(legacy, name) for name in names}
    operation = os.environ.get('CONTEXT_PAIRED_OPERATION', 'md')
    view = os.environ.get('CONTEXT_PAIRED_VIEW', 'full')
    assert view in ('full', 'summary')
    route = '/context' if operation == 'context' else '/issues/BUG-0016-capture/documents/capture.md'
    samples = {'baseline': [], 'optimized': []}
    count = int(os.environ.get('CONTEXT_PAIRED_SAMPLES', '30'))
    assert count >= 30
    expected = None
    for i in range(count + 1):
        for mode in (('baseline', 'optimized') if i % 2 == 0 else ('optimized', 'baseline')):
            monkeypatch.setattr(api, 'ProjectReader', old if mode == 'baseline' else reader.ProjectReader)
            monkeypatch.setattr(execution_context, 'stage_map', old._baseline_stage_map if mode == 'baseline' else stage_map)
            monkeypatch.setattr(titles, 'read_title', old._baseline_read_title if mode == 'baseline' else read_title)
            monkeypatch.setattr(change_index, 'read_title', old._baseline_read_title if mode == 'baseline' else read_title)
            for name in names:
                monkeypatch.setattr(legacy, name, (prior if mode == 'baseline' else modern)[name])
            start = time.perf_counter()
            response = client.get('/api/v1/requirement-center' + route,
                                  params={'space_id': 'space', 'repository_id': 'repo',
                                          'view': view if mode == 'optimized' else 'full'})
            elapsed = (time.perf_counter() - start) * 1000
            assert response.status_code == 200
            data = response.json()['data']
            semantic = sorted((card['id'], card['stage']) for card in data['issues']) if operation == 'context' else data
            if expected is None:
                expected = semantic
            assert semantic == expected
            if i:
                samples[mode].append({'ms': elapsed, 'request_id': response.headers['X-Request-ID'],
                                      'timings': response.headers.get('Server-Timing')})
    assert snapshot.stable(root).revision == frozen.revision
    report = {'operation': operation, 'optimized_view': view, 'revision': frozen.revision, 'samples': samples,
              'scheme': f'{count} alternating-order pairs after one warm-up per variant', 'summary': {}}
    for mode, rows in samples.items():
        values = sorted(row['ms'] for row in rows)
        report['summary'][mode] = {'n': len(values), 'median_ms': statistics.median(values),
                                   'p95_ms': values[math.ceil(len(values)*.95)-1], 'max_ms': max(values)}
    report['improvement'] = 1-report['summary']['optimized']['p95_ms']/report['summary']['baseline']['p95_ms']
    Path(os.environ['CONTEXT_PAIRED_OUTPUT']).write_text(json.dumps(report, indent=2))
    print(json.dumps(report['summary']), flush=True)
    assert report['improvement'] >= .5
