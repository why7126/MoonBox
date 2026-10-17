"""REQ-0022 acceptance regression: archived facts and validation document sources."""
from pathlib import Path

import pytest
import yaml

from app.services import requirement_center as service


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.mark.parametrize("status,root_status", [("draft", "hypothesis"), ("enriching", "hypothesis"), ("enriching", "confirmed"), ("pending_review", "confirmed")])
def test_completion_card_preserves_raw_status_and_real_documents(tmp_path, status, root_status):
    issue = tmp_path / "issues/bugs/plan/BUG-0099-validation"
    for name in ["capture.md", "bug.md", "acceptance.md", "workaround.md"]:
        write(issue / name, "# 测试文档\n")
    write(issue / "trace.md", f"---\nstatus: {status}\n---\n")
    write(issue / "root-cause.md", f"---\nstatus: {root_status}\n---\n# 根因分析\n")
    with service.using_governance_root(tmp_path):
        row = service._build_issue("bug", dict(id=issue.name, path=str(issue.relative_to(tmp_path)), status=status, severity="medium"))
    assert row.status == status
    assert row.stage == ("review-ready" if status == "pending_review" else "planning")
    assert {"root-cause.md", "acceptance.md", "workaround.md"} <= set(row.documents)
    if status == "enriching":
        assert ("尚未确认" if root_status == "hypothesis" else "仍需完成") in row.completion_hint
        assert row.action.disabled_reason is None
        assert row.action.command.startswith("/bug-complete")
    else:
        assert row.completion_hint is None


def test_archived_issue_and_sprint_do_not_reopen_or_block(tmp_path):
    issue = tmp_path / "issues/requirements/archive/REQ-0099-validation"
    write(issue / "trace.md", "---\nstatus: done\n---\n")
    write(tmp_path / "iterations/archive/sprint-099/sprint.yaml", "requirements: [REQ-0099-validation]\n")
    archived = tmp_path / "openspec/archive/2026-09-11-validation"
    write(archived / "trace.md", "---\nstatus: in_progress\n---\n")
    write(archived / "tasks.md", "- [x] complete\n")
    entry = dict(id=issue.name, path=str(issue.relative_to(tmp_path)), status="done", iteration="sprint-099", related_change="validation")
    with service.using_governance_root(tmp_path):
        row = service._build_issue("requirement", entry)
        assert row.stage == "done"
        assert row.blocked is None
        assert row.drift_warnings == []
        assert row.task_progress == (1, 1)
        assert service.read_requirement_center_change_document("validation", "tasks.md")[0] == "- [x] complete\n"
        with pytest.raises(PermissionError):
            service.update_requirement_center_change_document("validation", "tasks.md", "- [ ] complete\n", task_toggle=True)
        # A stale or missing historical Change cannot undo the issue terminal state.
        entry["related_change"] = "missing"
        assert service._build_issue("requirement", entry).stage == "done"


def test_acceptance_checks_issue_documents_not_card_display_list(tmp_path):
    issue = tmp_path / "issues/requirements/review/REQ-0099-validation"
    write(issue / "trace.md", "---\nstatus: in_sprint\n---\n")
    write(issue / "acceptance.md", "# Acceptance\n")
    write(tmp_path / "openspec/changes/validation/trace.md", "---\nstatus: applied\n---\n")
    write(
        tmp_path / "openspec/changes/validation/tasks.md",
        "\n".join(
            [
                "# Tasks",
                "## 实施任务",
                "- [x] complete",
                "## 回归验证",
                "- [x] unit tests",
                "- [ ] e2e tests",
                "## 验收返修",
                "- [ ] 返修验证截图",
                "- [ ] 人工复验通过",
            ]
        )
        + "\n",
    )
    entry = dict(id=issue.name, path=str(issue.relative_to(tmp_path)), status="in_sprint", related_change="validation")
    with service.using_governance_root(tmp_path):
        row = service._build_issue("requirement", entry)
        assert row.stage == "acceptance" and row.blocked == "验收结论待核实，请查看 acceptance.md 与交付证据"
        assert row.task_progress == (1, 1)
        assert row.test_progress == (1, 3)
        assert row.manual_acceptance_progress == (0, 1)
        (issue / "acceptance.md").unlink()
        assert service._build_issue("requirement", entry).blocked == "缺少 acceptance.md"
        write(issue / "acceptance.md", " ")
        assert "文档内容为空" in service._build_issue("requirement", entry).blocked


