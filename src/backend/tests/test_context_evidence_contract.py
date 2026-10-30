"""Reject incomplete or selectively retained formal-page performance evidence."""
import copy
import pytest
from verify_context_evidence import verify_live_windows, verify_request_segments


@pytest.mark.parametrize('fault', ['missing_phase', 'double_count', 'nested_gap', 'route_gap', 'nonfinite'])
def test_request_segments_reject_incomplete_or_unexplained_evidence(fault):
    phases = dict.fromkeys(('materialize', 'object_authorization', 'parse', 'cleanup',
                           'reconcile', 'external_reconcile', 'card_projection_exclusive',
                           'projection_commit', 'document_projection', 'reader_orchestration'), 0.0)
    phases.update(snapshot_and_fences=100, snapshot=90, fences_exclusive=10, total=100,
                  dependencies=5, response_finalize=3, request_audit=2, route_total=110)
    verify_request_segments({'server_timing': phases})
    if fault == 'missing_phase': phases.pop('parse')
    elif fault == 'double_count': phases['parse'] = 90
    elif fault == 'nested_gap': phases['snapshot'] = 70
    elif fault == 'route_gap': phases['route_total'] = 500
    elif fault == 'nonfinite': phases['parse'] = float('nan')
    with pytest.raises((AssertionError, KeyError)):
        verify_request_segments({'server_timing': phases})


def evidence():
    services = ['backend', 'chat-worker', 'governance-controller']
    health = [{'name': name, 'health': 'healthy', 'restarts': 0} for name in services]
    windows = []
    for kind in ('natural', 'loaded'):
        window = {'kind': kind, 'devtools_open': False, 'additional_stress_running': kind == 'loaded',
                  'stress_cpu_limit': 2, 'host_cpus': 10,
                  'host_load_samples': [{'load': [3, 4, 5]}, {'load': [4, 5, 6]}],
                  'service_health_before': copy.deepcopy(health), 'service_health_after': copy.deepcopy(health)}
        for action in ('navigation', 'refresh'):
            window[action] = [{'request_id': f'{kind}-{action}-{n}', 'status': 200,
                               'context_ms': 1000, 'first_card_ms': 1500,
                               'first_card_in_viewport': True, 'visible_cards': 29,
                               'snapshot_revision': 'a' * 64, 'authorized_cards': 214} for n in range(30)]
        windows.append(window)
    return {'backend_services': services, 'background_services_running': True,
            'default_sprint_cards': 29, 'authorized_cards': 214,
            'snapshot_revision': 'a' * 64, 'windows': windows}


def test_two_complete_windows_are_required():
    item = evidence()
    verify_live_windows(item)
    item['windows'].pop()
    with pytest.raises(AssertionError):
        verify_live_windows(item)


@pytest.mark.parametrize('fault', ['missing_request_id', 'repeated_request', 'failed_request',
                                  'slow_tail', 'missing_card', 'service_restart', 'missing_load', 'wrong_load_kind', 'devtools_open',
                                  'changed_revision', 'missing_authorized_card'])
def test_bad_formal_samples_cannot_pass(fault):
    item = evidence()
    window = item['windows'][1]
    row = window['refresh'][0]
    if fault == 'missing_request_id': row['request_id'] = None
    elif fault == 'repeated_request': row['request_id'] = item['windows'][0]['navigation'][0]['request_id']
    elif fault == 'failed_request': row['status'] = 503
    elif fault == 'slow_tail':
        for entry in window['refresh'][:2]: entry['context_ms'] = 23000
    elif fault == 'missing_card': row['visible_cards'] = 0
    elif fault == 'service_restart': window['service_health_after'][0]['restarts'] = 1
    elif fault == 'missing_load': window['host_load_samples'] = []
    elif fault == 'devtools_open': window['devtools_open'] = True
    elif fault == 'wrong_load_kind': window['additional_stress_running'] = False
    elif fault == 'changed_revision': row['snapshot_revision'] = 'b' * 64
    elif fault == 'missing_authorized_card': row['authorized_cards'] = 213
    with pytest.raises(AssertionError):
        verify_live_windows(item)


def test_expanded_sampling_requires_all_predeclared_samples():
    item = evidence()
    item['samples_per_action'] = 100
    for window in item['windows']:
        for action in ('navigation', 'refresh'):
            original = window[action]
            original.extend({**original[0], 'request_id': f'{window["kind"]}-{action}-{n}'}
                            for n in range(30, 100))
    verify_live_windows(item)
    item['windows'][0]['navigation'].pop()
    with pytest.raises(AssertionError):
        verify_live_windows(item)


def test_route_segments_include_measured_endpoint_and_dispatch_overhead():
    phases = dict.fromkeys(('materialize', 'object_authorization', 'parse', 'cleanup',
                           'reconcile', 'external_reconcile', 'card_projection_exclusive',
                           'projection_commit', 'document_projection', 'reader_orchestration'), 0.0)
    phases.update(snapshot_and_fences=100, snapshot=90, fences_exclusive=10, total=100,
                  dependencies=5, response_finalize=3, request_audit=0,
                  request_audit_dispatch=2, endpoint_overhead=25, route_total=135)
    verify_request_segments({'server_timing': phases})
    phases.pop('endpoint_overhead')
    with pytest.raises(AssertionError):
        verify_request_segments({'server_timing': phases})
