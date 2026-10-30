from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from opsx_acceptance import fingerprint, read_plan, read_turn, readiness, run_acceptance, run_product_turn, validate_report
from workflow_sync.derive import DerivedIssue
from workflow_sync import constants, issue_subdocuments


def test_legacy_sample_status_only_works_for_archived_plan(tmp_path):
    import pytest

    root, active = fixture(tmp_path)
    plan = json.loads((active / "acceptance-plan.json").read_text())
    plan["checks"][0]["required_sample"] = {"status": "completed-source-archive"}
    (active / "acceptance-plan.json").write_text(json.dumps(plan))

    with pytest.raises(ValueError, match="invalid required sample status"):
        read_plan(active)

    archived = root / "openspec" / "archive" / "2026-10-13-check-example"
    archived.mkdir(parents=True)
    (archived / "acceptance-plan.json").write_text(json.dumps(plan))
    assert read_plan(archived)["checks"][0]["required_sample"]["status"] == "completed-source-archive"
    assert issue_subdocuments.acceptance_checkmark(" ", "completed-source-archive", True) == "x"
    assert issue_subdocuments.acceptance_checkmark(" ", "completed-source-archive", False) == " "


def fixture(tmp_path: Path) -> tuple[Path, Path]:
    change = tmp_path / "openspec" / "changes" / "check-example"
    change.mkdir(parents=True)
    (tmp_path / "input.txt").write_text("v1", encoding="utf-8")
    (change / "acceptance-plan.json").write_text(json.dumps({
        "schema_version": 1,
        "change_id": "check-example",
        "preflight": [[sys.executable, "-c", "exit(0)"]],
        "checks": [
            {"id": "AC-001", "kind": "command", "inputs": ["input.txt"], "argv": [sys.executable, "-c", "exit(0)"]},
            {"id": "AC-002", "kind": "command", "inputs": ["openspec/changes/check-example/acceptance-plan.json"], "argv": [sys.executable, "-c", "exit(0)"]},
        ],
    }), encoding="utf-8")
    return tmp_path, change


def test_incremental_acceptance_only_invalidates_changed_ac(tmp_path):
    root, change = fixture(tmp_path)
    first = run_acceptance(root, "check-example", None)
    assert first["status"] == "passed"
    assert readiness(root, "check-example")["status"] == "ready"
    (root / "input.txt").write_text("v2", encoding="utf-8")
    assert readiness(root, "check-example")["stale"] == ["AC-001"]
    second = run_acceptance(root, "check-example", None)
    manifests = sorted((change / "evidence" / "acceptance").glob("*/manifest.json"))
    latest = json.loads(manifests[-1].read_text())
    assert second["status"] == "passed"
    assert latest["checks"][0]["reused"] is False
    assert latest["checks"][1]["reused"] is True


def test_partial_sample_blocks_command_probe_and_readiness(tmp_path):
    root, change = fixture(tmp_path)
    plan_path = change / "acceptance-plan.json"
    plan = json.loads(plan_path.read_text())
    plan["checks"][0]["required_sample"] = {"status": "partial"}
    plan_path.write_text(json.dumps(plan))
    result = run_acceptance(root, change.name, None)
    assert result["status"] == "blocked"
    manifest = json.loads((root / result["path"] / "manifest.json").read_text())
    assert manifest["checks"][0]["status"] == "blocked"
    assert manifest["checks"][0]["reason"] == "sample-incomplete"
    assert readiness(root, change.name)["stale"] == ["AC-001"]
    plan["checks"][0]["required_sample"]["status"] = "passed"
    plan_path.write_text(json.dumps(plan))
    assert run_acceptance(root, change.name, None)["status"] == "passed"
    assert readiness(root, change.name)["status"] == "ready"


