"""Conservative stop classification for the four direct Chat governance actions."""
import hashlib
import json
import pytest

from app.governance.direct_command_journal import (
    archive_completion_blocked, completion_block_reason, is_formal_workflow_sync,
    observe, prepare, terminal,
)
from app.governance.snapshot import digest, read_once


@pytest.mark.parametrize('action', [
    'sprint-propose', 'req-opsx', 'opsx-apply', 'opsx-archive',
])
@pytest.mark.parametrize('point,expected', [
    ('before-write', 'no_governance_write'),
    ('first-file', 'partial_write'),
    ('before-sync', 'partial_write'),
    ('sync-started', 'sync_incomplete'),
    ('after-sync', 'sync_completed_unverified'),
    ('external-edit', 'blocked_unobserved_source_change'),
])
def test_direct_command_restart_uses_observed_source_facts(
    tmp_path, monkeypatch, action, point, expected,
):
    private = tmp_path / 'private'; private.mkdir(mode=0o700)
    source = tmp_path / 'source'; source.mkdir()
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(private))
    cid = '34adbd04-59be-408f-92f0-a4c108115c03'
    key = 'one-request'
    before = digest(read_once(source))
    prepare(cid, key, action, 'REQ-9001-isolated', before)
    if point != 'before-write':
        first = source / 'issues' / 'requirements' / 'sample.md'
        first.parent.mkdir(parents=True)
        first.write_text('first isolated file')
        observe(cid, key, 'write-1', 'completed', source)
    if point == 'before-sync':
        second = source / 'iterations' / 'change' / 'sample.md'
        second.parent.mkdir(parents=True)
        second.write_text('second isolated file')
        observe(cid, key, 'write-2', 'completed', source)
    if point in ('sync-started', 'after-sync'):
        observe(cid, key, 'sync-1', 'started', source, sync=True)
    if point == 'after-sync':
        synced = source / 'issues' / 'requirements' / 'registry.yaml'
        synced.write_text('entries: []')
        observe(cid, key, 'sync-1', 'completed', source, sync=True,
                sync_succeeded=True)
    if point == 'external-edit':
        (source / 'issues' / 'requirements' / 'sample.md').write_text('unknown edit')
    result = terminal(cid, key, 'stopped', source)
    assert result['classification'] == expected
    assert terminal(cid, key, 'stopped', source) == result
    assert result['action'] == action
    assert not any('first isolated file' in str(step) for step in result['steps'])


def test_failed_sync_is_not_reported_complete(tmp_path, monkeypatch):
    private = tmp_path / 'private'; private.mkdir(mode=0o700)
    source = tmp_path / 'source'; source.mkdir()
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(private))
    cid = '04adbd04-59be-408f-92f0-a4c108115c03'
    prepare(cid, 'retry', 'req-opsx', 'REQ-9001-isolated', digest(read_once(source)))
    path = source / 'openspec' / 'changes' / 'sample.md'
    path.parent.mkdir(parents=True); path.write_text('partial')
    observe(cid, 'retry', 'write', 'completed', source)
    observe(cid, 'retry', 'sync', 'started', source, sync=True)
    observe(cid, 'retry', 'sync', 'completed', source, sync=True,
            sync_succeeded=False)
    assert terminal(cid, 'retry', 'failed', source)['classification'] == 'sync_incomplete'


def test_candidate_action_without_direct_journal_is_not_interrupted(
    tmp_path, monkeypatch,
):
    private = tmp_path / 'private'; private.mkdir(mode=0o700)
    source = tmp_path / 'source'; source.mkdir()
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(private))
    cid = '14adbd04-59be-408f-92f0-a4c108115c03'
    assert observe(cid, 'candidate-request', 'tool-1', 'completed', source) is None
    assert terminal(cid, 'candidate-request', 'stopped', source) is None


def test_openspec_change_control_file_is_a_governance_fact(tmp_path):
    source = tmp_path / 'source'; source.mkdir()
    before = digest(read_once(source))
    control = source / 'openspec' / 'changes' / 'isolated-change' / '.openspec.yaml'
    control.parent.mkdir(parents=True)
    control.write_text('schema: spec-driven\n')
    after = read_once(source)
    assert 'openspec/changes/isolated-change/.openspec.yaml' in after
    assert digest(after) != before