def test_generated_issue_documents_remain_issue_owned_after_change(tmp_path):
    issue = tmp_path / "issues/bugs/review/BUG-0099-validation"
    entry = dict(id=issue.name, path=str(issue.relative_to(tmp_path)), status="in_sprint", related_change="validation", severity="medium")
    write(tmp_path / "issues/bugs/_registry.yaml", yaml.safe_dump({"entries": [entry]}))
    write(issue / "trace.md", "---\nstatus: in_sprint\n---\n")
    write(issue / "bug.md", "# Bug")
    write(issue / "acceptance.md", "# Issue acceptance")
    write(tmp_path / "openspec/changes/validation/acceptance.md", "# Change acceptance")
    write(tmp_path / "openspec/changes/validation/tasks.md", "- [ ] task")
    with service.using_governance_root(tmp_path):
        for status in ("in_sprint", "proposed", "in_progress", "applied", "done"):
            row = service._build_issue("bug", entry, changes_override=["validation"], status_override=status)
            assert "acceptance.md" in row.documents
            assert next(doc for doc in row.document_entries if doc.name == "acceptance.md").url == (
                f"/api/v1/requirement-center/issues/{issue.name}/documents/acceptance.md"
            )
            assert service.read_requirement_center_document(issue.name, "acceptance.md")[0] == "# Issue acceptance"


def test_acceptance_readiness_is_separate_from_task_progress(tmp_path):
    issue = tmp_path / "issues/bugs/review/BUG-0099-validation"
    entry = dict(id=issue.name, path=str(issue.relative_to(tmp_path)), status="in_sprint", related_change="validation", severity="medium")
    write(tmp_path / "issues/bugs/_registry.yaml", yaml.safe_dump({"entries": [entry]}))
    write(issue / "trace.md", "---\nstatus: in_sprint\n---\n")
    write(issue / "acceptance.md", "---\nacceptance_status: pending\n---\n- [ ] AC-051：真实复验\n- [ ] AC-052：补齐证据\n")
    write(tmp_path / "openspec/changes/validation/trace.md", "---\nstatus: applied\n---\n")
    write(tmp_path / "openspec/changes/validation/tasks.md", "## 实施任务\n- [x] 完成\n## 回归验证\n- [x] 通过\n")
    with service.using_governance_root(tmp_path):
        row = service._build_issue("bug", entry)
        assert row.stage == "acceptance"
        assert row.task_progress == (1, 1) and row.test_progress == (1, 1)
        assert row.acceptance_pending_count == 2
        assert row.manual_acceptance_progress == (0, 2)
        assert "2 项待验证" in (row.action.disabled_reason or "")
        write(issue / "acceptance.md", "---\nacceptance_status: accepted\n---\n- [x] AC-051：真实复验\n- [ ] AC-052：补齐证据\n")
        partly_checked = service._build_issue("bug", entry)
        assert partly_checked.acceptance_pending_count == 1
        assert partly_checked.manual_acceptance_progress == (1, 2)
        assert "1 项待验证" in (partly_checked.action.disabled_reason or "")
        write(issue / "acceptance.md", "---\nacceptance_status: pending\n---\n- [x] AC-051：真实复验\n- [x] AC-052：补齐证据\n")
        unsigned = service._build_issue("bug", entry)
        assert unsigned.acceptance_pending_count == 0
        assert unsigned.manual_acceptance_progress == (2, 2)
        assert "验收结论待核实" in (unsigned.action.disabled_reason or "")
        write(issue / "acceptance.md", "---\nacceptance_status: accepted\n---\n- [x] AC-051：真实复验\n- [x] AC-052：补齐证据\n")
        accepted = service._build_issue("bug", entry)
        assert accepted.acceptance_pending_count == 0
        assert accepted.manual_acceptance_progress == (2, 2)
        assert accepted.acceptance_blocked_reason is None


