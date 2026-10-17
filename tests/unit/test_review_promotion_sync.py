"""BUG-0033: review moves and their registry projection cannot finish separately."""
import shutil
import subprocess
import sys
import runpy
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
OID = "BUG-0033-opsx-apply-governance-scope-source-readonly"


def test_archive_promotion_reads_bug_related_change_scalar():
    namespace = runpy.run_path(str(ROOT / "scripts/promote-issue-stage.py"))
    trace = "---\nrelated_change: fix-chat-standalone-archive-scope-tool-path\n---\n"
    assert namespace["change_refs_from_trace"](trace) == ["fix-chat-standalone-archive-scope-tool-path"]


@pytest.fixture
def project(tmp_path):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for name in ("promote-issue-stage.py", "sync-workflow-status.py"):
        shutil.copy2(ROOT / "scripts" / name, scripts / name)
    shutil.copytree(ROOT / "scripts/workflow_sync", scripts / "workflow_sync",
                    ignore=shutil.ignore_patterns("__pycache__"))
    titles = tmp_path / "src/backend/app/governance/titles.py"
    titles.parent.mkdir(parents=True)
    shutil.copy2(ROOT / "src/backend/app/governance/titles.py", titles)
    shutil.copy2(ROOT / "src/backend/app/governance/lifecycle.py", titles.parent / "lifecycle.py")
    (tmp_path / "openspec/changes").mkdir(parents=True)
    base = tmp_path / "issues/bugs"
    folder = base / "plan" / OID
    folder.mkdir(parents=True)
    for name in ("bug.md", "trace.md", "review.md", "capture.md"):
        (folder / name).write_text(
            "---\nbug_id: " + OID + "\ntitle: 评审迁移测试\nstatus: approved\n"
            "lifecycle_stage: plan\niteration: null\nopenspec_changes: []\n"
            "created_at: 2026-10-06 22:22:15\nupdated_at: 2026-10-07 13:11:12\n"
            "severity: high\n---\n# 评审迁移测试\n\n评审结论已确认，保留已有文档。\n")
    (folder / "capture.md").write_text(
        f"---\nbug_id: {OID}\ntitle: 评审迁移测试\ncreated_at: 2026-10-06 22:22:15\n"
        "updated_at: 2026-10-07 13:11:12\nseverity: high\n---\n# 评审迁移测试\n\n保留原始采集内容。\n")
    (base / "_registry.yaml").write_text(yaml.safe_dump({"next_id": 35, "entries": [
        {"id": OID, "title": "评审迁移测试", "status": "pending_review",
         "severity": "high", "path": f"issues/bugs/plan/{OID}/", "lifecycle_stage": "plan"},
        {"id": "BUG-0034-unrelated", "status": "captured", "path": "keep-me"},
    ]}, allow_unicode=True, sort_keys=False))
    (base / "CHANGELOG.md").write_text("# 缺陷索引\n\n| ID | 状态 | 路径 |\n|---|---|---|\n"
        f"| {OID} | pending_review | issues/bugs/plan/{OID}/ |\n")
    return tmp_path


def run(root, *options):
    return subprocess.run([sys.executable, str(root / "scripts/promote-issue-stage.py"),
        "--to", "review", "--bug", OID, *options], cwd=root, capture_output=True, text=True)


def test_bug0033_move_sync_and_retry(project):
    base = project / "issues/bugs"
    capture = (base / "plan" / OID / "capture.md").read_bytes()
    result = run(project)
    assert result.returncode == 0, result.stdout + result.stderr
    rows = yaml.safe_load((base / "_registry.yaml").read_text())["entries"]
    assert rows[0]["status"] == "approved"
    assert rows[0]["lifecycle_stage"] == "review"
    assert rows[0]["path"] == f"issues/bugs/review/{OID}/"
    assert rows[1] == {"id": "BUG-0034-unrelated", "status": "captured", "path": "keep-me"}
    assert (base / "review" / OID / "capture.md").read_bytes().split(b"---", 2)[2] == capture.split(b"---", 2)[2]
    assert not (base / "plan" / OID).exists()
    assert f"issues/bugs/review/{OID}" in (base / "CHANGELOG.md").read_text()
    before = {p: p.read_bytes() for p in base.rglob("*") if p.is_file()}
    assert run(project).returncode == 0
    assert {p: p.read_bytes() for p in before} == before


def test_bug0033_retained_move_recovers_after_sync_failure(project):
    script = project / "scripts/sync-workflow-status.py"
    original = script.read_bytes()
    script.write_text("raise SystemExit(2)\n")
    result = run(project)
    assert result.returncode != 0
    assert "documents retained" in result.stdout
    assert (project / "issues/bugs/review" / OID / "review.md").is_file()
    script.write_bytes(original)
    result = run(project)
    assert result.returncode == 0, result.stdout + result.stderr
    row = yaml.safe_load((project / "issues/bugs/_registry.yaml").read_text())["entries"][0]
    assert row["status"] == "approved"
    assert "/review/" in row["path"]


@pytest.mark.parametrize("option", ["--dry-run", "--check"])
def test_preview_does_not_mutate(project, option):
    before = {p: p.read_bytes() for p in (project / "issues").rglob("*") if p.is_file()}
    run(project, option)
    assert {p: p.read_bytes() for p in (project / "issues").rglob("*") if p.is_file()} == before


def test_success_exit_without_registry_sync_is_failure(project):
    (project / "scripts/sync-workflow-status.py").write_text("raise SystemExit(0)\n")
    assert run(project).returncode == 1
    assert (project / "issues/bugs/review" / OID / "review.md").is_file()


def test_destination_conflict_keeps_both_directories(project):
    base = project / "issues/bugs"
    (base / "review" / OID).mkdir(parents=True)
    registry = (base / "_registry.yaml").read_bytes()
    assert run(project).returncode == 1
    assert (base / "plan" / OID / "trace.md").is_file()
    assert (base / "_registry.yaml").read_bytes() == registry
