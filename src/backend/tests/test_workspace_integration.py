"""Synthetic authority/validator; all repository operations and DB journals are real."""
import json
from types import SimpleNamespace
import pytest
from sqlalchemy import insert, select, update
from app.moonbox_core import service, workspaces, integration
from app.moonbox_core.schema import assignments
from app.moonbox_core.integration_schema import candidates, operations
from app.moonbox_exec_server import validation
from app.moonbox_worktree import WorktreeConflict
from app.chat.service import ChatError
from test_chat import chat
from test_managed_worktree_git import repo, git


@pytest.fixture
def delivery_repo(chat, repo, monkeypatch):
    _, factory = chat
    source, managed = repo
    state_root = managed / 'governance-state'
    state_root.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(state_root))
    (source.root/'issues/requirements').mkdir(parents=True)
    (source.root/'issues/requirements/_registry.yaml').write_text('entries:\n- id: REQ-0042-example\n  status: in_progress\n')
    (source.root/'iterations/change/sprint-015').mkdir(parents=True)
    (source.root/'iterations/change/sprint-015/sprint.md').write_text('# Synthetic Sprint\n')
    git(source.root, 'add', '.')
    git(source.root, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '--amend', '--no-edit', '-q')
    with factory.begin() as db:
        main = workspaces.register_main(db, 'space', 'repo', source.root)
        child = workspaces.reserve_development(db, main, 'REQ-0042-example', managed)
    with factory.begin() as db:
        child = workspaces.materialize(db, main, child)
        db.execute(insert(assignments).values(workspace_id=child['id'], change_id='example-change',
            delivery_root='REQ-0042-example', state='developing'))
    from pathlib import Path
    root = Path(child['root_locator'])
    (root/'src').mkdir(); (root/'src/code.txt').write_text('task result')
    git(root, 'add', '.')
    git(root, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'task result')
    authority = {'allowed': True, 'revision': 'a' * 64}
    project = SimpleNamespace(key='synthetic-project', root=source.root, binding_revision='binding-v1', space_id='space', repository_id='repo')
    context = dict(delivery_root='REQ-0042-example', change_id='example-change', sprint_id='sprint-015')
    def authorize(db, actor, space, repository, change):
        if not authority['allowed']:
            raise ChatError(2601, '无迭代操作权限', 403)
        return project, context
    def scoped(db, actor, space, repository, wid, **kwargs):
        row = workspaces.get(db, space, repository, wid)
        assignment = db.execute(select(assignments).where(assignments.c.workspace_id == wid)).mappings().first()
        return project, row, assignment
    from app.moonbox_core import governance_projection
    monkeypatch.setattr(governance_projection, 'delivery', authorize)
    monkeypatch.setattr(integration, 'delivery', authorize)
    monkeypatch.setattr(service, 'scoped', scoped)
    monkeypatch.setattr(integration, '_governance', lambda *_: authority['revision'])
    monkeypatch.setattr(integration, 'repository_binding', lambda *_: {'workspace_root': str(managed)})
    return factory, source, child, authority


class SyntheticValidator:
    def capability(self):
        return {'available': True}
    def validate(self, **request):
        assert git(request['workspace'], 'rev-parse', 'HEAD') == request['candidate_commit']
        assert (request['workspace']/'src/code.txt').read_text() == 'task result'
        return {'candidate_id': request['candidate_id'], 'candidate_commit': request['candidate_commit'],
            'environment_key': 'synthetic-test-only', 'runtime_digest': 'sha256:'+'b'*64,
            'evidence_digest': 'c'*64, 'status': 'passed'}


def prepared(data, monkeypatch, passed=True):
    factory, _, child, _ = data
    if passed:
        monkeypatch.setattr(validation, 'provider', lambda: SyntheticValidator())
    with factory() as db:
        candidate = integration.prepare(db, 'alice', 'space', 'repo', child['id'], 'candidate-request')
    return integration.validate(factory, 'alice', 'space', 'repo', candidate['id'])


def test_missing_isolated_provider_blocks_confirmation(delivery_repo, monkeypatch):
    candidate = prepared(delivery_repo, monkeypatch, passed=False)
    assert candidate['state'] == 'validation_blocked'
    assert candidate['fingerprint'] is None
    with delivery_repo[0]() as db, pytest.raises(WorktreeConflict, match='validation_required'):
        integration.confirm(db, 'alice', 'space', 'repo', candidate['id'], 'd'*64, 'confirm')