def test_ready_dev_uses_linked_change_documents_for_action_gate(tmp_path):
    issue = tmp_path / "issues/bugs/review/BUG-0099-validation"
    entry = dict(id=issue.name, path=str(issue.relative_to(tmp_path)), status="in_sprint", related_change="validation", severity="medium")
    write(tmp_path / "issues/bugs/_registry.yaml", yaml.safe_dump({"entries": [entry]}))
    write(issue / "trace.md", "---\nstatus: in_sprint\n---\n")
    write(issue / "bug.md", "# 缺陷")
    change = tmp_path / "openspec/changes/validation"
    for name in ("proposal.md", "design.md", "tasks.md"):
        write(change / name, f"# {name}")
    write(change / "specs/example/spec.md", "# 规格")
    with service.using_governance_root(tmp_path):
        row = service._build_issue("bug", entry, changes_override=["validation"], status_override="in_sprint")
        assert row.blocked is None
        assert row.action.command == "/opsx-apply BUG-0099-validation"
        assert row.action.disabled_reason is None


def test_change_index_keeps_same_named_issue_and_change_documents(tmp_path):
    from app.governance.change_index import ChangeIndex

    oid = "BUG-0099-validation"
    issue = tmp_path / "issues/bugs/review" / oid
    entry = {"id": oid, "path": str(issue.relative_to(tmp_path)), "status": "in_sprint", "severity": "medium"}
    write(tmp_path / "issues/bugs/_registry.yaml", yaml.safe_dump({"entries": [entry]}))
    write(tmp_path / "issues/requirements/_registry.yaml", yaml.safe_dump({"entries": []}))
    write(issue / "trace.md", f"---\nstatus: in_sprint\nrelated_change: validation\n---\n")
    write(issue / "bug.md", "# Issue bug")
    write(issue / "acceptance.md", "# Issue acceptance")
    change = tmp_path / "openspec/changes/validation"
    write(change / "trace.md", f"---\nchange_id: validation\nstatus: proposed\nbug: {oid}\n---\n")
    write(change / "proposal.md", "---\ntitle: 修复验收入口\n---\n# 修复验收入口")
    write(change / "acceptance.md", "# Change acceptance")
    with service.using_governance_root(tmp_path):
        card = next(item for item in ChangeIndex(tmp_path).cards(lambda _: True) if item.id == "BUG-0099")
        issue_doc = next(doc for doc in card.document_entries if doc.name == "acceptance.md")
        change_doc = next(doc for doc in card.related_changes[0].document_entries if doc.name == "acceptance.md")
        assert issue_doc.url == f"/api/v1/requirement-center/issues/{oid}/documents/acceptance.md"
        assert change_doc.url == "/api/v1/requirement-center/changes/validation/documents/acceptance.md"
        assert service.read_requirement_center_change_document("validation", "acceptance.md")[0] == "# Change acceptance"


def test_missing_change_retains_issue_trace_and_archive_resolution_is_exact(tmp_path):
    with service.using_governance_root(tmp_path):
        assert service._issue_status({"status": "in_sprint"}, {"status": "in_progress"}, ["missing"]) == "in_progress"
        write(tmp_path / "openspec/archive/2026-09-11-validate-other/trace.md", "---\nstatus: archived\n---\n")
        assert service._change_status(["validate"]) is None
        with pytest.raises(PermissionError):
            service._change_dir("../../outside")


def test_current_repository_board_matches_registry_terminal_facts():
    root = Path(__file__).resolve().parents[3]
    with service.using_governance_root(root):
        for kind, issue_type in (("requirements", "requirement"), ("bugs", "bug")):
            entries = yaml.safe_load((root / "issues" / kind / "_registry.yaml").read_text())["entries"]
            rows = service._load_issues(issue_type)
            assert len(rows) == len(entries)
            for entry, row in zip(entries, rows):
                if entry.get("status") == "done":
                    assert row.stage == "done", entry["id"]
                    assert row.blocked is None, entry["id"]
                assert (root / entry["path"]).is_dir(), entry["id"]
                assert not row.drift_warnings, entry["id"]


