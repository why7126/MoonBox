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