@pytest.mark.parametrize('command,expected', [
    ('python scripts/sync-workflow-status.py --event opsx.apply --change sample', True),
    ('python scripts/sync-workflow-status.py --event opsx.apply --dry-run', False),
    ('python scripts/sync-workflow-status.py --event opsx.apply --check', False),
    ('rg sync-workflow-status.py scripts', False),
])
def test_formal_sync_observation_excludes_probes(command, expected):
    assert is_formal_workflow_sync({'type': 'commandExecution', 'command': command}) is expected


def test_archive_completion_gate_detects_post_command_spec_edit(tmp_path, monkeypatch):
    private = tmp_path / 'private'; private.mkdir(mode=0o700)
    source = tmp_path / 'source'; source.mkdir()
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(private))
    cid, key, change = '74adbd04-59be-408f-92f0-a4c108115c03', 'archive-request', 'add-isolated-ac012'
    specs = source / 'openspec' / 'specs'
    spec = specs / 'sample' / 'spec.md'
    spec.parent.mkdir(parents=True)
    spec.write_text('merged')
    value = hashlib.sha256()
    value.update(b'sample/spec.md\0')
    value.update(hashlib.sha256(b'merged').digest())
    journal = source / 'openspec' / 'archive' / '.archive-recovery' / f'{change}.json'
    journal.parent.mkdir(parents=True)
    journal.write_text(json.dumps({'change_id': change, 'expected_spec_hash': value.hexdigest()}))
    prepare(cid, key, 'opsx-archive', change, digest(read_once(source)))
    assert not archive_completion_blocked(cid, key, source)
    spec.write_text('later edit')
    observe(cid, key, 'later-edit', 'completed', source)
    assert archive_completion_blocked(cid, key, source)
    result = terminal(cid, key, 'failed', source)
    assert result['classification'] == 'blocked_archive_spec_drift'
    assert result['terminal_status'] == 'failed'


def test_archive_completion_gate_allows_turn_without_direct_command_record(tmp_path, monkeypatch):
    private = tmp_path / 'private'; private.mkdir(mode=0o700)
    source = tmp_path / 'source'; source.mkdir()
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(private))
    assert not archive_completion_blocked(
        '74adbd04-59be-408f-92f0-a4c108115c03', 'req-generate-request', source,
    )


def test_sprint_completion_gate_rejects_invalid_yaml_after_successful_sync(tmp_path, monkeypatch):
    private = tmp_path / 'private'; private.mkdir(mode=0o700)
    source = tmp_path / 'source'; source.mkdir()
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(private))
    cid, key, issue = '84adbd04-59be-408f-92f0-a4c108115c03', 'sprint-request', 'REQ-9001-isolated'
    sprint = source / 'iterations/change/sprint-901/sprint.yaml'
    sprint.parent.mkdir(parents=True)
    sprint.write_text('sprint_id: sprint-901\nrequirements:\n  - REQ-9001-isolated\n')
    prepare(cid, key, 'sprint-propose', issue, digest(read_once(source)))
    assert completion_block_reason(cid, key, source) is None
    sprint.write_text('sprint_id: sprint-901\nrequirements:\n  - REQ-9001-isolated\n    - REQ-9002-other\n')
    observe(cid, key, 'sync', 'completed', source, sync=True, sync_succeeded=True)
    assert completion_block_reason(cid, key, source) == 'sprint_source_invalid'
    assert terminal(cid, key, 'failed', source)['classification'] == 'blocked_invalid_sprint_source'


def test_sprint_completion_gate_rejects_missing_scope_and_accepts_valid_sprint(tmp_path, monkeypatch):
    private = tmp_path / 'private'; private.mkdir(mode=0o700)
    source = tmp_path / 'source'; source.mkdir()
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(private))
    cid, key, issue = '94adbd04-59be-408f-92f0-a4c108115c03', 'sprint-request', 'REQ-9001-isolated'
    sprint = source / 'iterations/change/sprint-901/sprint.yaml'
    sprint.parent.mkdir(parents=True)
    sprint.write_text('sprint_id: sprint-901\nrequirements: []\n')
    prepare(cid, key, 'sprint-propose', issue, digest(read_once(source)))
    assert completion_block_reason(cid, key, source) == 'sprint_source_invalid'
    sprint.write_text('sprint_id: sprint-901\nrequirements:\n  - REQ-9001-isolated\n')
    assert completion_block_reason(cid, key, source) is None
