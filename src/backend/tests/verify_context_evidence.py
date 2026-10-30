"""Validate retained BUG-0056 evidence; does not generate product observations."""
import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path


def p95(rows, key):
    return sorted(row[key] for row in rows)[math.ceil(len(rows) * .95) - 1]


def verify_request_segments(row):
    raw = row['server_timing']
    metrics = (raw if isinstance(raw, dict) else
               dict((part.strip().split(';dur=')[0], float(part.split(';dur=')[1]))
                    for part in raw.split(',')))
    assert all(math.isfinite(value) and value >= 0 for value in metrics.values())
    exclusive = ('snapshot_and_fences', 'materialize', 'object_authorization', 'parse',
                 'cleanup', 'reconcile', 'external_reconcile', 'card_projection_exclusive',
                 'projection_commit', 'document_projection', 'reader_orchestration')
    assert abs(sum(metrics[key] for key in exclusive) - metrics['total']) < .2
    assert abs(metrics['snapshot'] + metrics['fences_exclusive'] - metrics['snapshot_and_fences']) < .1
    assert abs(sum(metrics[key] for key in ('dependencies', 'total', 'response_finalize', 'request_audit'))
               + metrics.get('endpoint_overhead', 0) + metrics.get('request_audit_dispatch', 0)
               - metrics['route_total']) < 10


def verify_live_windows(live):
    """Require both real-service windows; a fast isolated run cannot replace them."""
    services = ['backend', 'chat-worker', 'governance-controller']
    assert live['backend_services'] == services
    assert live['background_services_running'] is True
    samples = live.get('samples_per_action', 30)
    assert samples in (30, 100)
    revision = live['snapshot_revision']
    assert len(revision) == 64 and all(c in '0123456789abcdef' for c in revision)
    windows = live['windows']
    assert len(windows) == 2
    assert {window['kind'] for window in windows} == {'natural', 'loaded'}
    request_ids = set()
    for window in windows:
        assert window['devtools_open'] is False
        assert window['additional_stress_running'] is (window['kind'] == 'loaded')
        if window['kind'] == 'loaded':
            assert window['stress_cpu_limit'] == 2
        assert window['host_cpus'] > 0
        assert len(window['host_load_samples']) >= 2
        assert all(len(row['load']) == 3 and all(math.isfinite(x) and x >= 0 for x in row['load'])
                   for row in window['host_load_samples'])
        for checkpoint in ('service_health_before', 'service_health_after'):
            health = window[checkpoint]
            assert len(health) == 3 and {row['name'] for row in health} == set(services)
            assert all(row['health'] == 'healthy' and row['restarts'] == 0 for row in health)
        for kind in ('navigation', 'refresh'):
            rows = window[kind]
            ids = [row['request_id'] for row in rows]
            assert len(rows) == samples and len(set(ids)) == samples and all(ids)
            assert not request_ids.intersection(ids)
            request_ids.update(ids)
            assert all(row['status'] == 200 and math.isfinite(row['context_ms'])
                       and row['context_ms'] > 0 for row in rows)
            assert all(row['visible_cards'] == live['default_sprint_cards'] for row in rows)
            assert all(row['snapshot_revision'] == revision and
                       row['authorized_cards'] == live['authorized_cards'] for row in rows)
            assert p95(rows, 'context_ms') <= 3000
            if kind == 'navigation':
                assert all(row['first_card_in_viewport'] and math.isfinite(row['first_card_ms'])
                           and row['first_card_ms'] > 0 for row in rows)
                assert p95(rows, 'first_card_ms') <= 4000


