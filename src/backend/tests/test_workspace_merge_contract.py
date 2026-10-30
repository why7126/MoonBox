from dataclasses import replace
import pytest
from app.moonbox_core.merge import CandidateInput, confirmable, reconcile_stage
from app.moonbox_worktree import WorktreeConflict


def candidate():
    return CandidateInput('space', 'repo', 'workspace', 'REQ-0042', 'change', 'sprint-015',
        'a'*40, 'b'*40, 'c'*40, 'd'*64, 'sha256:'+'e'*64, 'f'*64)


def check(recorded, current, **overrides):
    options = dict(can_operate_sprint=True, validation_state='passed',
        evidence_candidate=current.candidate_commit, main_clean=True, source_clean=True)
    options.update(overrides)
    return confirmable(recorded, current, **options)


def test_human_confirmation_requires_current_sprint_rights():
    value = candidate()
    assert check(value, value) == value.fingerprint()
    with pytest.raises(WorktreeConflict, match='forbidden'):
        check(value, value, can_operate_sprint=False)


@pytest.mark.parametrize('field,value', [
    ('source_commit', '1'*40), ('target_commit', '2'*40), ('candidate_commit', '3'*40),
    ('evidence_digest', '4'*64), ('governance_digest', '5'*64),
    ('runtime_digest', 'sha256:'+'6'*64), ('sprint_id', 'sprint-016'),
    ('space_id', 'other'), ('workspace_id', 'other'),
])
def test_any_input_change_invalidates_confirmation(field, value):
    old = candidate()
    with pytest.raises(WorktreeConflict, match='stale'):
        check(old, replace(old, **{field: value}))


@pytest.mark.parametrize('overrides', [dict(validation_state='pending'),
    dict(evidence_candidate='a'*40), dict(main_clean=False), dict(source_clean=False)])
def test_source_only_evidence_or_dirty_workspace_cannot_merge(overrides):
    with pytest.raises(WorktreeConflict):
        check(candidate(), candidate(), **overrides)


def test_git_success_database_failure_reconciles_without_duplicate_merge():
    args = dict(source_commit='a'*40, target_before='b'*40, candidate_commit='c'*40,
        operation_state='integrating')
    assert reconcile_stage(**args, actual_target='c'*40) == 'git_integrated'
    assert reconcile_stage(**args, actual_target='b'*40) == 'pending_integration'
    assert reconcile_stage(**args, actual_target='d'*40) == 'target_diverged'
