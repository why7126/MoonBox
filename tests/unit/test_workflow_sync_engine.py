from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.workflow_sync.collect import IssueRecord, SprintRecord
from scripts.workflow_sync.collect import load_issue_record, parse_frontmatter
from scripts.workflow_sync.derive import DerivedChange, DerivedIssue
from scripts.workflow_sync.engine import SyncEngine, SyncReport
from scripts.workflow_sync.issue_subdocuments import (
    SubdocumentFinding,
    SubdocumentSyncResult,
)
from scripts.workflow_sync.patch import PatchResult


def test_frontmatter_parser_ignores_nested_observability_status() -> None:
    text = """---
title: 嵌套状态边界
status: in_sprint
product_data_collection_observability:
  status: not_applicable
  reason: 测试夹具仅用于验证嵌套状态解析边界，不影响 API、DB、请求日志、行为事件、Task Trace、对象存储或请求封装。
  affected_layers: []
---
"""

    assert parse_frontmatter(text)["status"] == "in_sprint"


def test_load_issue_record_uses_top_level_status_before_nested_observability(tmp_path) -> None:
    issue_dir = tmp_path / "REQ-0099-observability-boundary"
    issue_dir.mkdir()
    (issue_dir / "requirement.md").write_text(
        "---\ntitle: 嵌套状态边界\npriority: P2\n---\n",
        encoding="utf-8",
    )
    (issue_dir / "trace.md").write_text(
        """---
status: in_sprint
product_data_collection_observability:
  status: not_applicable
  reason: 测试夹具仅用于验证嵌套状态解析边界，不影响 API、DB、请求日志、行为事件、Task Trace、对象存储或请求封装。
  affected_layers: []
---
""",
        encoding="utf-8",
    )

    issue = load_issue_record(issue_dir, "req")

    assert issue is not None
    assert issue.trace_status == "in_sprint"


def test_req_opsx_changelog_uses_newly_linked_change(monkeypatch) -> None:
    import scripts.workflow_sync.engine as engine_module

    issue = IssueRecord(
        issue_id="REQ-0099-sync-next",
        kind="req",
        path=Path("issues/requirements/review/REQ-0099-sync-next"),
        title="Sync next",
        priority="P2",
        trace_status="in_sprint",
        openspec_changes=[],
    )
    sprint = SprintRecord(
        sprint_id="sprint-099",
        path=Path("iterations/change/sprint-099"),
        status="planning",
        requirements=[issue.issue_id],
        changes=[],
    )
    change = DerivedChange(
        change_id="add-sync-next",
        state="proposed",
        display_status="proposed",
        note="proposed `add-sync-next`",
        tasks_done=0,
        tasks_total=1,
        linked_req=issue.issue_id,
        linked_bug=None,
        archive_date=None,
    )
    captured: list[str | None] = []

    monkeypatch.setattr(engine_module, "resolve_sprint_id", lambda *args, **kwargs: ("sprint-099", None))
    monkeypatch.setattr(engine_module, "load_all_issues", lambda: {issue.issue_id: issue})
    monkeypatch.setattr(engine_module, "run_openspec_list", lambda: {})
    monkeypatch.setattr(engine_module, "load_sprint", lambda sprint_id: sprint)
    monkeypatch.setattr(engine_module, "load_change_record", lambda *args, **kwargs: object())
    monkeypatch.setattr(engine_module, "derive_change_state", lambda record: change)
    monkeypatch.setattr(
        engine_module,
        "derive_issue",
        lambda issue_record, changes, sprint_record: DerivedIssue(
            issue_id=issue_record.issue_id,
            kind=issue_record.kind,
            display_status="in_sprint",
            linked_change=None,
            note="status `in_sprint`",
        ),
    )

    no_delta = lambda *args, **kwargs: PatchResult("noop", False, "")
    monkeypatch.setattr(engine_module, "patch_sprint_yaml_scope", no_delta)
    monkeypatch.setattr(engine_module, "patch_sprint_md", no_delta)
    monkeypatch.setattr(engine_module, "patch_release_note", no_delta)
    monkeypatch.setattr(engine_module, "patch_acceptance_report", no_delta)
    monkeypatch.setattr(engine_module, "patch_issue_trace", no_delta)
    monkeypatch.setattr(engine_module, "patch_registry_entry", no_delta)
    monkeypatch.setattr(engine_module, "patch_parent_requirement_bug_index", no_delta)

    def capture_changelog(issue_record, derived, sprint_record, write=True):
        captured.append(derived.linked_change)
        return PatchResult("issues/requirements/CHANGELOG.md", False, issue_record.issue_id)

    monkeypatch.setattr(engine_module, "patch_issue_changelog_index", capture_changelog)

    report = SyncEngine().run(
        sprint_id="auto",
        event="req.opsx",
        req_id=issue.issue_id,
        change_id=change.change_id,
    )

    assert report.ok
    assert captured == [change.change_id]


def test_subdocument_summary_lists_apply_details() -> None:
    result = SubdocumentSyncResult(
        issue_id="REQ-0099-sync-output",
        checked_files=2,
        updated_files=1,
        updated_fields=2,
        acceptance_status="pending",
        findings=[
            SubdocumentFinding(
                issue_id="REQ-0099-sync-output",
                file=ROOT / "issues/requirements/review/REQ-0099-sync-output/requirement.md",
                source="frontmatter.status",
                current="approved",
                target="in_sprint",
                classification="safe_sync",
                safe_to_sync=True,
                reason="primary document mirrors trace status",
            )
        ],
    )
    report = SyncReport(event="opsx.apply", focus_issue=result.issue_id, subdocument_results=[result])

    summary = report.format_summary()

    assert "updated_fields=2" in summary
    assert "Subdocument apply details" in summary
    assert "safe_sync" in summary
