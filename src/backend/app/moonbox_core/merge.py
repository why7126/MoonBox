"""Merge confirmation contract; authorization and Git integration remain server-owned."""
from dataclasses import dataclass, asdict
import hashlib
import json
import re

from app.moonbox_worktree import WorktreeConflict


@dataclass(frozen=True)
class CandidateInput:
    space_id: str
    repository_id: str
    workspace_id: str
    delivery_root: str
    change_id: str
    sprint_id: str
    source_commit: str
    target_commit: str
    candidate_commit: str
    evidence_digest: str
    runtime_digest: str
    governance_digest: str

    def __post_init__(self):
        for value in (self.source_commit, self.target_commit, self.candidate_commit):
            if not re.fullmatch(r'[0-9a-f]{40}(?:[0-9a-f]{24})?', value):
                raise ValueError('invalid_merge_commit')
        for value in (self.evidence_digest, self.governance_digest):
            if not re.fullmatch(r'[0-9a-f]{64}', value):
                raise ValueError('invalid_merge_digest')
        if not re.fullmatch(r'sha256:[0-9a-f]{64}', self.runtime_digest):
            raise ValueError('immutable_runtime_required')

    def fingerprint(self):
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True,
            separators=(',', ':')).encode()).hexdigest()


def confirmable(recorded, current, *, can_operate_sprint, validation_state,
                evidence_candidate, main_clean, source_clean):
    """Always called with fresh authority; a saved approval never grants a capability."""
    if not can_operate_sprint:
        raise WorktreeConflict('sprint_operation_forbidden')
    if recorded.fingerprint() != current.fingerprint():
        raise WorktreeConflict('merge_candidate_stale')
    if not main_clean or not source_clean:
        raise WorktreeConflict('workspace_has_changes')
    if validation_state != 'passed' or evidence_candidate != current.candidate_commit:
        raise WorktreeConflict('candidate_validation_required')
    return recorded.fingerprint()


def reconcile_stage(*, source_commit, target_before, candidate_commit, actual_target,
                    operation_state):
    """Reconcile Git truth after a crash without issuing a second merge."""
    if actual_target == candidate_commit:
        return 'git_integrated'
    if operation_state in ('git_integrated', 'completed'):
        return 'target_diverged'
    if actual_target == target_before:
        return 'pending_integration'
    return 'target_diverged'
