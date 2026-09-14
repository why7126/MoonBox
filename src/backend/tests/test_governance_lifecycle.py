import sys
from pathlib import Path
import pytest
from test_chat import chat
from test_governance_scope import bind
from lifecycle_fixture import populate, IDS
from app.governance.snapshot import stable
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
from scripts.workflow_sync.execution import transition
from scripts.workflow_sync.collect import ChangeRecord, TaskProgress

@pytest.mark.parametrize('kind',['requirement','bug'])
def test_context_observes_zero_start_and_completion(chat,tmp_path,monkeypatch,kind):
    monkeypatch.setattr("app.services.requirement_center._load_workspaces", lambda *args: [])
    client,_=chat;root=tmp_path/'project';populate(root);bind(monkeypatch,root)
    query={'space_id':'space','repository_id':'repo'}
    def get():
        response=client.get('/api/v1/requirement-center/context',params=query)
        assert response.status_code==200,response.text
        data=response.json()['data'];issue=next(x for x in data['issues'] if x['id'].startswith(IDS[kind].split('-lifecycle')[0]))
        return data,issue
    before,item=get();assert item['stage']=='ready-dev'
    record=ChangeRecord('fix-'+kind+'-lifecycle','active',tasks=TaskProgress(0,2))
    transition(root,record,'opsx.start',write=True)
    during,item=get();assert during['snapshot_revision']!=before['snapshot_revision']
    assert item['stage']=='development' and item['tasks']['done']==0
    assert item['action']['label']=='查看进度'
    tasks=root/'openspec/changes'/record.change_id/'tasks.md';tasks.write_text(tasks.read_text().replace('[ ]','[x]'))
    record.tasks.done=2
    _,item=get();assert item['stage']=='development'
    transition(root,record,'opsx.apply',write=True)
    _,item=get();assert item['stage']=='acceptance'