@pytest.mark.parametrize("stage", list(service.STAGES.values()))
@pytest.mark.parametrize("issue_type,prefix", [("requirement", "REQ"), ("bug", "BUG")])
def test_trace_always_targets_issue_in_every_stage(tmp_path, stage, issue_type, prefix):
    oid = f"{prefix}-0099-validation"
    with service.using_governance_root(tmp_path):
        for docs in (["trace.md", "tasks.md"], ["tasks.md"]):
            entries = service._document_entries(oid, docs, stage, issue_type, ["validation"])
            traces = [doc for doc in entries if doc.name == "trace.md"]
            assert len(traces) == 1
            assert traces[0].label == "trace.md"
            assert traces[0].url == f"/api/v1/requirement-center/issues/{oid}/documents/trace.md"
            assert not traces[0].editable


def test_missing_issue_trace_does_not_read_existing_change_trace(tmp_path):
    oid = "REQ-0099-validation"
    write(tmp_path / "issues/requirements/_registry.yaml", yaml.safe_dump({"entries": [{"id": oid, "path": f"issues/requirements/review/{oid}"}]}))
    write(tmp_path / "openspec/changes/validation/trace.md", "# Change-only content")
    with service.using_governance_root(tmp_path):
        assert "trace.md" not in service._display_document_names(tmp_path / f"issues/requirements/review/{oid}", ["validation"], "applied")
        with pytest.raises(FileNotFoundError):
            service.read_requirement_center_document(oid, "trace.md")


@pytest.mark.parametrize('kind,prefix', [('requirements','REQ'),('bugs','BUG')])
@pytest.mark.parametrize('location', ['change','archive'])
def test_sprint_document_uses_associated_sprint_for_card_and_read(tmp_path,kind,prefix,location):
    oid=f'{prefix}-0099-validation'
    issue=tmp_path/f'issues/{kind}/review/{oid}'
    entry=dict(id=oid,path=str(issue.relative_to(tmp_path)),status='in_sprint',iteration='sprint-005')
    if prefix == 'BUG':
        entry['severity'] = 'medium'
    write(tmp_path/f'issues/{kind}/_registry.yaml',yaml.safe_dump({'entries':[entry]}))
    write(issue/'trace.md','---\nstatus: in_sprint\n---\n')
    write(issue/'sprint.md','# Incorrect Issue copy')
    directory=tmp_path/f'iterations/{location}/sprint-005'
    write(directory/'sprint.yaml',yaml.safe_dump({kind:[oid]}))
    write(directory/'sprint.md','# Correct associated Sprint')
    with service.using_governance_root(tmp_path):
        row=service._build_issue('requirement' if prefix=='REQ' else 'bug',entry)
        assert 'sprint.md' in row.documents and row.blocked is None
        doc=next(doc for doc in row.document_entries if doc.name=='sprint.md')
        assert doc.capability.readable and not doc.editable and not doc.capability.ai_mutable
        assert service.read_requirement_center_document(oid,'sprint.md')[0]=='# Correct associated Sprint'
        (directory/'sprint.md').unlink()
        row=service._build_issue('requirement' if prefix=='REQ' else 'bug',entry)
        assert 'sprint.md' not in row.documents and 'sprint.md' in row.blocked
        assert not next(doc for doc in row.document_entries if doc.name=='sprint.md').capability.readable
        with pytest.raises(FileNotFoundError): service.read_requirement_center_document(oid,'sprint.md')