def test_validated_candidate_human_confirmation_preserves_commits_and_replays(delivery_repo, monkeypatch):
    factory, source, child, _ = delivery_repo
    base = source.head()
    candidate = prepared(delivery_repo, monkeypatch)
    assert source.head() == base
    with factory() as db:
        operation = integration.confirm(db, 'alice', 'space', 'repo', candidate['id'], candidate['fingerprint'], 'confirm')
    result = integration.integrate(factory, 'alice', 'space', 'repo', operation['id'])
    assert result['state'] == 'completed'
    assert result['governance_state'] == 'completed'
    assert source.head() == candidate['candidate_commit']
    assert (source.root/'src/code.txt').read_text() == 'task result'
    assert integration.integrate(factory, 'alice', 'space', 'repo', operation['id']) == result
    assert git(source.root, 'show', '-s', '--format=%P', source.head()).split() == [base, candidate['source_commit']]


@pytest.mark.parametrize('change', ['permission', 'governance', 'dirty_main'])
def test_current_permission_and_facts_rechecked_at_confirmation(delivery_repo, monkeypatch, change):
    factory, source, _, authority = delivery_repo
    candidate = prepared(delivery_repo, monkeypatch)
    if change == 'permission': authority['allowed'] = False
    elif change == 'governance': authority['revision'] = 'd'*64
    else: (source.root/'manual.txt').write_text('human edit')
    with factory() as db, pytest.raises((WorktreeConflict, ChatError)):
        integration.confirm(db, 'alice', 'space', 'repo', candidate['id'], candidate['fingerprint'], 'confirm')
    assert source.head() == candidate['target_commit']


def test_git_success_before_db_projection_is_reconciled_once(delivery_repo, monkeypatch):
    factory, source, _, _ = delivery_repo
    candidate = prepared(delivery_repo, monkeypatch)
    with factory() as db:
        operation = integration.confirm(db, 'alice', 'space', 'repo', candidate['id'], candidate['fingerprint'], 'confirm')
    # Simulate process loss between Git success and DB journal commit.
    source.integrate(candidate['candidate_commit'], source_commit=candidate['source_commit'], target_commit=candidate['target_commit'])
    assert integration.integrate(factory, 'alice', 'space', 'repo', operation['id'])['state'] == 'completed'
    assert git(source.root, 'rev-list', '--count', 'HEAD') == '3'


def test_revoked_actor_cannot_write_but_worker_can_record_proven_git_success(delivery_repo, monkeypatch):
    factory, source, child, authority = delivery_repo
    candidate = prepared(delivery_repo, monkeypatch)
    with factory.begin() as db:
        operation = integration.confirm(db, 'alice', 'space', 'repo', candidate['id'], candidate['fingerprint'], 'confirm')
    with factory.begin() as db:
        main_id = db.scalar(select(candidates.c.main_workspace_id).where(candidates.c.id == candidate['id']))
        workspaces.acquire(db, main_id, operation['id'], 1)
        workspaces.acquire(db, child['id'], operation['id'], 1)
        db.execute(update(operations).where(operations.c.id == operation['id']).values(state='applying'))
    authority['allowed'] = False
    assert not integration.reconcile_applied(factory, operation['id'])
    assert source.head() == candidate['target_commit']
    source.integrate(candidate['candidate_commit'], source_commit=candidate['source_commit'], target_commit=candidate['target_commit'])
    assert integration.reconcile_applied(factory, operation['id'])
    assert not integration.reconcile_applied(factory, operation['id'])
    assert git(source.root, 'rev-list', '--count', 'HEAD') == '3'


def test_nested_credentials_rejected_in_candidate(delivery_repo):
    factory, source, child, _ = delivery_repo
    from pathlib import Path
    path = Path(child['root_locator'])
    (path/'src/.env.secret').write_text('synthetic fixture')
    git(path, 'add', '.')
    git(path, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'forbidden fixture')
    with factory() as db, pytest.raises(WorktreeConflict, match='shared_governance'):
        integration.prepare(db, 'alice', 'space', 'repo', child['id'], 'forbidden')
    assert not (source.root/'src/.env.secret').exists()


