"""Fast navigation is read admission; execution still uses current facts."""
import pytest
from sqlalchemy import select, func
from app.chat import service
from app.chat.schema import governance_candidates, turns
from app.chat.workspace import git
from app.governance import preparation, execution_context
from test_chat import chat
from test_governance_scope import bind
from test_governance_candidates import contents, OID


@pytest.fixture
def scene(chat, tmp_path, monkeypatch):
    root = tmp_path / 'repo'; root.mkdir()
    private = tmp_path / 'private'; private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(private)); bind(monkeypatch, root)
    captured, draft = contents()
    def write(files):
        for name, body in files.items():
            path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(body)
    write(captured)
    git(root, 'init'); git(root, 'add', '.')
    git(root, '-c', 'user.name=Test', '-c', 'user.email=test@invalid', 'commit', '-m', 'fixture')
    return chat[1], write, draft


def test_open_does_not_prepare_write_or_reconcile(scene, monkeypatch):
    factory, _, _ = scene
    def forbidden(*args, **kwargs):
        pytest.fail('write preparation must wait for Send')
    monkeypatch.setattr(preparation, '_object_session_snapshot', forbidden)
    monkeypatch.setattr(execution_context, 'reconcile', forbidden)
    with factory() as db:
        first = preparation.prepare_object_session(db, 'alice', 'space', 'repo', OID, 'open-chat', idempotency_key='open')
        second = preparation.prepare_object_session(db, 'alice', 'space', 'repo', OID, 'open-chat', idempotency_key='open-again')
        assert first['conversation_id'] == second['conversation_id']
        assert db.scalar(select(func.count()).select_from(governance_candidates)) == 0
        assert db.scalar(select(func.count()).select_from(turns)) == 0
        with pytest.raises(service.ChatError):
            preparation.prepare_object_session(db, 'bob', 'space', 'repo', OID, 'open-chat')


def test_send_prepares_candidate_for_exact_opened_conversation_once(scene):
    factory, _, _ = scene
    with factory() as db:
        opened = preparation.prepare_object_session(db, 'alice', 'space', 'repo', OID, 'open-chat')
        parent = service.conversation(db, 'alice', opened['conversation_id'])
        for _ in range(2):
            result = preparation.prepare_send(db, 'alice', parent, f'/req-generate {OID}', 'send-once')
            assert result['id'] == parent['id']
        candidate = db.execute(select(governance_candidates)).mappings().one()
        assert candidate['conversation_id'] == parent['id']
        assert candidate['prepared_turn_id'] is None
        assert db.scalar(select(func.count()).select_from(turns)) == 0


def test_stage_change_after_open_is_checked_on_send(scene):
    factory, write, draft = scene
    with factory() as db:
        opened = preparation.prepare_object_session(db, 'alice', 'space', 'repo', OID, 'open-chat')
        parent = service.conversation(db, 'alice', opened['conversation_id'])
        write(draft)
        with pytest.raises(service.ChatError):
            preparation.prepare_send(db, 'alice', parent, f'/req-generate {OID}', 'send-changed')
        assert db.scalar(select(func.count()).select_from(governance_candidates)) == 0


def test_send_retains_project_wide_recovery(scene, monkeypatch):
    factory, _, _ = scene
    calls = []
    original = execution_context.reconcile
    def tracked(*args, **kwargs):
        calls.append(kwargs); return original(*args, **kwargs)
    monkeypatch.setattr(execution_context, 'reconcile', tracked)
    with factory() as db:
        opened = preparation.prepare_object_session(db, 'alice', 'space', 'repo', OID, 'open-chat')
        assert not calls
        preparation.prepare_send(db, 'alice', service.conversation(db, 'alice', opened['conversation_id']), f'/req-generate {OID}', 'send')
        assert calls and all('operation_id' not in call for call in calls)
