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
