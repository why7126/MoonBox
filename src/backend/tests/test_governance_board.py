"""REQ-0022 acceptance regression: archived facts and validation document sources."""
from pathlib import Path

import pytest
import yaml

from app.services import requirement_center as service


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


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
    write(tmp_path / "openspec/changes/validation/tasks.md", "- [x] complete\n")
    entry = dict(id=issue.name, path=str(issue.relative_to(tmp_path)), status="in_sprint", related_change="validation")
    with service.using_governance_root(tmp_path):
        row = service._build_issue("requirement", entry)
        assert row.stage == "acceptance" and row.blocked is None
        assert row.test_progress == (2, 3)
        (issue / "acceptance.md").unlink()
        assert service._build_issue("requirement", entry).blocked == "缺少 acceptance.md"
        write(issue / "acceptance.md", " ")
        assert "文档内容为空" in service._build_issue("requirement", entry).blocked


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