def test_issue_projection_refresh_does_not_stale_acceptance_criteria(tmp_path):
    relative = "issues/bugs/review/BUG-9001-isolated/acceptance.md"
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_text("---\nbug_id: BUG-9001-isolated\nupdated_at: old\nacceptance_status: pending\n---\n\n"
                    "# 验收\n\n- [ ] AC-001：归档成功。\n\n## 验收结果回填\n\n```yaml\naccepted_at: null\n```\n")
    check = {"id": "AC-001", "kind": "command", "inputs": [relative], "argv": [sys.executable]}
    before = fingerprint(tmp_path, check)
    path.write_text(path.read_text().replace("updated_at: old", "updated_at: new")
                    .replace("acceptance_status: pending", "acceptance_status: passed")
                    .replace("accepted_at: null", "accepted_at: now"))
    assert fingerprint(tmp_path, check) == before
    path.write_text(path.read_text().replace("- [ ] AC-001", "- [x] AC-001"))
    assert fingerprint(tmp_path, check) != before


def test_product_turn_requires_same_turn_command_success(tmp_path):
    db_path = tmp_path / "chat.db"
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE TABLE chat_turns (id TEXT, conversation_id TEXT, status TEXT, error_code TEXT)")
        db.execute("CREATE TABLE chat_events (turn_id TEXT, sequence INTEGER, event_type TEXT, payload TEXT)")
        db.execute("INSERT INTO chat_turns VALUES ('turn-1','chat-1','completed',NULL)")
        db.execute("INSERT INTO chat_events VALUES ('turn-1',47,'execution.tool',?)", (json.dumps({"type": "commandExecution", "phase": "completed", "exit_code": 0, "arguments": {"command": "bash scripts/archive-change.sh example --finalize"}, "result": "secret-output"}),))
    turn = read_turn(db_path, "turn-1")
    assert turn["commands"][0]["sequence"] == 47
    assert "secret-output" not in json.dumps(turn)
    root, change = fixture(tmp_path)
    plan_path = change / "acceptance-plan.json"
    plan = json.loads(plan_path.read_text())
    plan["checks"] = [{"id": "AC-001", "kind": "product_turn", "inputs": ["input.txt"], "turn_id": "turn-1", "command_contains": "archive-change.sh"}]
    plan_path.write_text(json.dumps(plan))
    assert run_acceptance(root, "check-example", db_path)["status"] == "passed"
    with sqlite3.connect(db_path) as db:
        db.execute("UPDATE chat_turns SET status='stopped' WHERE id='turn-1'")
    (root / "input.txt").write_text("v2")
    assert run_acceptance(root, "check-example", db_path)["status"] == "failed"


def test_product_turn_without_completed_command_fails(tmp_path):
    db_path = tmp_path / "chat.db"
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE TABLE chat_turns (id TEXT, conversation_id TEXT, status TEXT, error_code TEXT)")
        db.execute("CREATE TABLE chat_events (turn_id TEXT, sequence INTEGER, event_type TEXT, payload TEXT)")
        db.execute("INSERT INTO chat_turns VALUES ('turn-1','chat-1','completed',NULL)")
        db.execute("INSERT INTO chat_events VALUES ('turn-1',4,'execution.tool',?)", (json.dumps({"type": "commandExecution", "phase": "started", "arguments": {"command": "bash scripts/archive-change.sh example --finalize"}}),))
    root, change = fixture(tmp_path)
    plan_path = change / "acceptance-plan.json"
    plan = json.loads(plan_path.read_text())
    plan["checks"] = [{"id": "AC-001", "kind": "product_turn", "inputs": ["input.txt"], "turn_id": "turn-1", "command_contains": "archive-change.sh"}]
    plan_path.write_text(json.dumps(plan))
    assert run_acceptance(root, "check-example", db_path)["status"] == "failed"


