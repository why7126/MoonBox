"""Default source-workspace recovery windows for candidate-backed actions."""
import json

import pytest
from sqlalchemy import func, insert, select

from app.chat import service
from app.chat.schema import (conversations, governance_applications, governance_candidates,
    turns)
from app.chat.workspace import git, snapshot
from app.governance import scope, store, writer
from app.governance.candidate_recovery import reconcile_terminal_candidates
from app.governance.preparation import prepare_object_session
from app.governance.snapshot import stable
from test_chat import chat
from test_governance_candidates import BASE, OID, contents
from test_governance_review import review_files
from test_requirement_completion_recovery import completed


def facts(action):
    if action == 'req-generate':
        return (*contents(), OID, BASE)
    if action == 'req-complete':
        return (*completed(), OID, BASE)
    return review_files()


def write_delta(root, before, after, names):
    for name in names:
        path = root / name
        if name in after:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(after[name])
        else:
            path.unlink(missing_ok=True)


@pytest.mark.parametrize('action', ['req-generate', 'req-complete', 'req-review'])
@pytest.mark.parametrize('point', ['before-write', 'first-file', 'before-sync',
    'partial-sync', 'after-sync', 'unknown-external-edit'])
def test_source_action_restart_classifies_persisted_steps(
    chat, tmp_path, monkeypatch, action, point,
):
    _, factory = chat
    source = tmp_path / 'source'; source.mkdir()
    private = tmp_path / 'private'; private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(private))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS', json.dumps([{
        'id': 'repo', 'space_id': 'space', 'governance_root': str(source),
        'source_root': str(source), 'workspace_mode': 'source',
    }]))
    before, after, oid, base = facts(action)
    for name, body in before.items():
        path = source / name; path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    sync_script = source / 'scripts/sync-workflow-status.py'
    sync_script.parent.mkdir(parents=True, exist_ok=True)
    sync_script.write_text('import sys\nsys.exit(0)\n')
    git(source, 'init'); git(source, 'add', '.')
    git(source, '-c', 'user.name=Test', '-c', 'user.email=test@invalid',
        'commit', '-m', 'source baseline')
    with factory() as db:
        prepared = prepare_object_session(db, 'alice', 'space', 'repo', oid, action=action)
        parent = service.conversation(db, 'alice', prepared['conversation_id'])
        project = scope.authorize(db, 'alice', 'space', 'repo', write=True)
        turn = service.identity()
        terminal = 'completed' if point in ('after-sync', 'partial-sync') else 'stopped'
        db.execute(insert(turns).values(**turn, conversation_id=parent['id'],
            client_request_id=f'ac011-{action}-{point}', prompt=f'/{action} {oid}',
            status=terminal, executor_turn_id='observed-executor'))
        candidate = service.identity()
        db.execute(insert(governance_candidates).values(**candidate, actor_id='alice',
            space_id='space', repository_id='repo', scope_key=project.key,
            conversation_id=parent['id'], object_id=oid, action=action,
            binding_revision=project.binding_revision, baseline_hash=stable(source).revision,
            state='running', revision=1, prepared_turn_id=turn['id']))
        manifest = {name: {key: value for key, value in item.items()
            if key in ('kind', 'sha256', 'executable')}
            for name, item in snapshot(source)['files'].items()}
        store.write(candidate['id'], 'baseline', {'workspace_mode': 'source',
            'base_path': base, 'files': {name: body.decode() for name, body in before.items()},
            'workspace_manifest': manifest})
        db.commit()
    changed = sorted(name for name in before.keys() | after.keys()
        if before.get(name) != after.get(name))
    if point == 'first-file':
        write_delta(source, before, after, changed[:1])
    elif point == 'before-sync':
        write_delta(source, before, after, changed[:-2])
    elif point == 'partial-sync':
        write_delta(source, before, after, changed[:-1])
    elif point == 'after-sync':
        write_delta(source, before, after, changed)
    elif point == 'unknown-external-edit':
        write_delta(source, before, after, changed[:1])
        extra = source / 'src/external.py'; extra.parent.mkdir(parents=True, exist_ok=True)
        extra.write_text('# external edit\n')
    reconcile_terminal_candidates(factory, lambda cid: (source, source))
    reconcile_terminal_candidates(factory, lambda cid: (source, source))
    with factory() as db:
        state, error = db.execute(select(governance_candidates.c.state,
            governance_candidates.c.error_code)).one()
        applications = db.scalar(select(func.count())
            .select_from(governance_applications))
    if point == 'after-sync':
        assert (state, error, applications) == ('applied', None, 1)
        assert stable(source).files == after
    elif point == 'unknown-external-edit':
        assert (state, error, applications) == ('rejected', 'source_recovery_blocked', 0)
        assert (source / 'src/external.py').exists()
        with factory() as db:
            project = scope.authorize(db, 'alice', 'space', 'repo')
            with pytest.raises(service.ChatError) as blocked:
                writer.assert_readable(db, project)
            assert blocked.value.status == 503
    else:
        assert (state, applications) == ('rejected', 0)
        assert stable(source).files == before
