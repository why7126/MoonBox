"""Shared read-only deep close gate, used before any Sprint mutation."""
from pathlib import Path
from app.governance.archive_admission import change_acceptance
from app.governance.archive_recovery import archive_paths, recovery_admission


def change_close_readiness(root: Path, change: str, *, source_root: Path | None = None) -> dict:
    active = root / 'openspec/changes' / change
    folders = ([active] if active.is_dir() else []) + archive_paths(root, change)
    if len(folders) != 1:
        return {'ready': False, 'reason': 'change_identity_ambiguous'}
    if (folders[0] / 'acceptance-plan.json').is_file():
        return change_acceptance(root, change, source_root=source_root)
    # Historical changes without a structured plan keep their existing task/trace
    # gate. This is explicitly not a claim that automated AC evidence exists.
    return {**recovery_admission(root, change, source_root=source_root), 'source': 'legacy-task-trace'}


def close_blockers(root: Path, changes) -> list[str]:
    blockers = []
    for change in sorted(set(changes)):
        result = change_close_readiness(root, change)
        if not result['ready']:
            code = result.get('recovery_reason') or 'acceptance_not_ready'
            blockers.append(f"{change}: {code}: {result.get('reason', '归档核验受阻')}")
    return blockers