def test_trusted_archive_product_turn_requires_same_turn_events_and_completed_operation(tmp_path):
    db_path = tmp_path / "chat.db"
    with sqlite3.connect(db_path) as db:
        db.executescript("""
            CREATE TABLE chat_conversations (id TEXT, owner_id TEXT, space_id TEXT, repository_id TEXT);
            CREATE TABLE chat_turns (id TEXT, conversation_id TEXT, status TEXT, error_code TEXT, prompt TEXT);
            CREATE TABLE chat_relations (conversation_id TEXT, object_id TEXT, role TEXT);
            CREATE TABLE governance_archive_operations (change_id TEXT, stage TEXT, actor_id TEXT);
            CREATE TABLE chat_events (turn_id TEXT, sequence INTEGER, source_id TEXT, event_type TEXT, payload TEXT);
            INSERT INTO chat_conversations VALUES ('chat-1','alice','space','repo');
            INSERT INTO chat_turns VALUES ('turn-1','chat-1','completed',NULL,'/sprint-archive sprint-102');
            INSERT INTO chat_relations VALUES ('chat-1','sprint-102','primary');
            INSERT INTO governance_archive_operations VALUES ('sprint-102','completed','alice');
        """)
        for seq, source, event_type, payload in (
            (1, "archive:started", "execution.state", {"status": "running", "executor": "trusted_archive"}),
            (2, "archive:usage", "execution.usage", {"total_tokens": 0, "usage_scope": "trusted_archive_v1", "usage_pending": False}),
            (3, "archive:terminal", "execution.state", {"status": "completed"}),
        ):
            db.execute("INSERT INTO chat_events VALUES (?,?,?,?,?)", ("turn-1", seq, source, event_type, json.dumps(payload)))
    check = {"turn_id": "turn-1", "command_contains": "/sprint-archive sprint-102",
             "execution_proof": "trusted_archive_v1", "trusted_archive_object_id": "sprint-102", "timeout_seconds": 1}
    result = run_product_turn(check, db_path)
    assert result["status"] == "passed" and result["operation_stage"] == "completed" and result["model_tokens"] == 0
    with sqlite3.connect(db_path) as db:
        db.execute("UPDATE governance_archive_operations SET stage='claimed'")
    assert run_product_turn(check, db_path)["status"] == "failed"
    with sqlite3.connect(db_path) as db:
        db.execute("UPDATE governance_archive_operations SET stage='completed'")
        db.execute("UPDATE chat_events SET payload=? WHERE source_id='archive:usage'", (json.dumps({"total_tokens": 1, "usage_scope": "trusted_archive_v1", "usage_pending": False}),))
    assert run_product_turn(check, db_path)["status"] == "failed"
    with sqlite3.connect(db_path) as db:
        db.execute("UPDATE chat_events SET payload='[]' WHERE source_id='archive:usage'")
    assert run_product_turn(check, db_path)["status"] == "failed"


def test_trusted_archive_plan_binds_exact_sprint_command(tmp_path):
    import pytest
    _, change = fixture(tmp_path)
    path = change / "acceptance-plan.json"
    plan = json.loads(path.read_text())
    plan["checks"] = [{"id": "AC-001", "kind": "product_turn", "inputs": ["input.txt"],
                       "turn_id": "turn-1", "command_contains": "/sprint-archive sprint-102",
                       "execution_proof": "trusted_archive_v1", "trusted_archive_object_id": "sprint-102"}]
    path.write_text(json.dumps(plan))
    assert read_plan(change)["checks"][0]["trusted_archive_object_id"] == "sprint-102"
    plan["checks"][0]["command_contains"] = "/sprint-archive sprint-103"
    path.write_text(json.dumps(plan))
    with pytest.raises(ValueError, match="invalid trusted archive proof"):
        read_plan(change)


