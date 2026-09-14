from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_promote_module():
    path = ROOT / "scripts/promote-issues-for-archive.py"
    spec = importlib.util.spec_from_file_location("promote_issues_for_archive", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_refresh_promoted_indexes_uses_archive_path(tmp_path, monkeypatch):
    promote = load_promote_module()
    import scripts.workflow_sync.collect as collect
    import scripts.workflow_sync.patch as patch
    from scripts.workflow_sync.collect import IssueRecord, SprintRecord

    monkeypatch.setattr(promote, "ROOT", tmp_path)
    monkeypatch.setattr(collect, "ROOT", tmp_path)
    monkeypatch.setattr(patch, "ROOT", tmp_path)
    promote.patch_registry_entry.__globals__["ROOT"] = tmp_path
    promote.patch_issue_changelog_index.__globals__["ROOT"] = tmp_path
    promote.load_change_record.__globals__["ROOT"] = tmp_path
    monkeypatch.setattr(promote, "run_openspec_list", lambda: {"changes": []})

    issue_dir = tmp_path / "issues/bugs/archive/BUG-0099-sync-drift"
    issue_dir.mkdir(parents=True)
    (issue_dir / "trace.md").write_text(
        """---
bug_id: BUG-0099-sync-drift
status: done
lifecycle_stage: archive
iteration: sprint-099
related_change: fix-sync-drift
openspec_changes:
  - change_id: fix-sync-drift
    type: fix
    status: archived
---

# Trace
""",
        encoding="utf-8",
    )
    (issue_dir / "bug.md").write_text(
        """---
bug_id: BUG-0099-sync-drift
status: done
severity: high
related_change: fix-sync-drift
---

# Sync drift
""",
        encoding="utf-8",
    )

    registry_path = tmp_path / "issues/bugs/_registry.yaml"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(
        """entries:
  - id: BUG-0099-sync-drift
    title: Sync drift
    status: done
    severity: high
    lifecycle_stage: review
    path: issues/bugs/review/BUG-0099-sync-drift/
    related_change: fix-sync-drift
    iteration: sprint-099
""",
        encoding="utf-8",
    )
    changelog_path = tmp_path / "issues/bugs/CHANGELOG.md"
    changelog_path.write_text(
        """# 缺陷当前态看板索引

| BUG | 标题 | 严重等级 | 当前状态 | 阶段 | 关联 Sprint | 关联 Change | 最近更新时间 | 下一步 | 事实源 |
|---|---|---|---|---|---|---|---|---|---|
| BUG-0099-sync-drift | Sync drift | high | done | review | sprint-099 | fix-sync-drift | 2026-09-14 08:00:00 | 无 | `issues/bugs/review/BUG-0099-sync-drift/trace.md` |
""",
        encoding="utf-8",
    )

    sprint_dir = tmp_path / "iterations/change/sprint-099"
    sprint_dir.mkdir(parents=True)
    (sprint_dir / "sprint.yaml").write_text(
        """sprint_id: sprint-099
status: planning
bugs:
  - BUG-0099-sync-drift
changes:
  - fix-sync-drift
""",
        encoding="utf-8",
    )

    archive_dir = tmp_path / "openspec/archive/2026-09-14-fix-sync-drift"
    archive_dir.mkdir(parents=True)
    (archive_dir / "tasks.md").write_text("- [x] done\n", encoding="utf-8")
    (archive_dir / "trace.md").write_text(
        """---
status: archived
change_id: fix-sync-drift
bug_id: BUG-0099-sync-drift
---
""",
        encoding="utf-8",
    )
    (archive_dir / "proposal.md").write_text(
        """---
change_id: fix-sync-drift
bug_id: BUG-0099-sync-drift
---
""",
        encoding="utf-8",
    )

    candidate = promote.PromotionCandidate(
        issue_id="BUG-0099-sync-drift",
        kind="bug",
        stage="review",
        status="done",
        change_ids=["fix-sync-drift"],
        pending_changes=[],
        reason="test",
    )
    issue = IssueRecord(
        issue_id="BUG-0099-sync-drift",
        kind="bug",
        path=issue_dir,
        title="Sync drift",
        priority="high",
        trace_status="done",
        related_change="fix-sync-drift",
        openspec_changes=[{"change_id": "fix-sync-drift", "type": "fix", "status": "archived"}],
    )
    sprint = SprintRecord(
        sprint_id="sprint-099",
        path=sprint_dir,
        status="planning",
        bugs=["BUG-0099-sync-drift"],
        changes=["fix-sync-drift"],
    )
    monkeypatch.setattr(promote, "load_all_issues", lambda: {issue.issue_id: issue})
    monkeypatch.setattr(promote, "load_sprint", lambda sprint_id: sprint)

    assert promote.refresh_promoted_indexes(
        [candidate],
        sprint_id="sprint-099",
        change_id=None,
        dry_run=False,
    ) == 0

    registry_text = registry_path.read_text(encoding="utf-8")
    changelog_text = changelog_path.read_text(encoding="utf-8")
    assert "lifecycle_stage: archive" in registry_text
    assert "path: issues/bugs/archive/BUG-0099-sync-drift/" in registry_text
    assert "| BUG-0099-sync-drift | Sync drift | high | done | archive | sprint-099 | fix-sync-drift |" in changelog_text
    assert "`issues/bugs/archive/BUG-0099-sync-drift/trace.md`" in changelog_text
