"""Trusted combined-revision validator port; never accepts client-provided pass reports."""
from typing import Protocol


class CandidateValidator(Protocol):
    def capability(self) -> dict: ...
    def validate(self, *, candidate_id: str, candidate_commit: str, workspace, change_id: str) -> dict: ...


class UnavailableCandidateValidator:
    def capability(self):
        # Existing verification.tasks validates a configured URL, not an immutable
        # combined revision with its own DB. It cannot attest a merge candidate.
        return {'available': False, 'reason_code': 'isolated_candidate_validation_unavailable',
            'dependency': 'REQ-0048-chat-isolated-acceptance-orchestration'}

    def validate(self, **kwargs):
        return {'status': 'blocked', **self.capability()}


def provider() -> CandidateValidator:
    from app.verification.candidate import CandidateSupplier
    return CandidateSupplier()