def test_product_turn_negative_gate_requires_same_turn_marker(tmp_path):
    db_path = tmp_path / "chat.db"
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE TABLE chat_turns (id TEXT, conversation_id TEXT, status TEXT, error_code TEXT)")
        db.execute("CREATE TABLE chat_events (turn_id TEXT, sequence INTEGER, event_type TEXT, payload TEXT)")
        db.execute("INSERT INTO chat_turns VALUES ('turn-1','chat-1','completed',NULL)")
        db.execute("INSERT INTO chat_events VALUES ('turn-1',4,'execution.tool',?)", (json.dumps({"type": "commandExecution", "phase": "completed", "exit_code": 1, "arguments": {"command": "bash scripts/archive-change.sh check-example --finalize"}, "result": "ACCEPTANCE_GATE_BLOCKED issue_acceptance_pending checked=0 total=2"}),))
    root, change = fixture(tmp_path)
    plan_path = change / "acceptance-plan.json"
    plan = json.loads(plan_path.read_text())
    plan["checks"] = [{"id": "AC-001", "kind": "product_turn", "inputs": ["input.txt"], "turn_id": "turn-1", "command_contains": "bash scripts/archive-change.sh check-example --finalize", "expected_exit_code": 1, "require_acceptance_gate_blocked": True, "effects": [{"kind": "exists", "path": "input.txt"}]}]
    plan_path.write_text(json.dumps(plan))
    assert run_acceptance(root, "check-example", db_path)["status"] == "passed"
    with sqlite3.connect(db_path) as db:
        db.execute("UPDATE chat_events SET payload=? WHERE turn_id='turn-1'", (json.dumps({"type": "commandExecution", "phase": "completed", "exit_code": 1, "arguments": {"command": "bash scripts/archive-change.sh check-example --finalize"}, "result": "spec merge failed"}),))
    (root / "input.txt").write_text("v2", encoding="utf-8")
    assert run_acceptance(root, "check-example", db_path)["status"] == "failed"


def test_negative_gate_plan_requires_expected_exit_and_state_effect(tmp_path):
    root, change = fixture(tmp_path)
    path = change / "acceptance-plan.json"
    plan = json.loads(path.read_text())
    plan["checks"] = [{"id": "AC-001", "kind": "product_turn", "inputs": ["input.txt"], "turn_id": "turn-1", "command_contains": "archive-change.sh", "expected_exit_code": 1, "require_acceptance_gate_blocked": True}]
    path.write_text(json.dumps(plan))
    import pytest
    with pytest.raises(ValueError, match="state effect"):
        read_plan(change)


def test_partial_diagnostic_does_not_replace_complete_readiness_and_can_be_reused(tmp_path):
    root, change = fixture(tmp_path)
    assert run_acceptance(root, change.name, None)["status"] == "passed"
    (root / "input.txt").write_text("v2", encoding="utf-8")
    plan_path = change / "acceptance-plan.json"
    plan = json.loads(plan_path.read_text())
    plan["checks"][1]["argv"] = [sys.executable, "-c", "exit(1)"]
    plan_path.write_text(json.dumps(plan))
    partial = run_acceptance(root, change.name, None, {"AC-001"})
    assert partial["scope"] == "diagnostic"
    assert readiness(root, change.name)["stale"] == ["AC-001", "AC-002"]
    # Restore the other AC; the full run reuses the passed diagnostic result.
    plan["checks"][1]["argv"] = [sys.executable, "-c", "exit(0)"]
    plan_path.write_text(json.dumps(plan))
    full = run_acceptance(root, change.name, None)
    assert full["scope"] == "complete"
    assert readiness(root, change.name)["status"] == "ready"
    manifest = json.loads((root / full["path"] / "manifest.json").read_text())
    assert all(row["reused"] for row in manifest["checks"])


def test_invalid_summary_is_not_publishable(tmp_path):
    import pytest
    with pytest.raises(ValueError, match="title/frontmatter"):
        validate_report({"status": "passed", "checks": [{"id": "AC-001", "status": "passed"}]}, "结论：passed。\n")


def test_summary_must_include_declared_evidence_path(tmp_path):
    import pytest
    manifest = {"status": "passed", "checks": [{"id": "AC-001", "status": "passed", "evidence_kinds": ["visual"],
        "artifacts": [{"path": "evidence/redacted.png", "sha256": "example"}]}]}
    summary = "---\ntitle: 测试\n---\n\n# 测试\n\n结论：passed。\n| AC-001 | passed | visual |\n"
    with pytest.raises(ValueError, match="evidence path"):
        validate_report(manifest, summary)