def test_telemetry_failure_does_not_replace_durable_business_result(delivery_repo, monkeypatch):
    from sqlalchemy import event
    factory, source, _, _ = delivery_repo
    with factory() as db:
        engine = db.get_bind()
    def break_trace(_connection, _cursor, statement, *_):
        if 'task_traces' in statement or 'task_trace_spans' in statement:
            raise RuntimeError('synthetic telemetry outage')
    event.listen(engine, 'before_cursor_execute', break_trace)
    try:
        candidate = prepared(delivery_repo, monkeypatch)
        with factory() as db:
            operation = integration.confirm(db, 'alice', 'space', 'repo', candidate['id'], candidate['fingerprint'], 'confirm')
        assert integration.integrate(factory, 'alice', 'space', 'repo', operation['id'])['state'] == 'completed'
        assert source.head() == candidate['candidate_commit']
    finally:
        event.remove(engine, 'before_cursor_execute', break_trace)


def test_business_confirmation_write_failure_prevents_git_effect(delivery_repo, monkeypatch):
    from sqlalchemy import event
    factory, source, _, _ = delivery_repo
    candidate = prepared(delivery_repo, monkeypatch)
    with factory() as db:
        engine = db.get_bind()
    def break_business(_connection, _cursor, statement, *_):
        if statement.lstrip().upper().startswith('INSERT INTO MOONBOX_MERGE_OPERATIONS'):
            raise RuntimeError('synthetic audit outage')
    event.listen(engine, 'before_cursor_execute', break_business)
    try:
        with factory() as db, pytest.raises(RuntimeError, match='audit outage'):
            integration.confirm(db, 'alice', 'space', 'repo', candidate['id'], candidate['fingerprint'], 'confirm')
        assert source.head() == candidate['target_commit']
        with factory() as db:
            assert db.scalar(select(operations.c.id)) is None
    finally:
        event.remove(engine, 'before_cursor_execute', break_business)


def test_board_overlay_keeps_scope_and_does_not_advance_formal_governance(delivery_repo,monkeypatch):
    from app.moonbox_core.projection import delivery_overlay
    factory,source,child,_=delivery_repo
    baseline=source.head()
    with factory() as db:
        overlay=delivery_overlay(db,'space','repo',['example-change','REQ-0042-example'])
        assert overlay['example-change']['integration_state']=='developing'
        assert delivery_overlay(db,'foreign','repo',['example-change'])=={}
        assert delivery_overlay(db,'space','repo',[])=={}
    candidate=prepared(delivery_repo,monkeypatch)
    with factory() as db:
        overlay=delivery_overlay(db,'space','repo',['example-change'])
        assert overlay['example-change']['integration_state']=='validated'
    assert source.head()==baseline


@pytest.mark.parametrize('human_drift', [False, True])
def test_governance_projection_resumes_without_remerging_or_overwriting(delivery_repo, monkeypatch, human_drift):
    from app.moonbox_core import governance_projection as projection
    factory, source, _, _ = delivery_repo
    candidate = prepared(delivery_repo, monkeypatch)
    with factory() as db:
        operation = integration.confirm(db, 'alice', 'space', 'repo', candidate['id'], candidate['fingerprint'], 'confirm')
    original = projection._replace
    def interrupt(root, item):
        if item['path'].endswith('sprint.md'):
            raise OSError('synthetic interruption')
        original(root, item)
    monkeypatch.setattr(projection, '_replace', interrupt)
    result = integration.integrate(factory, 'alice', 'space', 'repo', operation['id'])
    assert result['state'] == 'completed' and result['governance_state'] == 'blocked'
    assert source.head() == candidate['candidate_commit']
    registry = source.root/'issues/requirements/_registry.yaml'
    saved = registry.read_text()
    if human_drift:
        registry.write_text(saved + '# later human edit\n')
    monkeypatch.setattr(projection, '_replace', original)
    result = integration.integrate(factory, 'alice', 'space', 'repo', operation['id'])
    assert source.head() == candidate['candidate_commit']
    assert result['governance_state'] == ('blocked' if human_drift else 'completed')
    assert registry.read_text() == saved + ('# later human edit\n' if human_drift else '')
    if not human_drift:
        assert (source.root/'iterations/change/sprint-015/sprint.md').read_text().count(operation['id']) == 1
        assert integration.integrate(factory, 'alice', 'space', 'repo', operation['id']) == result


