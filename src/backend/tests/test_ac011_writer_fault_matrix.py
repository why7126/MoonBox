"""AC-011: durable writer interruptions for each candidate-backed REQ action."""
import pytest

from app.governance import writer
from app.governance.snapshot import stable, digest, read_once
from test_governance_candidates import contents, OID, BASE
from test_governance_review import review_files
from test_governance_writer import writing, queue
from test_requirement_completion_recovery import completed
from test_chat import chat


def scenario(writing, action):
    factory, project, initial_before, initial_after, permit = writing
    if action == 'req-generate':
        before, after = contents()
    elif action == 'req-complete':
        before, after = completed()
    else:
        before, after, _, _ = review_files()
    for path in stable(project.root).files:
        (project.root / path).unlink()
    for path, body in before.items():
        target = project.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
    operation_id = queue((factory, project, before, after, permit),
        key='ac011-' + action, candidate_action=action, object_id=OID, base_path=BASE)
    return factory, project, before, after, operation_id


@pytest.mark.parametrize('action', ['req-generate', 'req-complete', 'req-review'])
@pytest.mark.parametrize('point', ['before-write', 'after-first-file', 'before-sync'])
def test_candidate_action_recovers_exact_file_steps(writing, monkeypatch, action, point):
    factory, project, before, after, operation_id = scenario(writing, action)
    sync_calls = []
    def synced(*_):
        sync_calls.append('sync')
        return {'event': action.replace('-', '.'), 'source_hash': 'controlled-fixture'}
    monkeypatch.setattr(writer, 'run_workflow_sync', synced)
    if point == 'before-write':
        original = writer.replace_file
        def crash_before(*args, **kwargs):
            raise SystemExit('injected before first replace')
        monkeypatch.setattr(writer, 'replace_file', crash_before)
        with factory() as db:
            with pytest.raises(SystemExit): writer.process(db, operation_id)
        assert stable(project.root).files == before
        monkeypatch.setattr(writer, 'replace_file', original)
    elif point == 'after-first-file':
        def crash_after(index, _path):
            if index == 0:
                raise SystemExit('injected after first replace')
        with factory() as db:
            with pytest.raises(SystemExit): writer.process(db, operation_id, after_write=crash_after)
        assert stable(project.root).files not in (before, after)
    else:
        def crash_before_sync(*_):
            raise SystemExit('injected before sync')
        monkeypatch.setattr(writer, 'run_workflow_sync', crash_before_sync)
        with factory() as db:
            with pytest.raises(SystemExit): writer.process(db, operation_id)
        assert stable(project.root).files == after
        monkeypatch.setattr(writer, 'run_workflow_sync', synced)
    with factory() as restarted:
        result = writer.process(restarted, operation_id)
        assert result['state'] == 'applied'
        assert writer.process(restarted, operation_id)['state'] == 'applied'
    assert stable(project.root).files == after
    assert sync_calls == ['sync']


@pytest.mark.parametrize('action', ['req-generate', 'req-complete', 'req-review'])
def test_completed_sync_is_not_replayed_after_restart(writing, monkeypatch, action):
    factory, project, _, after, operation_id = scenario(writing, action)
    sync_calls = []
    def synced(*_):
        sync_calls.append('sync')
        return {'event': action.replace('-', '.'), 'object_id': OID,
                'source_hash': digest(read_once(project.root))}
    monkeypatch.setattr(writer, 'run_workflow_sync', synced)
    original_set_state = writer.set_state
    def crash_before_verified(db, oid, state, phase, error=None):
        if state == 'applied':
            raise SystemExit('injected after sync journal, before verified state')
        return original_set_state(db, oid, state, phase, error)
    monkeypatch.setattr(writer, 'set_state', crash_before_verified)
    with factory() as db:
        with pytest.raises(SystemExit): writer.process(db, operation_id)
    assert stable(project.root).files == after
    monkeypatch.setattr(writer, 'set_state', original_set_state)
    with factory() as restarted:
        assert writer.process(restarted, operation_id)['state'] == 'applied'
    assert sync_calls == ['sync']


@pytest.mark.parametrize('action', ['req-generate', 'req-complete', 'req-review'])
def test_ambiguous_partial_sync_blocks_replay(writing, monkeypatch, action):
    factory, project, _, _, operation_id = scenario(writing, action)
    calls = []
    def partial_sync(*_):
        calls.append('sync')
        index = project.root / 'issues/requirements/CHANGELOG.md'
        index.write_text(index.read_text() + '\npartial sync effect\n')
        raise SystemExit('injected during sync')
    monkeypatch.setattr(writer, 'run_workflow_sync', partial_sync)
    with factory() as db:
        with pytest.raises(SystemExit): writer.process(db, operation_id)
    with factory() as restarted:
        assert writer.process(restarted, operation_id)['state'] == 'recovery_blocked'
    assert calls == ['sync']
    assert 'partial sync effect' in (project.root / 'issues/requirements/CHANGELOG.md').read_text()


@pytest.mark.parametrize('action', ['req-generate', 'req-complete', 'req-review'])
def test_completed_sync_with_derived_files_recovers_without_replay(writing, monkeypatch, action):
    factory, project, _, _, operation_id = scenario(writing, action)
    calls = []
    def synced(*_):
        calls.append('sync')
        target = project.root / 'issues/requirements/CHANGELOG.md'
        target.write_text(target.read_text() + '\nverified derived projection\n')
        return {'event': action.replace('-', '.'), 'object_id': OID,
                'source_hash': digest(read_once(project.root))}
    monkeypatch.setattr(writer, 'run_workflow_sync', synced)
    original_set_state = writer.set_state
    def crash_before_verified(db, oid, state, phase, error=None):
        if state == 'applied': raise SystemExit('after synchronized files, before terminal commit')
        return original_set_state(db, oid, state, phase, error)
    monkeypatch.setattr(writer, 'set_state', crash_before_verified)
    with factory() as db:
        with pytest.raises(SystemExit): writer.process(db, operation_id)
    monkeypatch.setattr(writer, 'set_state', original_set_state)
    with factory() as restarted:
        assert writer.process(restarted, operation_id)['state'] == 'applied'
    assert calls == ['sync']
    assert (project.root / 'issues/requirements/CHANGELOG.md').read_text().count('verified derived projection') == 1
