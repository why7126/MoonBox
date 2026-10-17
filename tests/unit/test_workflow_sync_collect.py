from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_infer_change_links_ignores_proposal_body_issue_mentions(tmp_path, monkeypatch):
    import scripts.workflow_sync.collect as collect

    monkeypatch.setattr(collect, "ROOT", tmp_path)
    change_dir = tmp_path / "openspec/archive/2026-09-14-refresh-issue-index-after-archive-promotion"
    change_dir.mkdir(parents=True)
    (change_dir / "proposal.md").write_text(
        """---
created_at: 2026-09-14 09:01:23
---

BUG-0014 归档时发现 promote 后索引短暂保留旧路径，本 Change 只修复治理脚本。
""",
        encoding="utf-8",
    )

    assert collect.infer_change_links("refresh-issue-index-after-archive-promotion", {}) == (None, None)


def test_infer_change_links_uses_proposal_frontmatter(tmp_path, monkeypatch):
    import scripts.workflow_sync.collect as collect

    monkeypatch.setattr(collect, "ROOT", tmp_path)
    bug_dir = tmp_path / "issues/bugs/archive/BUG-0014-sync"
    bug_dir.mkdir(parents=True)
    change_dir = tmp_path / "openspec/archive/2026-09-14-fix-sync"
    change_dir.mkdir(parents=True)
    (change_dir / "proposal.md").write_text(
        """---
bug_id: BUG-0014-sync
---

# Fix
""",
        encoding="utf-8",
    )

    assert collect.infer_change_links("fix-sync", {}) == (None, "BUG-0014-sync")


def test_sprint_scope_accepts_yaml_indentless_lists(tmp_path, monkeypatch):
    import scripts.workflow_sync.collect as collect

    monkeypatch.setattr(collect, "ROOT", tmp_path)
    sprint = tmp_path / "iterations/change/sprint-010"
    sprint.mkdir(parents=True)
    (sprint / "sprint.yaml").write_text(
        """id: sprint-010
status: planning
requirements:
- REQ-9108-isolated
changes:
- add-isolated-apply-ac010
scope_estimates:
- id: REQ-9108-isolated
  change: add-isolated-apply-ac010
""", encoding="utf-8",
    )

    assert collect.find_sprints_for_change("add-isolated-apply-ac010") == ["sprint-010"]


def test_load_sprint_rejects_malformed_yaml(tmp_path, monkeypatch):
    import pytest
    import scripts.workflow_sync.collect as collect

    monkeypatch.setattr(collect, "ROOT", tmp_path)
    sprint = tmp_path / "iterations/change/sprint-010"
    sprint.mkdir(parents=True)
    (sprint / "sprint.yaml").write_text(
        """sprint_id: sprint-010
requirements:
- REQ-9108-isolated
scope_estimates:
- id: REQ-9108-isolated
  size: M
  - id: REQ-9208-malformed
    size: S
""", encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid Sprint YAML"):
        collect.load_sprint("sprint-010")