def test_source_pass_does_not_attest_combined_candidate(delivery_repo, monkeypatch):
    from pathlib import Path
    factory, source, child, _ = delivery_repo
    # Main adds an incompatible condition in a separate path, so Git can merge cleanly.
    (source.root/'src').mkdir(exist_ok=True)
    (source.root/'src/incompatible.txt').write_text('main-only incompatible condition')
    git(source.root,'add','.'); git(source.root,'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','main condition')
    assert not (Path(child['root_locator'])/'src/incompatible.txt').exists()
    class CombinedValidator(SyntheticValidator):
        def validate(self, **request):
            assert (request['workspace']/'src/incompatible.txt').exists()
            assert (request['workspace']/'src/code.txt').exists()
            return {'status':'failed','reason_code':'candidate_checks_failed'}
    monkeypatch.setattr(validation,'provider',CombinedValidator)
    with factory() as db:
        candidate = integration.prepare(db,'alice','space','repo',child['id'],'combination-failure')
    result = integration.validate(factory,'alice','space','repo',candidate['id'])
    assert result['state'] == 'validation_blocked'
    with factory() as db, pytest.raises(WorktreeConflict,match='validation_required'):
        integration.confirm(db,'alice','space','repo',candidate['id'],'0'*64,'forbidden')
    assert not (source.root/'src/code.txt').exists()


def test_two_confirmed_deliveries_serialize_and_second_requires_revalidation(delivery_repo, monkeypatch):
    from pathlib import Path
    factory, source, first, _ = delivery_repo
    first_candidate = prepared(delivery_repo, monkeypatch)
    with factory() as db:
        first_operation = integration.confirm(db,'alice','space','repo',first_candidate['id'],first_candidate['fingerprint'],'first-confirm')
        main = workspaces.get(db,'space','repo',db.scalar(select(candidates.c.main_workspace_id).where(candidates.c.id==first_candidate['id'])))
        second = workspaces.reserve_development(db,main,'REQ-0055-example',Path(first['root_locator']).parent)
        db.commit()
        second = workspaces.materialize(db,main,second)
        db.execute(insert(assignments).values(workspace_id=second['id'],change_id='parallel-change',delivery_root='REQ-0055-example',state='developing'))
        db.commit()
    second_root = Path(second['root_locator']); (second_root/'src').mkdir()
    (second_root/'src/code.txt').write_text('task result')
    git(second_root,'add','.'); git(second_root,'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','second result')
    original = integration.delivery
    def authorize(db,actor,space,repository,change):
        project,context = original(db,actor,space,repository,change)
        if change == 'parallel-change': context = dict(context,change_id=change,delivery_root='REQ-0055-example')
        return project,context
    monkeypatch.setattr(integration,'delivery',authorize)
    with factory() as db:
        second_candidate = integration.prepare(db,'alice','space','repo',second['id'],'second-prepare')
    second_candidate = integration.validate(factory,'alice','space','repo',second_candidate['id'])
    with factory() as db:
        second_operation = integration.confirm(db,'alice','space','repo',second_candidate['id'],second_candidate['fingerprint'],'second-confirm')
    # Establish deterministic queue order independently of the clock resolution.
    with factory.begin() as db:
        db.execute(update(operations).where(operations.c.id==first_operation['id']).values(created_at='2026-01-01T00:00:00Z'))
        db.execute(update(operations).where(operations.c.id==second_operation['id']).values(created_at='2026-01-02T00:00:00Z'))
    assert integration.integrate(factory,'alice','space','repo',second_operation['id'])['state']=='queued'
    assert source.head()==first_candidate['target_commit']
    assert integration.integrate(factory,'alice','space','repo',first_operation['id'])['state']=='completed'
    with pytest.raises(WorktreeConflict):
        integration.integrate(factory,'alice','space','repo',second_operation['id'])
    assert source.head()==first_candidate['candidate_commit']
