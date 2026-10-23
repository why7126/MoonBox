import copy
import json
import time
import tomllib

import pytest
import yaml
from sqlalchemy import insert, select, update

from app.chat import service
from app.chat.schema import conversations, turns, governance_candidates, governance_applications
from app.chat.workspace import git, prepare_workspace, snapshot
from app.governance import store, scope
from app.governance.candidates import frontmatter, validate
from app.governance.preparation import (prepare_object_session, prepare_command_snapshot,
    bind_prepared_turn, initialize_workspace, collect, _command_baseline_id,
    _checkpoint_applied_workspace, execution_prompt_for_turn)
from app.governance.snapshot import stable
from app.governance.writer import process
from test_chat import chat
from test_governance_candidates import contents, front, OID, BASE


def completed():
    before=contents()[1];after=copy.deepcopy(before)
    for name in ('requirement.md','user-stories.md','business-flow.md','acceptance.md'):
        after[f'{BASE}/{name}']=front({'requirement_id':OID,'status':'pending_review'})
    meta,_=frontmatter(before[f'{BASE}/trace.md'])
    meta.update(status='pending_review',knowledge_base_refs=['docs/knowledge-base/test.md'])
    meta['lifecycle']['completed']='2026-09-30'
    after[f'{BASE}/trace.md']=front(meta)
    for p in ('issues/requirements/_registry.yaml','issues/requirements/CHANGELOG.md'):
        after[p]=after[p].replace(b'draft',b'pending_review')
    return before,after


def test_requirement_noop_requires_complete_valid_facts():
    _,after=completed()
    assert validate(after,after,OID,BASE,'req-complete')['files']==[]
    del after[f'{BASE}/user-stories.md']
    with pytest.raises(service.ChatError):validate(after,after,OID,BASE,'req-complete')


@pytest.mark.parametrize('failure',['missing','outside','stage','identity','other_index'])
def test_completion_rejects_incomplete_or_unbounded_results(failure):
    before,after=completed()
    assert validate(before,after,OID,BASE,'req-complete')['manifest_hash']
    if failure=='missing':del after[f'{BASE}/acceptance.md']
    elif failure=='outside':after['src/other.py']=b'changed'
    elif failure=='stage':after[f'{BASE}/trace.md']=after[f'{BASE}/trace.md'].replace(b'pending_review',b'enriching')
    elif failure=='identity':after[f'{BASE}/user-stories.md']=after[f'{BASE}/user-stories.md'].replace(OID.encode(),b'REQ-9999-other')
    else:after['issues/requirements/CHANGELOG.md']+=b'\nother object'
    with pytest.raises(service.ChatError):validate(before,after,OID,BASE,'req-complete')


def test_temporary_lock_profile_preserves_repository_security(tmp_path):
    from app.chat.container_server import write_profiles
    write_profiles(tmp_path)
    config=tomllib.loads((tmp_path/'config.toml').read_text())
    for profile in config['permissions'].values():
        assert profile['filesystem']['/tmp']=='write'
        assert profile['filesystem']['/runtime']=='deny'
        assert profile['filesystem']['/work/.git']=='read'
        assert profile['network']['enabled'] is False
    assert config['permissions']['moonbox-read']['filesystem']['/work']=='read'


@pytest.mark.parametrize('conflict',[None,'source','unrelated','no_provenance'])
def test_preserved_completion_round_trip(chat,tmp_path,monkeypatch,conflict):
    _,factory=chat;root=tmp_path/'repo';root.mkdir()
    private=tmp_path/'private';private.mkdir(mode=0o700)
    workspaces=tmp_path/'workspaces';workspaces.mkdir()
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{
        'id':'repo','space_id':'space','governance_root':str(root),'workspace_root':str(workspaces)}]))
    before,after=completed()
    for p,b in before.items():
        target=root/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
    git(root,'init');git(root,'add','.')
    git(root,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','baseline')
    with factory() as db:
        parent_info=prepare_object_session(db,'alice','space','repo',OID,action='req-complete')
        parent=service.conversation(db,'alice',parent_info['conversation_id'])
        workspace=prepare_workspace(root,workspaces,parent['id'])['path']
        prior=service.identity()
        db.execute(insert(turns).values(**prior,conversation_id=parent['id'],client_request_id='old',
            prompt=f'/req-complete {OID}',status='stopped',executor_turn_id=None if conflict=='no_provenance' else 'executed'))
        store.write(_command_baseline_id(parent['id'],'old'),'baseline',{'object_id':OID,'files':{p:b.decode() for p,b in before.items()}})
        retained=workspace/f'{BASE}/user-stories.md';retained.write_bytes(after[f'{BASE}/user-stories.md'])
        if conflict=='source':(root/f'{BASE}/requirement.md').write_bytes(before[f'{BASE}/requirement.md']+b'\nnew source')
        if conflict=='unrelated':(workspace/'other.txt').write_text('preserve me')
        preserved=snapshot(workspace)['hash']
        if conflict:
            with pytest.raises(service.ChatError):prepare_command_snapshot(db,'alice',parent,f'/req-complete {OID}','resume')
            assert snapshot(workspace)['hash']==preserved
            return
        prepare_command_snapshot(db,'alice',parent,f'/req-complete {OID}','resume')
        turn=service.identity()
        db.execute(insert(turns).values(**turn,conversation_id=parent['id'],client_request_id='resume',prompt=f'/req-complete {OID}',status='completed'))
        bind_prepared_turn(db,parent['id'],turn['id'])
        db.execute(update(conversations).where(conversations.c.id==parent['id']).values(active_turn_id=turn['id']));db.commit()
        parent=service.conversation(db,'alice',parent['id'])
        assert '保留当前工作区' in execution_prompt_for_turn(db,parent,f'/req-complete {OID}')
        initialize_workspace(db,parent,root,workspace)
        assert snapshot(workspace)['hash']==preserved
        for p,b in after.items():
            target=workspace/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
        project=scope.authorize(db,'alice','space','repo',write=True)
        permit=private/'maintenance.json';permit.write_text(json.dumps({'scope_key':project.key,
            'binding_revision':project.binding_revision,'registered_writers':['governance-controller'],
            'external_writers_paused':True,'expires_at':time.time()+600}));permit.chmod(0o600)
        from app.governance.readiness import publish
        publish()
        collect(db,parent,turn['id'],workspace,'completed')
        candidate=db.execute(select(governance_candidates)).mappings().one()
        assert candidate['state']=='pending',dict(candidate)
        assert store.read(candidate['id'],'baseline')['binding_revision']==project.binding_revision
        application=db.execute(select(governance_applications)).mappings().one()
        assert process(db,application['id'])['state']=='applied'
        assert stable(root).files==after
        from app.governance.completion_recovery import checkpoint_applied_completions
        checkpoint_applied_completions(factory,lambda cid:(root,workspace))
        assert git(workspace,'status','--porcelain').strip()  # Active turns block checkpointing.
        db.execute(update(conversations).where(conversations.c.id==parent['id']).values(active_turn_id=None));db.commit()
        checkpoint_applied_completions(factory,lambda cid:(root,workspace))
        assert not git(workspace,'status','--porcelain').strip()
        assert store.read(candidate['id'],'baseline')['workspace_checkpoint_commit']
        assert retained.read_bytes()==after[f'{BASE}/user-stories.md']
