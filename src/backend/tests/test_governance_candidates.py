import copy
import json
from pathlib import Path
import pytest
import yaml
from sqlalchemy import insert, select, update
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import mysql
from app.chat import service
from app.chat.schema import governance_candidates,governance_applications,governance_project_locks,turns
from app.chat.workspace import git,prepare_workspace
from app.governance.candidates import validate
from app.governance.preparation import prepare, initialize_workspace, collect
from app.governance import store
from test_chat import chat
from test_governance_scope import bind,fixture_tree

OID='REQ-0099-local-check';BASE=f'issues/requirements/plan/{OID}'

def front(data,body='\n需求说明正文，包含本地验证目标与验收条件。\n'):
    return ('---\n'+yaml.safe_dump(data,allow_unicode=True)+'---\n'+body).encode()


def contents():
    meta={'requirement_id':OID,'status':'captured','iteration':None,'openspec_changes':[], 'lifecycle':{'captured':'2026-09-11'}}
    files={f'{BASE}/capture.md':b'captured input',f'{BASE}/trace.md':front(meta),
      'issues/requirements/_registry.yaml':yaml.safe_dump({'next_id':100,'entries':[{'id':OID,'status':'captured','path':BASE}]}).encode(),
      'issues/bugs/_registry.yaml':b'entries: []\n',
      'issues/requirements/CHANGELOG.md':front({'purpose':'index','updated_at':'2026-09-11'},f'| {OID} | captured | {BASE} |\n')}
    result=copy.deepcopy(files);result[f'{BASE}/requirement.md']=front({'requirement_id':OID,'status':'draft'})
    meta['status']='draft';meta['lifecycle']['generated']='2026-09-11';result[f'{BASE}/trace.md']=front(meta)
    result['issues/requirements/_registry.yaml']=files['issues/requirements/_registry.yaml'].replace(b'captured',b'draft')
    result['issues/requirements/CHANGELOG.md']=files['issues/requirements/CHANGELOG.md'].replace(b'captured',b'draft')
    return files,result


def test_fixed_write_set_and_semantic_rejection():
    before,after=contents();result=validate(before,after,OID,BASE)
    assert len(result['files'])==4 and result['manifest_hash']
    for name,body in [('src/evil.py',b'code'),('openspec/specs/live/spec.md',b'live'),('issues/bugs/_registry.yaml',b'entries: [other]')]:
        bad={**after,name:body}
        with pytest.raises(service.ChatError): validate(before,bad,OID,BASE)
    bad=copy.deepcopy(after);bad[f'{BASE}/trace.md']=bad[f'{BASE}/trace.md'].replace(b'iteration: null',b'iteration: sprint-999')
    with pytest.raises(service.ChatError): validate(before,bad,OID,BASE)
    bad=copy.deepcopy(after);bad['issues/requirements/CHANGELOG.md']+=b'\nother row changed'
    with pytest.raises(service.ChatError): validate(before,bad,OID,BASE)


@pytest.mark.parametrize("terminal", ["completed", "failed", "stopped"])
def test_prepare_isolated_uncommitted_and_success_candidate(chat,tmp_path,monkeypatch,terminal):
    _,factory=chat;source=tmp_path/'repo';source.mkdir();private=tmp_path/'private';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private));bind(monkeypatch,source)
    before,after=contents()
    for name,body in before.items():
        path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
    for name in ['AGENTS.md','openspec/project.md','.agents/skills/req-generate/SKILL.md','.agents/skills/workflow-sync/SKILL.md','scripts/sync-workflow-status.py','scripts/ai_usage.py']:
        target=source/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('# Synthetic control file\n')
    git(source,'init');git(source,'add','.');git(source,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','baseline')
    (source/f'{BASE}/capture.md').write_text('latest uncommitted governance input')
    workspaces=tmp_path/'workspaces';workspaces.mkdir()
    with factory() as db:
        prepared=prepare(db,'alice','space','repo',OID)
        assert db.scalar(select(turns.c.id)) is None
        cid=prepared['conversation_id'];parent=service.conversation(db,'alice',cid)
        path=prepare_workspace(source,workspaces,cid)["path"]
        from app.chat.policy import write_allowed
        assert not write_allowed(db,'alice',parent)
        initialize_workspace(db,parent,source,path)
        assert write_allowed(db,'alice',parent)
        assert (path/f'{BASE}/capture.md').read_text()=='latest uncommitted governance input'
        for name,body in after.items():
            if name.endswith('capture.md'):continue
            target=path/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
        turn=service.identity();db.execute(insert(turns).values(**turn,conversation_id=cid,client_request_id='test',status=terminal,prompt='synthetic'));db.commit()
        collect(db,parent,turn['id'],path,terminal)
        row=db.execute(select(governance_candidates)).mappings().one()
        assert row['state']==('pending' if terminal=='completed' else 'rejected')
        assert not (source/f'{BASE}/requirement.md').exists()
        if terminal=='completed':assert store.read(row['id'],'result')['manifest_hash']==row['manifest_hash']
        with pytest.raises(service.ChatError):initialize_workspace(db,parent,source,path)


def test_mysql_schema_compiles_with_durable_identity():
    for table in (governance_candidates,governance_applications,governance_project_locks):
        statement=str(CreateTable(table).compile(dialect=mysql.dialect()))
        assert table.name in statement
    assert 'uq_governance_application_request' in str(CreateTable(governance_applications).compile(dialect=mysql.dialect()))
