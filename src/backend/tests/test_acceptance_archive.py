"""Real file publication and HTTP ACL; no product/model acceptance claim."""
import json
from pathlib import Path
import pytest
from sqlalchemy import select,update
from test_chat import chat
from test_acceptance_api import operation
from app.verification.acceptance_state import AcceptanceState,Conflict
from app.verification.acceptance_controller import Controller
from app.verification.acceptance_archive import publish
from app.verification.acceptance_schema import archives,results


def settled(chat,monkeypatch,tmp_path):
    item=operation(chat,monkeypatch,tmp_path);_,factory=chat
    private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private))
    change=tmp_path/'openspec/changes/add-test';change.mkdir(parents=True)
    (change/'trace.md').write_text('---\nstatus: in_progress\n---\n')
    state=AcceptanceState(factory);token=state.claim(item['id'],'worker')
    state.result(token,'AC-001','passed',evidence={'kind':'command','digest':'d'*64,'password':'never-export'})
    state.cleanup(item['id'],released=True)
    Controller(state,None,None).finish_owner(token,'passed')
    return state,state.get(item['id'])


def test_immutable_archive_survives_online_expiry_and_checks_acl(chat,monkeypatch,tmp_path):
    state,item=settled(chat,monkeypatch,tmp_path);client,factory=chat
    artifact=publish(factory,item['id']);version=state.get(item['id'])['version']
    assert publish(factory,item['id'])==artifact
    assert state.get(item['id'])['version']==version
    path=tmp_path/artifact['path'];raw=path.read_text()
    assert 'never-export' not in raw and str(tmp_path) not in raw and 'alice' not in raw
    with factory.begin() as db:
        db.execute(update(results).where(results.c.attempt_id==item['attempt_id']).values(updated_at='2000-01-01T00:00:00+00:00'))
    url='/api/v1/chat/acceptance-operations/'+item['id']+'/evidence'
    assert client.get(url).status_code==410
    assert client.get(url+'/archive').json()['data']['items'][0]['digest']==artifact['digest']
    from app.main import app
    from app.api.v1.admin_auth import require_session_user
    app.dependency_overrides[require_session_user]=lambda:{'id':'bob'}
    assert client.get(url+'/archive').status_code==404


def test_crash_after_file_write_recovers_without_replacing_history(chat,monkeypatch,tmp_path):
    state,item=settled(chat,monkeypatch,tmp_path);_,factory=chat
    from app.verification import acceptance_archive as module
    original=module.replace_file
    def lost_ack(*args,**kwargs):
        original(*args,**kwargs)
        raise OSError('synthetic interrupted publication')
    monkeypatch.setattr(module,'replace_file',lost_ack)
    with pytest.raises(OSError):publish(factory,item['id'])
    with factory() as db:assert db.scalar(select(archives.c.state))=='pending'
    monkeypatch.setattr(module,'replace_file',original)
    artifact=publish(factory,item['id'])
    path=tmp_path/artifact['path'];path.write_text('{}')
    with pytest.raises(Conflict,match='archive_integrity_failed'):publish(factory,item['id'])
    assert path.read_text()=='{}'


def test_cancel_or_symlink_prevents_publication(chat,monkeypatch,tmp_path):
    state,item=settled(chat,monkeypatch,tmp_path);_,factory=chat
    target=tmp_path/'outside';target.mkdir()
    (tmp_path/'openspec/changes/add-test/evidence').symlink_to(target,target_is_directory=True)
    from app.chat.service import ChatError
    with pytest.raises((ChatError,OSError)):publish(factory,item['id'])
    assert list(target.iterdir())==[]
    current=state.get(item['id']);state.cancel(item['id'],current['version'])
    with pytest.raises(Conflict,match='cancelled'):publish(factory,item['id'])


def test_long_term_reference_follows_unique_archived_change(chat,monkeypatch,tmp_path):
    state,item=settled(chat,monkeypatch,tmp_path);client,factory=chat
    artifact=publish(factory,item['id'])
    destination=tmp_path/'openspec/archive/2026-10-29-add-test'
    destination.parent.mkdir()
    (tmp_path/'openspec/changes/add-test').rename(destination)
    response=client.get('/api/v1/chat/acceptance-operations/'+item['id']+'/evidence/archive')
    assert response.status_code==200
    record=response.json()['data']['items'][0]
    assert record['digest']==artifact['digest']
    assert record['path'].startswith('openspec/archive/2026-10-29-add-test/')
