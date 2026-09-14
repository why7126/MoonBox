from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.workflow_sync.collect import ChangeRecord, TaskProgress, parse_frontmatter_yaml
from scripts.workflow_sync.execution import atomic_write, transition
from scripts.workflow_sync.derive import derive_change_state
from app.governance.lifecycle import change_state, aggregate_states, execution_metadata


@pytest.fixture
def change(tmp_path):
    folder = tmp_path / "openspec/changes/fix-example"
    folder.mkdir(parents=True)
    path = folder / "trace.md"
    path.write_text("---\nstatus: proposed\ncreated_at: 2026-09-12 00:00:00\nupdated_at: 2026-09-12 00:00:00\n---\n\n## Notes\nKeep this.\n")
    return tmp_path, path, ChangeRecord("fix-example", "active", tasks=TaskProgress(0, 2))


def test_zero_start_progress_complete_and_replay(change):
    root, path, record = change
    initial = path.read_text()
    preview = transition(root, record, "opsx.start", write=False)
    assert path.read_text() == initial
    assert change_state(preview, 0, 2) == "in_progress"
    record.trace = transition(root, record, "opsx.start", write=True)
    started = path.read_text()
    transition(root, record, "opsx.start", write=True)
    assert path.read_text() == started
    record.trace = transition(root, record, "opsx.progress", write=True)
    assert derive_change_state(record).state == "in_progress"
    with pytest.raises(ValueError, match="all tasks"):
        transition(root, record, "opsx.apply", write=True)
    record.tasks.done = 2
    record.trace = transition(root, record, "opsx.progress", write=True)
    assert derive_change_state(record).state == "in_progress"
    record.trace = transition(root, record, "opsx.apply", write=True)
    assert derive_change_state(record).state == "applied"
    completed = path.read_text()
    transition(root, record, "opsx.start", write=True)
    assert path.read_text() == completed
    assert "Keep this." in completed
    assert completed.count("execution:") == 1


def test_progress_without_start_and_unsupported_schema_fail_closed(change):
    root, path, record = change
    with pytest.raises(ValueError, match="opsx.start"):
        transition(root, record, "opsx.progress", write=True)
    with pytest.raises(ValueError, match="schema"):
        change_state({"execution": {"schema_version": 9}}, 1, 2)


@pytest.mark.parametrize("trace,done,total,expected", [
    ({}, 0, 2, "proposed"), ({}, 1, 2, "in_progress"),
    ({}, 2, 2, "applied"), ({"status": "in_progress"}, 0, 2, "in_progress"),
    ({"status": "applied"}, 0, 2, "applied"), ({"status": "archived"}, 0, 2, "archived"),
])
def test_legacy_state_compatibility(trace, done, total, expected):
    record = ChangeRecord("fix-example", "active", tasks=TaskProgress(done, total), trace=trace)
    assert derive_change_state(record).state == change_state(trace, done, total) == expected


def test_multiple_changes_do_not_accept_unstarted_work():
    assert aggregate_states(["applied", "proposed"]) == "proposed"
    assert aggregate_states(["archived", "in_progress"]) == "in_progress"


def test_atomic_conflict_and_interrupted_replace_recovery(change, monkeypatch):
    root, path, record = change
    original = path.read_text()
    path.write_text(original + "external\n")
    with pytest.raises(ValueError, match="Concurrent"):
        atomic_write(path, "overwrite", original)
    assert path.read_text().endswith("external\n")
    import scripts.workflow_sync.execution as execution
    replace = execution.os.replace
    monkeypatch.setattr(execution.os, "replace", lambda *args: (_ for _ in ()).throw(OSError("interrupted")))
    with pytest.raises(OSError, match="interrupted"):
        transition(root, record, "opsx.start", write=True)
    assert "execution:" not in path.read_text()
    assert not list(path.parent.glob(".workflow-*"))
    monkeypatch.setattr(execution.os, "replace", replace)
    transition(root, record, "opsx.start", write=True)
    assert execution_metadata(path.read_text())["execution"]["started_at"]


def test_symlink_write_rejected(change):
    root, path, record = change
    other = root / "other.md"
    path.rename(other)
    path.symlink_to(other)
    with pytest.raises(ValueError):
        transition(root, record, "opsx.start", write=True)


def test_start_missing_sprint_does_not_write(change, monkeypatch):
    import scripts.workflow_sync.engine as engine
    root, path, record = change
    monkeypatch.setattr(engine, "ROOT", root)
    monkeypatch.setattr(engine, "resolve_sprint_id", lambda *a, **k: (None, "missing"))
    monkeypatch.setattr(engine, "load_all_issues", lambda: {})
    monkeypatch.setattr(engine, "run_openspec_list", lambda: {})
    monkeypatch.setattr(engine, "load_change_record", lambda *a: record)
    report = engine.SyncEngine().run(event="opsx.start", change_id=record.change_id)
    assert report.errors
    assert "execution:" not in path.read_text()


def test_projection_failure_keeps_fact_and_retry_repairs(change, monkeypatch):
    import scripts.workflow_sync.engine as engine
    from scripts.workflow_sync.collect import SprintRecord
    from scripts.workflow_sync.patch import PatchResult
    root,path,record=change
    sprint=SprintRecord('sprint-999',root/'iterations/change/sprint-999','planning',changes=[record.change_id])
    monkeypatch.setattr(engine,'ROOT',root)
    monkeypatch.setattr(engine,'resolve_sprint_id',lambda *a,**k:('sprint-999',None))
    monkeypatch.setattr(engine,'load_all_issues',lambda:{})
    monkeypatch.setattr(engine,'run_openspec_list',lambda:{})
    monkeypatch.setattr(engine,'load_sprint',lambda *a:sprint)
    def reload_record(*args):
        record.trace = {**parse_frontmatter_yaml(path.read_text()), **execution_metadata(path.read_text())}
        return record
    monkeypatch.setattr(engine,'load_change_record',reload_record)
    def fail(*a,**k):raise OSError('projection interrupted')
    monkeypatch.setattr(engine,'patch_sprint_md',fail)
    result=engine.SyncEngine().run(event='opsx.start',change_id=record.change_id)
    assert result.errors and 'projection interrupted' in result.errors[0]
    started=path.read_text()
    for name in ['patch_sprint_md','patch_release_note','patch_acceptance_report']:
        monkeypatch.setattr(engine,name,lambda *a,**k:PatchResult('projection',True))
    result=engine.SyncEngine().run(event='opsx.start',change_id=record.change_id)
    assert not result.errors and len(result.updated)==3
    assert path.read_text()==started
