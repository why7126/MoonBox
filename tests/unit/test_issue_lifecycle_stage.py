"""Physical lifecycle projection must not rewrite historical or semantic status facts."""
from pathlib import Path
from types import SimpleNamespace
import runpy
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from workflow_sync.issue_stage import scan_stage_drift, replace_stage
from workflow_sync.issue_status_residuals import scan_issue_status_residuals, reconcile_issue_status_residuals
from workflow_sync.issue_subdocuments import sync_issue_subdocuments
from workflow_sync.derive import DerivedIssue


def document(stage='plan', status='done'):
    return (f'---\nstatus: {status}\nlifecycle_stage: {stage}\ncreated_at: 2026-01-01 00:00:00\n'
            'updated_at: 2026-01-01 00:00:00\n---\n# 历史\n```yaml\nlifecycle_stage: plan\n```\n')


def issue_at(tmp_path, stage='archive', kind='bug'):
    path = tmp_path / stage / ('BUG-0099-test' if kind == 'bug' else 'REQ-0099-test')
    path.mkdir(parents=True)
    for name in ['trace.md', 'capture.md', 'bug.md' if kind == 'bug' else 'requirement.md']:
        (path / name).write_text(document())
    (path / 'root-cause.md').write_text(document(status='confirmed'))
    return SimpleNamespace(path=path, issue_id=path.name, kind=kind, trace_status='done',
                           openspec_changes=[], related_changes=[], related_change=None)


@pytest.mark.parametrize('kind', ['bug', 'req'])
@pytest.mark.parametrize('stage', ['plan', 'review', 'archive'])
def test_sync_projects_physical_stage_and_preserves_history(tmp_path, kind, stage):
    issue = issue_at(tmp_path, stage, kind)
    before = {p.name: p.read_text() for p in issue.path.glob('*.md')}
    derived = DerivedIssue(issue.issue_id, kind, 'done', None, '')
    sync_issue_subdocuments(issue, derived, event=None, source_change=None, write=False)
    assert {p.name:p.read_text() for p in issue.path.glob('*.md')} == before
    sync_issue_subdocuments(issue, derived, event=None, source_change=None, write=True)
    assert not scan_stage_drift(issue.path)
    for p in issue.path.glob('*.md'):
        assert p.read_text().split('---', 2)[2] == before[p.name].split('---', 2)[2]
    assert (issue.path / 'root-cause.md').read_text() == before['root-cause.md']
    stable = {p.name:p.read_bytes() for p in issue.path.glob('*.md')}
    sync_issue_subdocuments(issue, derived, event=None, source_change=None, write=True)
    assert {p.name:p.read_bytes() for p in issue.path.glob('*.md')} == stable


def test_archived_residual_preview_repair_and_idempotency(tmp_path):
    issue = issue_at(tmp_path)
    (issue.path / 'trace.md').write_text(document('archive'))
    assert len(scan_issue_status_residuals(issue.path)) == 2
    before = {p:p.read_bytes() for p in issue.path.glob('*.md')}
    result = reconcile_issue_status_residuals(issue, write=False)
    assert len(result.planned) == 2
    assert all(p.target_status == 'archive' for p in result.planned)
    assert {p:p.read_bytes() for p in before} == before
    result = reconcile_issue_status_residuals(issue, write=True)
    assert (result.changed_files, result.changed_fields) == (2, 2)
    assert not scan_issue_status_residuals(issue.path)
    assert (issue.path / 'root-cause.md').read_bytes() == before[issue.path / 'root-cause.md']
    assert reconcile_issue_status_residuals(issue, write=True).changed_files == 0


@pytest.mark.parametrize('invalid', ['unknown', 'null', '[plan]', 'plan\nlifecycle_stage: archive', '"unterminated'])
def test_invalid_stage_blocks_without_writes(tmp_path, invalid):
    issue = issue_at(tmp_path)
    (issue.path / 'bug.md').write_text(document(invalid))
    before = {p:p.read_bytes() for p in issue.path.glob('*.md')}
    result = reconcile_issue_status_residuals(issue, write=True)
    assert result.blockers
    assert {p:p.read_bytes() for p in before} == before


def test_absent_stage_and_legacy_paths_are_not_invented(tmp_path):
    text = '---\nstatus: done\n---\n历史 lifecycle_stage: plan\n'
    assert replace_stage(text, 'archive') == text
    issue = issue_at(tmp_path, 'legacy')
    assert scan_stage_drift(issue.path) == []


@pytest.mark.parametrize('target', ['review', 'archive'])
def test_migration_previews_and_applies_all_stage_mirrors(tmp_path, target):
    ns = runpy.run_path(str(ROOT / 'scripts/promote-issue-stage.py'))
    issue = issue_at(tmp_path, 'plan' if target == 'review' else 'review')
    candidate = ns['IssueCandidate']('bug', issue.issue_id, issue.path, issue.path/'trace.md')
    dest = tmp_path / target / issue.issue_id
    before = (issue.path/'trace.md').read_text()
    promotion = ns['Promotion'](candidate, dest, before, replace_stage(before,target), 'test')
    diff = ns['diff_trace'](promotion,tmp_path)
    assert 'capture.md' in diff and 'bug.md' in diff
    args = SimpleNamespace(check=False,dry_run=True)
    assert ns['apply_promotions'](tmp_path,[promotion],args,ns['Report']()) == 0
    assert not dest.exists()
    args.dry_run = False
    assert ns['apply_promotions'](tmp_path,[promotion],args,ns['Report']()) == 0
    assert not scan_stage_drift(dest)
    assert 'status: confirmed' in (dest/'root-cause.md').read_text()


def test_stage_only_reconcile_preserves_non_lifecycle_status(tmp_path):
    issue = issue_at(tmp_path)
    capture = issue.path / 'capture.md'
    capture.write_text(document(status='confirmed'))
    reconcile_issue_status_residuals(issue, write=True)
    assert 'status: confirmed' in capture.read_text()
    assert not scan_stage_drift(issue.path)


def test_invalid_stage_prevents_subdocument_sync(tmp_path):
    issue = issue_at(tmp_path)
    (issue.path / 'capture.md').write_text(document('unknown'))
    before = {p:p.read_bytes() for p in issue.path.glob('*.md')}
    derived = DerivedIssue(issue.issue_id, 'bug', 'done', None, '')
    result = sync_issue_subdocuments(issue, derived, event=None, source_change=None, write=True)
    assert result.blockers
    assert {p:p.read_bytes() for p in before} == before