def verify(directory, ac):
    metadata = json.loads((directory / 'inputs.json').read_text())
    for name, expected in metadata['source_sha256'].items():
        assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == expected, f'stale source: {name}'
    read = lambda name: json.loads((directory / name).read_text())
    executed = read('executed-source-sha256.json')
    assert all(metadata['source_sha256'][name] == value for name, value in executed.items())
    regression = read('regression.json')
    assert regression['failed'] == 0 and regression['passed'] >= 160
    if ac == 'AC-001':
        for operation in ('context', 'md'):
            result = read(f'paired-{operation}.json')
            assert result['revision'] == metadata['snapshot_revision']
            assert all(len(result['samples'][mode]) >= 30 for mode in ('baseline', 'optimized'))
            assert len(result['samples']['baseline']) == len(result['samples']['optimized'])
            for mode in ('baseline', 'optimized'):
                rows = result['samples'][mode]
                assert len({row['request_id'] for row in rows}) == len(rows)
                assert all(math.isfinite(row['ms']) and row['ms'] > 0 for row in rows)
                assert result['summary'][mode]['p95_ms'] == p95(rows, 'ms')
            measured = 1 - p95(result['samples']['optimized'], 'ms') / p95(result['samples']['baseline'], 'ms')
            assert abs(measured - result['improvement']) < 1e-9
            assert result['improvement'] >= .5
        rows = read('browser.json')['samples']
        for cold in (False, True):
            selected = [row for row in rows if row['cold'] == cold]
            assert len(selected) >= 30
            assert len({row['request_id'] for row in selected}) == len(selected)
            assert all(row['status'] == 200 and row['visible_cards'] == metadata['default_sprint_cards'] for row in selected)
            assert all(row['first_card_in_viewport'] and row['viewport_width'] > 0 and row['viewport_height'] > 0 for row in selected)
            assert p95(selected, 'first_card_ms') <= (6000 if cold else 4000)
            assert p95(selected, 'context_ms') <= (5000 if cold else 3000)
    elif ac in ('AC-003', 'AC-004'):
        kind = 'archive' if ac == 'AC-003' else 'identity'
        item = next(row for row in read('indexes.json') if row['kind'] == kind)
        assert item['equal'] and item['n'] == (171 if kind == 'archive' else 106)
        assert item['directory_scans'] == 1 if kind == 'archive' else item['registry_parses'] == 2
        assert item['baseline_ms'] > 0 and item['optimized_ms'] > 0
    elif ac == 'AC-005':
        frontend = read('frontend.json')
        assert frontend['failed'] == 0 and frontend['passed'] > 0
        observations = read('browser-functional.json')
        assert observations['status'] == 'passed'
        assert {'default_sprint', 'all', 'type_filter', 'refresh', 'document'} <= set(observations['checks'])
    elif ac == 'AC-006':
        for row in read('browser.json')['samples']:
            verify_request_segments(row)
        if metadata.get('read_profile') == 'summary':
            live = read('live-browser.json')
            verify_live_windows(live)
            for window in live['windows']:
                for action in ('navigation', 'refresh'):
                    for row in window[action]:
                        verify_request_segments(row)
                        assert all(math.isfinite(row[key]) and row[key] >= 0
                                   for key in ('queue', 'wait', 'transfer'))
    elif ac == 'AC-007':
        expanded = read('expanded-latency.json')
        assert expanded['files'] == 10000 and expanded['bytes'] == 32 * 1024**2
        for cold in (False, True):
            rows = [row for row in expanded['samples'] if row['cold'] == cold]
            assert len(rows) == 30 and len({row['request_id'] for row in rows}) == 30
            assert all(row['status'] == 200 and row['cards'] == expanded.get('cards', 1458) for row in rows)
        for scale in ('reference', 'expanded'):
            for concurrency in (1, 4):
                pair = {mode: read(f'resource-{scale}-{concurrency}-{mode}.json')
                        for mode in ('baseline', 'optimized')}
                for item in pair.values():
                    if metadata.get('read_profile') == 'summary':
                        assert item.get('server_lifecycle') == 'persistent_event_loop'
                    assert item['duration_s'] >= 1800 and item['completed'] > 0 and item['errors'] == 0
                    assert item['cards'] == (expanded.get('cards', 1458) if scale == 'expanded' else metadata['authorized_cards'])
                    assert item['files'] == (10000 if scale == 'expanded' else metadata['files'])
                    assert item['bytes'] == (32 * 1024**2 if scale == 'expanded' else metadata['bytes'])
                    assert item['cache_bytes'] <= 64 * 1024**2
                    memory = item['memory_samples']
                    first = [row['rss'] for row in memory if row['elapsed_s'] <= 300]
                    last = [row['rss'] for row in memory if row['elapsed_s'] >= item['duration_s'] - 300]
                    assert len(first) >= 50 and len(last) >= 50
                    assert statistics.median(first) == item['first_5m_rss_median']
                    assert statistics.median(last) == item['last_5m_rss_median']
                assert pair['optimized']['last_5m_rss_median'] <= pair['optimized']['first_5m_rss_median'] + 32 * 1024**2
                assert pair['optimized']['peak_rss'] <= pair['baseline']['peak_rss'] + 128 * 1024**2
                assert pair['optimized']['cpu_s_per_request'] <= pair['baseline']['cpu_s_per_request']
                assert pair['optimized']['cards'] == pair['baseline']['cards']
                assert pair['optimized']['snapshot_revision'] == pair['baseline']['snapshot_revision']
                if scale == 'reference':
                    assert pair['optimized']['cards'] == metadata['authorized_cards']
    elif ac == 'AC-010':
        live = read('live-browser.json')
        verify_live_windows(live)
        background = read('background.json')
        assert background['mysql_failed'] == 0 and background['sqlite_failed'] == 0
        assert background['reference_indexes_present'] is True
        assert background['orphan_reference_full_scans'] == 0
        assert background['automatic_backup_bounded'] is True
    elif ac == 'AC-008':
        checks = read('governance.json')
        assert all(checks[name] == 'passed' for name in
                   ('openspec', 'language', 'sprint_scope', 'context_budget', 'directory_structure'))
    elif ac != 'AC-002':
        raise ValueError('unknown acceptance item')
    print(f'{ac}: retained evidence passed; sources match')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--ac', required=True)
    arguments = parser.parse_args()
    verify(arguments.evidence, arguments.ac)