def test_sprint_documents_are_readonly_and_separate_from_issue_and_change(tmp_path):
    oid = 'BUG-0099-validation'
    issue = tmp_path / f'issues/bugs/review/{oid}'
    entry = dict(id=oid, path=str(issue.relative_to(tmp_path)), status='in_sprint', iteration='sprint-005', related_change='validation', severity='medium')
    write(tmp_path / 'issues/bugs/_registry.yaml', yaml.safe_dump({'entries': [entry]}))
    write(tmp_path / 'issues/requirements/_registry.yaml', 'entries: []\n')
    write(issue / 'trace.md', '---\nstatus: in_sprint\n---\n')
    write(issue / 'bug.md', '# Issue Bug')
    write(tmp_path / 'openspec/changes/validation/trace.md', '---\nstatus: applied\niteration: sprint-005\n---\n')
    write(tmp_path / 'openspec/changes/validation/tasks.md', '- [x] done')
    sprint = tmp_path / 'iterations/change/sprint-005'
    write(sprint / 'sprint.yaml', yaml.safe_dump({'bugs': [oid], 'changes': ['validation']}))
    for name in service.SPRINT_DOCUMENT_NAMES:
        write(sprint / name, f'# Sprint {name}')
    with service.using_governance_root(tmp_path):
        row = service._build_issue('bug', entry)
        for name in service.SPRINT_DOCUMENT_NAMES:
            assert name in row.documents
            document = next(doc for doc in row.document_entries if doc.name == name)
            assert document.capability.readable and not document.editable and not document.capability.ai_mutable
            assert service.read_requirement_center_document(oid, name)[0] == f'# Sprint {name}'
            assert service.read_requirement_center_change_document('validation', name)[0] == f'# Sprint {name}'
        (sprint / 'release-note.md').unlink()
        assert 'release-note.md' not in service._build_issue('bug', entry).documents
        with pytest.raises(FileNotFoundError):
            service.read_requirement_center_document(oid, 'release-note.md')


def test_sprint_resolution_never_falls_back_to_old_or_unrelated_documents(tmp_path):
    oid='REQ-0099-validation';entry={'id':oid,'iteration':'sprint-005'}
    active=tmp_path/'iterations/change/sprint-005'
    old=tmp_path/'iterations/archive/sprint-005'
    for directory in (active,old): write(directory/'sprint.yaml',yaml.safe_dump({'requirements':[oid]}))
    write(old/'sprint.md','# Old copy')
    with service.using_governance_root(tmp_path):
        assert service._sprint_document(entry,{}) is None
        write(active/'sprint.md','# Current')
        assert service._sprint_document(entry,{}).read_text()=='# Current'
        write(active/'sprint.yaml','requirements: []')
        assert service._sprint_document(entry,{}) is None
        assert service._sprint_document({'id':oid,'iteration':'../../outside'},{}) is None
        assert service._sprint_document({'id':oid},{}) is None


def test_sprint_document_does_not_allow_symlink_escape(tmp_path):
    directory=tmp_path/'iterations/change/sprint-005';oid='REQ-0099-validation'
    write(directory/'sprint.yaml',yaml.safe_dump({'requirements':[oid]}))
    write(tmp_path/'outside.md','not sprint')
    (directory/'sprint.md').symlink_to(tmp_path/'outside.md')
    with service.using_governance_root(tmp_path):
        assert service._sprint_document({'id':oid,'iteration':'sprint-005'},{}) is None


@pytest.mark.parametrize('status',list(service.STAGES))
@pytest.mark.parametrize('kind,prefix,main',[('requirements','REQ','requirement.md'),('bugs','BUG','bug.md')])
def test_main_document_remains_first_and_issue_owned(tmp_path,status,kind,prefix,main):
    oid=f'{prefix}-0099-validation';issue=tmp_path/f'issues/{kind}/review/{oid}'
    entry=dict(id=oid,path=str(issue.relative_to(tmp_path)),status=status,related_change='validation')
    write(tmp_path/f'issues/{kind}/_registry.yaml',yaml.safe_dump({'entries':[entry]}))
    write(issue/'trace.md',f'---\nstatus: {status}\n---\n')
    write(tmp_path/'openspec/changes/validation/tasks.md','- [ ] task')
    write(tmp_path/f'openspec/changes/validation/{main}','# Wrong Change copy')
    with service.using_governance_root(tmp_path):
        row=service._build_issue('requirement' if prefix=='REQ' else 'bug',entry)
        assert main not in row.documents
        write(issue/main,'# Issue main document')
        row=service._build_issue('requirement' if prefix=='REQ' else 'bug',entry)
        assert row.documents[0]==main
        doc=row.document_entries[0]
        assert doc.url==f'/api/v1/requirement-center/issues/{oid}/documents/{main}'
        assert doc.capability==service.compute_document_capability(issue_type=row.type,stage=row.stage,document_name=main,path_category='issue',exists=True)
        assert service.read_requirement_center_document(oid,main)[0]=='# Issue main document'
        (issue/main).unlink()
        with pytest.raises(FileNotFoundError):service.read_requirement_center_document(oid,main)


