"""Actual turn HTTP admission under deterministic concurrent filesystem updates."""
import pytest
from sqlalchemy import select, func
from app.chat.schema import turns
from app.governance import preparation
from test_chat import chat, create
from test_governance_writer import writing
from test_governance_candidates import OID


@pytest.mark.parametrize('mode', ['once', 'continuous', 'invalid', 'mismatch'])
def test_actual_send_snapshot_race(writing, chat, monkeypatch, mode):
    factory, project, *_ = writing
    client, _ = chat
    cid = create(client)
    monkeypatch.setattr('app.chat.isolated.allowed', lambda *a: True)
    monkeypatch.setattr('app.chat.settings.execution_limits', lambda: dict(user_concurrency=2, space_concurrency=2, user_monthly_tokens=10000, space_monthly_tokens=10000, user_storage_bytes=10000000, space_storage_bytes=10000000, turn_reserved_tokens=10, turn_reserved_bytes=1000000))
    original = preparation._preflight_object_session
    calls = []
    def preflight(*args):
        calls.append(1)
        if mode == 'mismatch':
            raise preparation.service.ChatError(2606, 'mismatch', 409,
                kind='workspace_fact_source_stale', details={'reason': 'manifest_mismatch'})
        if mode == 'invalid' and len(calls) > 1:
            raise preparation.service.ChatError(2604, '验收已失效', 409, kind='governance_validation_failed')
        item = original(*args)
        if mode == 'continuous' or len(calls) == 1:
            p = project.root / 'docs/concurrent.md'
            p.parent.mkdir(exist_ok=True)
            p.write_text('concurrent update ' + str(len(calls)))
        return item
    monkeypatch.setattr(preparation, '_preflight_object_session', preflight)
    url = f'/api/v1/chat/conversations/{cid}/turns'
    payload = {'client_request_id': 'race-once', 'prompt': '/req-generate ' + OID}
    response = client.post(url, json=payload)
    if mode == 'once':
        assert response.status_code == 200, response.text
        assert response.json()['data']['status'] == 'queued'
        assert len(calls) == 3  # two baseline checks plus enqueue guard revalidation
        again = client.post(url, json=payload)
        assert again.status_code == 200, again.text
        assert again.json()['data']['id'] == response.json()['data']['id']
        assert len(calls) == 3  # two baseline checks plus enqueue guard revalidation
    else:
        assert response.status_code == 409, response.text
        assert len(calls) == (2 if mode == 'invalid' else 3)
        if mode != 'invalid':
            assert ('manifest_mismatch' if mode == 'mismatch' else 'concurrent_update') in response.text
    if mode != 'once':
        from app.governance import store
        assert not (store.root() / preparation._command_baseline_id(cid, 'race-once')).exists()
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(turns)) == (1 if mode == 'once' else 0)

@pytest.mark.parametrize('versions,accepted', [(['old', 'new', 'new'], True), (['old', 'new', 'old'], False), (['same', 'same'], True)])
def test_source_projection_sampling(versions, accepted, monkeypatch, tmp_path):
    from types import SimpleNamespace
    values = iter(versions)
    monkeypatch.setattr(preparation, 'stable', lambda root: SimpleNamespace(revision=next(values)))
    project = SimpleNamespace(root=tmp_path, source_root=tmp_path / 'source')
    if accepted:
        assert preparation._ensure_executor_snapshot(project).revision == versions[-1]
    else:
        with pytest.raises(preparation.service.ChatError) as error:
            preparation._ensure_executor_snapshot(project)
        assert error.value.details['reason'] == 'manifest_mismatch'
