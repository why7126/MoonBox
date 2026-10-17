from pathlib import Path

from scripts.workflow_sync.collect import IssueRecord, SprintRecord
from scripts.workflow_sync.derive import DerivedChange, derive_issue


def _change(change_id: str, state: str) -> DerivedChange:
    return DerivedChange(change_id, state, state, state, 1, 1, "REQ-9114", None, None)


def test_multi_change_issue_stays_in_sprint_until_all_archived():
    first = "add-first"
    second = "add-second"
    issue = IssueRecord(
        issue_id="REQ-9114",
        kind="req",
        path=Path("issues/requirements/review/REQ-9114"),
        trace_status="in_sprint",
        openspec_changes=[{"change_id": first}, {"change_id": second}],
        related_change=first,
    )
    sprint = SprintRecord("sprint-010", Path("iterations/change/sprint-010"), "planning", requirements=[issue.issue_id])
    changes = {first: _change(first, "archived"), second: _change(second, "applied")}

    partial = derive_issue(issue, changes, sprint)
    assert partial.display_status == "in_sprint"
    assert partial.linked_change == second

    changes[second] = _change(second, "archived")
    complete = derive_issue(issue, changes, sprint)
    assert complete.display_status == "done"
