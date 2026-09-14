from pathlib import Path
import pytest
from scripts.workflow_sync.collect import load_issue_record
from scripts.workflow_sync.classification import resolve_classification, sync_classification


def doc(path, text):
    path.write_text('---\ncreated_at: 2026-01-01 12:00:00\nupdated_at: 2026-01-01 12:00:00\n' + text + '\n---\n\n历史 priority: P2 保留\n')


@pytest.mark.parametrize('kind,key,value,other', [('req','priority','P0','severity'), ('req','priority','P3','severity'), ('bug','severity','high','priority')])
def test_trace_wins_and_sync_is_idempotent(tmp_path, monkeypatch, kind, key, value, other):
    import scripts.workflow_sync.patch as patch
    monkeypatch.setattr(patch, 'ROOT', tmp_path)
    folder = tmp_path / 'item'; folder.mkdir()
    doc(folder/'trace.md', f'{key}: {value}')
    doc(folder/'capture.md', f'{key}_hint: old\n{other}: P2')
    original = (folder/'capture.md').read_text()
    issue = load_issue_record(folder, kind)
    assert issue.priority == value and issue.classification_error is None
    assert any(r.changed for r in sync_classification(issue, write=False))
    assert (folder/'capture.md').read_text() == original
    sync_classification(issue, write=True)
    result = (folder/'capture.md').read_text()
    assert f'{key}: {value}' in result and f'{key}_hint:' not in result
    assert f'\n{other}:' not in result
    assert '历史 priority: P2 保留' in result
    assert 'created_at: 2026-01-01 12:00:00' in result
    assert not any(r.changed for r in sync_classification(issue, write=True))
    assert not (folder/'bug.md').exists()


def test_legacy_hint_missing_and_invalid(tmp_path):
    doc(tmp_path/'capture.md', 'severity_hint: medium\npriority: P2')
    assert resolve_classification(tmp_path, 'bug') == ('medium', None)
    doc(tmp_path/'trace.md', 'severity: P2')
    assert 'invalid' in resolve_classification(tmp_path, 'bug')[1]
    doc(tmp_path/'trace.md', 'priority: P2')
    doc(tmp_path/'capture.md', 'priority: P2')
    assert 'missing severity' in resolve_classification(tmp_path, 'bug')[1]


def test_registry_bug_field_is_severity(tmp_path, monkeypatch):
    import scripts.workflow_sync.patch as patch
    from scripts.workflow_sync.collect import IssueRecord
    from scripts.workflow_sync.derive import DerivedIssue
    monkeypatch.setattr(patch, 'ROOT', tmp_path)
    folder = tmp_path/'issues/bugs/plan/BUG-0099-test';folder.mkdir(parents=True)
    registry = tmp_path/'issues/bugs/_registry.yaml'
    registry.write_text('entries:\n  - id: BUG-0099-test\n    priority: P2\n    severity: low\n')
    issue = IssueRecord('BUG-0099-test','bug',folder,priority='high')
    derived = DerivedIssue(issue_id=issue.issue_id, kind='bug', display_status='captured', note='', linked_change=None)
    patch.patch_registry_entry(registry, issue, derived, None)
    assert 'priority:' not in registry.read_text()
    assert 'severity: high' in registry.read_text()
