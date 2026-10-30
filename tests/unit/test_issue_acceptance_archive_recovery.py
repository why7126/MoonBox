"""Archive acceptance gate keeps applying after the active Change moves."""
import importlib.util
from pathlib import Path
import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts/validate-issue-acceptance-ready.py"
SPEC = importlib.util.spec_from_file_location("issue_acceptance_ready", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def trace(root: Path, path: str, issue: str | None = None) -> None:
    target = root / path / "trace.md"
    target.parent.mkdir(parents=True)
    target.write_text(f"---\nchange_id: isolated-change\nstatus: applied\nbug: {issue or 'null'}\n---\n")


def test_standalone_archive_recovery_uses_unique_canonical_trace(tmp_path):
    trace(tmp_path, "openspec/archive/2026-10-13-isolated-change")
    assert MODULE.readiness(tmp_path, "isolated-change") == (True, "standalone_change")


def test_archive_recovery_accepts_unique_legacy_transition_trace(tmp_path):
    trace(tmp_path, "openspec/changes/archive/2026-10-13-isolated-change")
    assert MODULE.readiness(tmp_path, "isolated-change") == (True, "standalone_change")
    trace(tmp_path, "openspec/archive/2026-10-13-isolated-change")
    assert MODULE.readiness(tmp_path, "isolated-change") == (False, "change_identity_ambiguous")


def test_archive_recovery_rejects_ambiguous_or_missing_trace(tmp_path):
    trace(tmp_path, "openspec/archive/2026-10-13-isolated-change")
    trace(tmp_path, "openspec/archive/2026-10-14-isolated-change")
    assert MODULE.readiness(tmp_path, "isolated-change") == (False, "change_identity_ambiguous")
    (tmp_path / "openspec/archive/2026-10-14-isolated-change/trace.md").unlink()
    (tmp_path / "openspec/archive/2026-10-13-isolated-change/trace.md").unlink()
    assert MODULE.readiness(tmp_path, "isolated-change") == (False, "change_identity_ambiguous")


def test_issue_linked_archive_still_requires_signed_acceptance(tmp_path):
    issue = "BUG-9001-isolated"
    trace(tmp_path, "openspec/archive/2026-10-13-isolated-change", issue)
    assert MODULE.readiness(tmp_path, "isolated-change") == (False, "issue_acceptance_missing_or_ambiguous")
    acceptance = tmp_path / "issues/bugs/review" / issue / "acceptance.md"
    acceptance.parent.mkdir(parents=True)
    acceptance.write_text("---\nacceptance_status: passed\n---\n\n- [x] AC-001：通过。\n")
    assert MODULE.readiness(tmp_path, "isolated-change") == (True, "issue_acceptance_passed")


@pytest.mark.parametrize('field,issue,domain',[
    ('requirement_id','REQ-9001-isolated','requirements'),
    ('bug_id','BUG-9001-isolated','bugs'),
])
def test_generated_change_trace_issue_id_never_bypasses_acceptance(tmp_path,field,issue,domain):
    target=tmp_path/'openspec/changes/isolated-change/trace.md';target.parent.mkdir(parents=True)
    target.write_text(f'---\nchange_id: isolated-change\nstatus: applied\n{field}: {issue}\n---\n')
    assert MODULE.readiness(tmp_path,'isolated-change')==(False,'issue_acceptance_missing_or_ambiguous')
    acceptance=tmp_path/'issues'/domain/'review'/issue/'acceptance.md';acceptance.parent.mkdir(parents=True)
    acceptance.write_text('---\nacceptance_status: pending\n---\n\n- [ ] AC-001：待验收。\n')
    assert MODULE.readiness(tmp_path,'isolated-change')==(False,'issue_acceptance_pending checked=0 total=1')
    acceptance.write_text('---\nacceptance_status: passed\n---\n\n- [x] AC-001：通过。\n')
    assert MODULE.readiness(tmp_path,'isolated-change')==(True,'issue_acceptance_passed')


def test_partial_change_admission_never_closes_whole_issue(tmp_path):
    import json,sys
    from app.governance.archive_admission import change_acceptance,issue_acceptance
    from scripts.opsx_acceptance import run_acceptance
    issue='REQ-9001-isolated';change='isolated-change'
    folder=tmp_path/'openspec/changes'/change;folder.mkdir(parents=True)
    (folder/'trace.md').write_text(f'---\nrequirement_id: {issue}\nstatus: applied\n---\n')
    (folder/'acceptance.md').write_text('- [ ] AC-001 subset\n')
    doc=tmp_path/'issues/requirements/review'/issue/'acceptance.md';doc.parent.mkdir(parents=True)
    doc.write_text('---\nacceptance_status: partial\n---\n- [ ] AC-010 whole workflow\n- [ ] AC-011 other workflow\n')
    (tmp_path/'input.txt').write_text('immutable input')
    plan=dict(schema_version=1,change_id=change,issue_id=issue,issue_acceptance_scope='partial',scope_description='dependency only',issue_ac_mapping={'AC-001':['AC-010']},checks=[dict(id='AC-001',kind='command',inputs=['input.txt'],argv=[sys.executable,'-c','exit(0)'])])
    (folder/'acceptance-plan.json').write_text(json.dumps(plan))
    assert run_acceptance(tmp_path,change,None)['status']=='passed'
    result=change_acceptance(tmp_path,change)
    assert result['ready'] and result['total']==1 and result['issue_complete'] is False
    assert not issue_acceptance(tmp_path,doc.parent,[change])['ready']
    doc.write_text(doc.read_text().replace('acceptance_status: partial','acceptance_status: partial\nmanual_acceptance_status: required'))
    assert not change_acceptance(tmp_path,change)['ready']
    doc.write_text(doc.read_text().replace('\nmanual_acceptance_status: required',''))
    (tmp_path/'input.txt').write_text('changed')
    assert not change_acceptance(tmp_path,change)['ready']