def test_report_validation_failure_does_not_publish_manifest(tmp_path, monkeypatch):
    import pytest
    import opsx_acceptance

    root, change = fixture(tmp_path)
    def reject_report(_manifest, _summary):
        raise ValueError("invalid report")
    monkeypatch.setattr(opsx_acceptance, "validate_report", reject_report)
    with pytest.raises(ValueError, match="invalid report"):
        run_acceptance(root, change.name, None)
    assert not list((change / "evidence" / "acceptance").glob("*/manifest.json"))


def test_legacy_partial_manifest_cannot_be_readiness_baseline(tmp_path):
    root, change = fixture(tmp_path)
    run = change / "evidence" / "acceptance" / "legacy-partial"
    run.mkdir(parents=True)
    (run / "manifest.json").write_text(json.dumps({"status": "passed", "checks": [
        {"id": "AC-001", "status": "passed"},
        {"id": "AC-002", "status": "blocked", "reason": "not-selected"},
    ]}))
    assert readiness(root, change.name) == {"status": "blocked", "reason": "manifest-missing"}


def test_newer_failed_diagnostic_revokes_older_complete_pass(tmp_path):
    root, change = fixture(tmp_path)
    full = run_acceptance(root, change.name, None)
    passed = json.loads((root / full["path"] / "manifest.json").read_text())
    diagnostic = change / "evidence" / "acceptance" / "newer-diagnostic"
    diagnostic.mkdir()
    (diagnostic / "manifest.json").write_text(json.dumps({
        "scope": "diagnostic", "run_id": "newer-diagnostic", "status": "failed",
        "checks": [{**passed["checks"][0], "status": "failed"}, {"id": "AC-002", "status": "blocked", "reason": "not-selected"}],
    }))
    assert readiness(root, change.name)["stale"] == ["AC-001"]


def test_preflight_diagnostic_does_not_erase_matching_pass(tmp_path):
    from opsx_acceptance import reusable_checks, read_plan

    root, change = fixture(tmp_path)
    result = run_acceptance(root, change.name, None)
    passed = json.loads((root / result["path"] / "manifest.json").read_text())
    diagnostic = change / "evidence" / "acceptance" / "newer-preflight"
    diagnostic.mkdir()
    (diagnostic / "manifest.json").write_text(json.dumps({
        "scope": "diagnostic", "run_id": "newer-preflight", "status": "blocked",
        "checks": [{**row, "status": "blocked", "reason": "preflight-failed"} for row in passed["checks"]],
    }))
    assert set(reusable_checks(root, change, read_plan(change))) == {"AC-001", "AC-002"}


def test_visual_plan_requires_declared_coverage_and_artifact(tmp_path):
    import pytest
    root, change = fixture(tmp_path)
    path = change / "acceptance-plan.json"
    plan = json.loads(path.read_text())
    plan["checks"][0]["evidence_kinds"] = ["command", "visual"]
    path.write_text(json.dumps(plan))
    with pytest.raises(ValueError, match="visual evidence"):
        read_plan(change)
    plan["checks"][0]["coverage"] = {"stages": ["验收中"], "viewports": ["1440px", "390px"]}
    plan["checks"][0]["artifacts"] = ["openspec/changes/check-example/evidence/card.png"]
    path.write_text(json.dumps(plan))
    assert read_plan(change)["checks"][0]["coverage"]["viewports"] == ["1440px", "390px"]