@pytest.mark.parametrize("value,expected", [
    ("2026-09-12 07:03:59", "26/09/12 07:03"),
    ("2024-02-29T00:01:00+08:00", "24/02/29 00:01"),
    ("2026-12-31T23:59:00Z", "26/12/31 23:59"),
    (None, "更新时间未知"), ("", "更新时间未知"),
    ("2026-02-29 12:00:00", "更新时间未知"),
    ("2026-09-12", "更新时间未知"), ("17:30", "更新时间未知"),
    ("bad-date-value-long", "更新时间未知"),
])
def test_card_updated_date(value, expected):
    assert service._updated_at(value) == expected


def test_card_updated_datetime():
    from datetime import datetime
    assert service._updated_at(datetime(2026, 1, 2, 3, 4)) == "26/01/02 03:04"


def test_issue_card_classification_uses_priority_for_req_and_severity_for_bug(tmp_path):
    req = tmp_path / "issues/requirements/review/REQ-0099-validation"
    bug = tmp_path / "issues/bugs/review/BUG-0099-validation"
    write(req / "trace.md", "---\nstatus: in_sprint\npriority: P0\n---\n")
    write(bug / "trace.md", "---\nstatus: in_sprint\nseverity: medium\n---\n")
    with service.using_governance_root(tmp_path):
        req_row = service._build_issue("requirement", {"id": req.name, "path": str(req.relative_to(tmp_path)), "priority": "P0"})
        bug_row = service._build_issue("bug", {"id": bug.name, "path": str(bug.relative_to(tmp_path)), "severity": "medium"})
        assert req_row.priority == "P0" and req_row.severity == ""
        assert bug_row.priority == "" and bug_row.severity == "medium"
        assert not bug_row.drift_warnings


@pytest.mark.parametrize("entry,expected", [
    ({"id": "BUG-0099-validation"}, "缺少 severity"),
    ({"id": "BUG-0099-validation", "severity": "P2"}, "非法 severity: p2"),
])
def test_bug_card_classification_does_not_default_to_priority(tmp_path, entry, expected):
    bug = tmp_path / "issues/bugs/review/BUG-0099-validation"
    write(bug / "trace.md", "---\nstatus: in_sprint\n---\n")
    with service.using_governance_root(tmp_path):
        row = service._build_issue("bug", {**entry, "path": str(bug.relative_to(tmp_path))})
        assert row.priority == ""
        assert row.severity == ""
        assert any(expected in warning for warning in row.drift_warnings)


@pytest.mark.parametrize("stage", ["plan", "review", "archive"])
def test_nested_prototype_discovery_and_read(tmp_path, monkeypatch, stage):
    folder=tmp_path / f'issues/requirements/{stage}/REQ-0999-prototype'
    write(folder/'prototype/web/prototype.html', '<h1>web</h1>')
    write(folder/'prototype/admin/prototype.html', '<h1>admin</h1>')
    write(tmp_path/'outside.html', 'outside')
    (folder/'prototype/escape.html').symlink_to(tmp_path/'outside.html')
    assert service._prototype_documents(folder)==['prototype/admin/prototype.html','prototype/web/prototype.html']
    monkeypatch.setattr(service, '_find_issue_dir', lambda _: folder)
    assert service.read_requirement_center_document('REQ-0999-prototype','prototype/web/prototype.html') == ('<h1>web</h1>', '.html')
    for name in ['prototype/escape.html','prototype/../../outside.html','prototype/missing.html']:
        with pytest.raises(FileNotFoundError): service.read_requirement_center_document('REQ-0999-prototype',name)
