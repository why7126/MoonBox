import hashlib
import json
from pathlib import Path

from scripts import opsx_acceptance as acceptance


def _fixture(tmp_path: Path, monkeypatch):
    change = "fix-example"
    archive = tmp_path / "openspec" / "archive" / f"2026-10-17-{change}"
    archive.mkdir(parents=True)
    (archive / "trace.md").write_text("---\nstatus: archived\nchange_id: fix-example\n---\n")
    evidence = archive / "verification.md"
    evidence.write_text("new evidence\n", encoding="utf-8")
    old = hashlib.sha256(b"old evidence\n").hexdigest()
    row = {"id": "AC-001", "status": "passed", "artifacts": [{"path": f"openspec/changes/{change}/verification.md", "sha256": old}]}
    manifest = {"run_id": "original-run", "checks": [row]}
    check = {"id": "AC-001", "kind": "command", "argv": ["python", "-V"]}
    monkeypatch.setattr(acceptance, "read_plan", lambda _: {"change_id": change, "checks": [check]})
    monkeypatch.setattr(acceptance, "fingerprint", lambda *_: "input-hash")
    supplement = {
        "schema_version": 1,
        "change_id": change,
        "source_run_id": "original-run",
        "check_id": "AC-001",
        "input_fingerprint": "input-hash",
        "argv": check["argv"],
        "exit_code": 0,
        "artifacts": [{"path": row["artifacts"][0]["path"], "previous_sha256": old,
                       "current_sha256": hashlib.sha256(evidence.read_bytes()).hexdigest()}],
    }
    path = archive / "evidence" / "acceptance" / "supplements" / "AC-001.json"
    path.parent.mkdir(parents=True)
    return archive, evidence, manifest, supplement, path


def test_valid_supplement_preserves_original_manifest(tmp_path, monkeypatch):
    archive, _, manifest, supplement, path = _fixture(tmp_path, monkeypatch)
    original = json.dumps(manifest, sort_keys=True)
    assert not acceptance.archived_manifest_artifacts_match(tmp_path, archive, manifest)
    path.write_text(json.dumps(supplement), encoding="utf-8")
    assert acceptance.archived_manifest_artifacts_match(tmp_path, archive, manifest)
    assert json.dumps(manifest, sort_keys=True) == original


def test_changed_input_or_artifact_revokes_supplement(tmp_path, monkeypatch):
    archive, evidence, manifest, supplement, path = _fixture(tmp_path, monkeypatch)
    path.write_text(json.dumps(supplement), encoding="utf-8")
    monkeypatch.setattr(acceptance, "fingerprint", lambda *_: "changed-input")
    assert not acceptance.archived_manifest_artifacts_match(tmp_path, archive, manifest)
    monkeypatch.setattr(acceptance, "fingerprint", lambda *_: "input-hash")
    evidence.write_text("changed again\n", encoding="utf-8")
    assert not acceptance.archived_manifest_artifacts_match(tmp_path, archive, manifest)


def test_wrong_command_or_other_ac_mismatch_is_rejected(tmp_path, monkeypatch):
    archive, _, manifest, supplement, path = _fixture(tmp_path, monkeypatch)
    supplement["argv"] = ["other"]
    path.write_text(json.dumps(supplement), encoding="utf-8")
    assert not acceptance.archived_manifest_artifacts_match(tmp_path, archive, manifest)
    manifest["checks"].append({"id": "AC-002", "status": "passed", "artifacts": [
        {"path": "missing.md", "sha256": "0" * 64}]})
    assert not acceptance.archived_manifest_artifacts_match(tmp_path, archive, manifest)
