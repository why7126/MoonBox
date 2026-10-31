from pathlib import Path
from types import SimpleNamespace
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from sprint_close_stale_scan import current_issue_state_lines, scan_issue_line


ISSUE = "BUG-0001-history-example"
CHANGE = "fix-history-example"


def _hits(tmp_path: Path, filename: str, text: str):
    path = tmp_path / filename
    path.write_text(text, encoding="utf-8")
    lines = text.splitlines()
    state_lines = current_issue_state_lines(path, lines)
    return [
        hit
        for line_no, line in enumerate(lines, 1)
        for hit in scan_issue_line(
            issue_id=ISSUE,
            line=line,
            line_no=line_no,
            file_path=path,
            root=tmp_path,
            derived_issues={ISSUE: SimpleNamespace(display_status="done", linked_change=CHANGE)},
            derived_changes={CHANGE: SimpleNamespace(state="archived")},
            current_state_lines=state_lines,
        )
    ]


def test_historical_status_and_sample_do_not_block(tmp_path):
    text = (
        "---\nstatus: done\n---\n# 验收\n"
        "2026-10-01 当时验收 pending，样本 Change applied。\n"
        "| 日期 | 状态 |\n| 2026-10-01 | in_sprint |\n"
        "```yaml\nstatus: pending\n```\n"
    )
    assert _hits(tmp_path, "trace.md", text) == []


def test_current_metadata_blocks_but_nested_status_does_not(tmp_path):
    text = "---\nstatus: in_sprint\nopenspec_changes:\n  - status: archived\n---\n# 历史\napplied\n"
    hits = _hits(tmp_path, "trace.md", text)
    assert [(hit.kind, hit.line) for hit in hits] == [("issue-subdocument-stale-state", 2)]


def test_current_acceptance_and_active_evidence_path_block(tmp_path):
    text = (
        "---\nacceptance_status: pending\n---\n# 验收\n"
        f"[证据](../../../../openspec/changes/{CHANGE}/evidence/summary.md)\n"
    )
    hits = _hits(tmp_path, "acceptance.md", text)
    assert {hit.kind for hit in hits} == {
        "issue-subdocument-stale-state",
        "issue-subdocument-active-change-path",
    }


def test_top_yaml_current_state_blocks(tmp_path):
    text = "```yaml\nstatus: applied\n```\n# 追溯\n历史 pending\n"
    hits = _hits(tmp_path, "trace.md", text)
    assert [(hit.kind, hit.line) for hit in hits] == [("issue-subdocument-stale-state", 2)]


def test_issue_title_is_not_current_wait_but_remaining_text_is(tmp_path):
    from sprint_close_stale_scan import scan_line
    title = "独立 Change 未纳入迭代却提前显示待开发"
    def check(line):
        return scan_line(line=line, line_no=1, file_path=tmp_path / "sprint.md",
            root=tmp_path, sprint=SimpleNamespace(requirements=[], bugs=[ISSUE], sprint_id="sprint-017"),
            issues={ISSUE: SimpleNamespace(title=title, kind="bug")}, derived_issues={},
            derived_changes={CHANGE: SimpleNamespace(state="archived")})
    for identity in [ISSUE, "BUG-0001"]:
        line = f"| {identity} | {title} | done | archived `{CHANGE}` |"
        assert check(line) == []
        assert any(h.kind == "stale-change-apply" for h in check(line + " 待实现"))
        assert any(h.kind == "stale-change-apply" for h in check(line + " 待 `/opsx-apply`"))
    assert check(f"{title} `{CHANGE}`")