def test_preflight_failure_blocks_without_running_ac(tmp_path):
    root, change = fixture(tmp_path)
    plan_path = change / "acceptance-plan.json"
    plan = json.loads(plan_path.read_text())
    plan["preflight"] = [[sys.executable, "-c", "exit(1)"]]
    plan_path.write_text(json.dumps(plan))
    result = run_acceptance(root, "check-example", None)
    assert result["status"] == "blocked"
    latest = json.loads(next((change / "evidence" / "acceptance").glob("*/manifest.json")).read_text())
    assert all(row["reason"] == "preflight-failed" for row in latest["checks"])


def test_missing_artifact_is_diagnostic_block_before_command(tmp_path):
    root, change = fixture(tmp_path)
    marker = root / "command-ran"
    plan_path = change / "acceptance-plan.json"
    plan = json.loads(plan_path.read_text())
    plan["checks"][0]["argv"] = [sys.executable, "-c", f"from pathlib import Path; Path({str(marker)!r}).write_text('ran')"]
    plan["checks"][0]["artifacts"] = ["openspec/changes/check-example/evidence/missing.png"]
    plan_path.write_text(json.dumps(plan))
    result = run_acceptance(root, change.name, None)
    assert result["status"] == "blocked" and result["scope"] == "diagnostic"
    assert not marker.exists()
    manifest = json.loads((root / result["path"] / "manifest.json").read_text())
    assert any(item.startswith("artifact-missing:") for item in manifest["checks"][0]["effect_problems"])
    assert readiness(root, change.name)["reason"] == "manifest-missing"


def test_visual_matrix_requires_each_stage_viewport_pair(tmp_path):
    root, change = fixture(tmp_path)
    artifact = change / "evidence" / "screen.png"
    artifact.parent.mkdir()
    artifact.write_bytes(b"redacted")
    plan_path = change / "acceptance-plan.json"
    plan = json.loads(plan_path.read_text())
    check = plan["checks"][0]
    check["evidence_kinds"] = ["command", "visual"]
    check["artifacts"] = ["openspec/changes/check-example/evidence/screen.png"]
    check["coverage"] = {"stages": ["首部", "底部"], "viewports": ["1440x900"], "samples": [
        {"stage": "首部", "viewport": "1440x900", "artifacts": check["artifacts"]},
    ]}
    plan_path.write_text(json.dumps(plan))
    blocked = run_acceptance(root, change.name, None)
    assert blocked["status"] == "blocked"
    manifest = json.loads((root / blocked["path"] / "manifest.json").read_text())
    assert "coverage-missing:底部@1440x900" in manifest["checks"][0]["effect_problems"]
    check["coverage"]["samples"].append({"stage": "底部", "viewport": "1440x900", "artifacts": check["artifacts"]})
    plan_path.write_text(json.dumps(plan))
    passed = run_acceptance(root, change.name, None)
    assert passed["status"] == "passed"
    summary = (root / passed["path"] / "summary.md").read_text()
    assert "command, visual" in summary
    assert "evidence/screen.png" in summary


def test_artifact_tampering_invalidates_readiness(tmp_path):
    root, change = fixture(tmp_path)
    artifact = change / "evidence" / "screen.png"
    artifact.parent.mkdir()
    artifact.write_bytes(b"sanitized image")
    plan_path = change / "acceptance-plan.json"
    plan = json.loads(plan_path.read_text())
    plan["checks"][0]["artifacts"] = ["openspec/changes/check-example/evidence/screen.png"]
    plan_path.write_text(json.dumps(plan))
    assert run_acceptance(root, change.name, None)["status"] == "passed"
    artifact.write_bytes(b"changed")
    assert readiness(root, change.name)["stale"] == ["AC-001"]


