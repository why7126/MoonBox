from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.workflow_sync.collect import IssueRecord, SprintRecord
from scripts.workflow_sync.derive import DerivedIssue
from scripts.workflow_sync.patch import (
    patch_issue_changelog_index,
    patch_issue_trace,
    patch_registry_entry,
)


def test_bug_sprint_propose_patches_trace_registry_and_changelog(tmp_path, monkeypatch) -> None:
    import scripts.workflow_sync.patch as patch_module

    monkeypatch.setattr(patch_module, "ROOT", tmp_path)
    issue_dir = tmp_path / "issues/bugs/review/BUG-0099-sync-drift"
    issue_dir.mkdir(parents=True)
    trace_path = issue_dir / "trace.md"
    trace_path.write_text(
        """---
bug_id: BUG-0099-sync-drift
status: approved
lifecycle_stage: review
iteration:
related_change:
openspec_changes:
  - change_id: fix-sync-drift
    type: fix
    status: proposed
---

# 追溯

```yaml
lifecycle:
  status: approved
  stage: plan
  iteration: null
  related_change: null
openspec_changes:
  - change_id: fix-sync-drift
    type: fix
    status: proposed
status: approved
```
""",
        encoding="utf-8",
    )
    registry_path = tmp_path / "issues/bugs/_registry.yaml"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(
        """entries:
  - id: BUG-0099-sync-drift
    title: Sync drift
    status: approved
    severity: medium
    priority: P2
    lifecycle_stage: plan
    path: issues/bugs/plan/BUG-0099-sync-drift/
    related_change: null
    iteration: null
""",
        encoding="utf-8",
    )
    changelog_path = tmp_path / "issues/bugs/CHANGELOG.md"
    changelog_path.write_text(
        """# 缺陷当前态看板索引

| BUG | 标题 | 严重等级 | 当前状态 | 阶段 | 关联 Sprint | 关联 Change | 最近更新时间 | 下一步 | 事实源 |
|---|---|---|---|---|---|---|---|---|---|
| BUG-0099-sync-drift | Sync drift | medium | approved | review | 无 | 无 | 2026-08-15 10:00:00 | `/sprint-propose --bug BUG-0099-sync-drift` | `issues/bugs/review/BUG-0099-sync-drift/trace.md` |
""",
        encoding="utf-8",
    )

    issue = IssueRecord(
        issue_id="BUG-0099-sync-drift",
        kind="bug",
        path=issue_dir,
        title="Sync drift",
        priority="medium",
        trace_status="approved",
        related_change="fix-sync-drift",
        openspec_changes=[{"change_id": "fix-sync-drift", "type": "fix", "status": "proposed"}],
    )
    derived = DerivedIssue(
        issue_id=issue.issue_id,
        kind="bug",
        display_status="in_sprint",
        linked_change="fix-sync-drift",
        note="proposed `fix-sync-drift`",
    )
    sprint = SprintRecord(
        sprint_id="sprint-099",
        path=tmp_path / "iterations/change/sprint-099",
        status="planning",
        bugs=[issue.issue_id],
        changes=["fix-sync-drift"],
    )

    trace_result = patch_issue_trace(
        issue,
        derived,
        {"fix-sync-drift": "proposed"},
        sprint=sprint,
        event="sprint.propose",
        write=True,
    )
    registry_result = patch_registry_entry(registry_path, issue, derived, sprint, write=True)
    changelog_result = patch_issue_changelog_index(issue, derived, sprint, write=True)
    second_changelog_result = patch_issue_changelog_index(issue, derived, sprint, write=False)

    trace_text = trace_path.read_text(encoding="utf-8")
    registry_text = registry_path.read_text(encoding="utf-8")
    changelog_text = changelog_path.read_text(encoding="utf-8")

    assert trace_result.changed
    assert "iteration: sprint-099" in trace_text
    assert "status: in_sprint" in trace_text
    assert "stage: review" in trace_text
    assert registry_result.changed
    assert "path: issues/bugs/review/BUG-0099-sync-drift/" in registry_text
    assert "iteration: sprint-099" in registry_text
    assert "related_change: fix-sync-drift" in registry_text
    assert changelog_result.changed
    assert "| BUG-0099-sync-drift | Sync drift | medium | in_sprint | review | sprint-099 | fix-sync-drift |" in changelog_text
    assert "`/opsx-apply BUG-0099-sync-drift`" in changelog_text
    assert not second_changelog_result.changed

    applied = DerivedIssue(
        issue_id=issue.issue_id,
        kind="bug",
        display_status="in_sprint",
        linked_change="fix-sync-drift",
        note="apply 完成；待 archive `fix-sync-drift`",
    )
    patch_issue_changelog_index(issue, applied, sprint, write=True)
    assert "`/opsx-archive BUG-0099-sync-drift`" in changelog_path.read_text(encoding="utf-8")