def test_workflow_sync_preserves_valid_pass_and_invalidates_stale_plan(tmp_path, monkeypatch):
    root, change = fixture(tmp_path)
    monkeypatch.setattr(constants, "ROOT", root)
    issue_dir = root / "issues" / "bugs" / "review" / "BUG-9999-example"
    issue_dir.mkdir(parents=True)
    (issue_dir / "acceptance.md").write_text("---\nacceptance_status: pending\n---\n\n- [ ] AC-001\n- [ ] AC-002\n")
    plan_path = change / "acceptance-plan.json"
    plan = json.loads(plan_path.read_text())
    plan["issue_id"] = issue_dir.name
    plan_path.write_text(json.dumps(plan))
    derived = DerivedIssue(issue_id=issue_dir.name, kind="bug", display_status="in_sprint", linked_change=change.name, note="")
    assert issue_subdocuments.acceptance_status_for(derived, "opsx.modify", issue_path=issue_dir, source_change=change.name) == "pending"
    run_acceptance(root, change.name, None)
    assert issue_subdocuments.acceptance_status_for(derived, "opsx.accept", issue_path=issue_dir, source_change=change.name) == "passed"
    (root / "input.txt").write_text("v2")
    assert issue_subdocuments.acceptance_status_for(derived, "opsx.modify", issue_path=issue_dir, source_change=change.name) == "pending"


def test_archived_evidence_remains_linked_after_change_moves(tmp_path, monkeypatch):
    root, change = fixture(tmp_path)
    monkeypatch.setattr(constants, "ROOT", root)
    issue_dir = root / "issues" / "bugs" / "archive" / "BUG-9999-example"
    issue_dir.mkdir(parents=True)
    (issue_dir / "acceptance.md").write_text("---\nacceptance_status: pending\n---\n\n- [ ] AC-001\n- [ ] AC-002\n")
    plan_path = change / "acceptance-plan.json"
    plan = json.loads(plan_path.read_text())
    plan["issue_id"] = issue_dir.name
    artifact = change / "evidence" / "proof.png"
    artifact.parent.mkdir()
    artifact.write_bytes(b"sanitized proof")
    plan["checks"][0]["artifacts"] = ["openspec/changes/check-example/evidence/proof.png"]
    plan_path.write_text(json.dumps(plan))
    run_acceptance(root, change.name, None)
    target = root / "openspec" / "archive" / "2026-10-12-check-example"
    target.parent.mkdir(parents=True)
    (change / "trace.md").write_text("---\nstatus: archived\nchange_id: check-example\n---\n")
    change.rename(target)
    derived = DerivedIssue(issue_id=issue_dir.name, kind="bug", display_status="done", linked_change="check-example", note="")
    assert issue_subdocuments.acceptance_status_for(derived, "opsx.archive", issue_path=issue_dir, source_change="check-example") == "passed"
    assert issue_subdocuments.acceptance_plan_for(root, "check-example") == target / "acceptance-plan.json"


def test_partial_issue_scope_requires_complete_change_mapping(tmp_path):
    import pytest
    root, change = fixture(tmp_path)
    issue = root/'issues/requirements/review/REQ-0001-example'
    issue.mkdir(parents=True)
    (issue/'acceptance.md').write_text('- [ ] AC-010 full workflow\n- [ ] AC-011 deferred\n')
    plan=json.loads((change/'acceptance-plan.json').read_text())
    plan.update(issue_id='REQ-0001-example',issue_acceptance_scope='partial',scope_description='Only dependency implementation',issue_ac_mapping={'AC-001':['AC-010'],'AC-002':['AC-010']})
    (change/'acceptance.md').write_text('- [ ] AC-001 subset one\n- [ ] AC-002 subset two\n')
    def save(): (change/'acceptance-plan.json').write_text(json.dumps(plan))
    save(); assert read_plan(change)['issue_acceptance_scope']=='partial'
    plan['issue_ac_mapping']['AC-002']=['AC-099']; save()
    with pytest.raises(ValueError,match='explicit Issue mapping'): read_plan(change)
    plan['issue_ac_mapping']['AC-002']=['AC-010']
    (change/'acceptance.md').write_text('- [ ] AC-001 subset one\n')
    save()
    with pytest.raises(ValueError,match='local AC coverage'): read_plan(change)
    plan['issue_acceptance_scope']='full'; save()
    with pytest.raises(ValueError,match='AC set differs'): read_plan(change)
