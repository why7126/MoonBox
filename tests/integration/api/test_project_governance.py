"""REQ-0022 scoped HTTP contract using real session auth and database schema."""
import json
from pathlib import Path
from sqlalchemy import text
from app.db.session import get_session_factory
from test_requirement_center import _auth_headers,_seed_space_facts


def test_projects_context_and_document_real_session(api_client,tmp_path,monkeypatch):
    headers=_auth_headers(api_client)
    with get_session_factory()() as db:
        actor=db.execute(text("SELECT id FROM admin_users WHERE username='superadmin'")).scalar_one()
    _seed_space_facts(actor,actor,actor)
    for folder in ('requirements','bugs'):
        directory=tmp_path/'governance'/'issues'/folder;directory.mkdir(parents=True)
        (directory/'_registry.yaml').write_text('entries: []\n')
    root=tmp_path/'governance';issue=root/'issues/requirements/plan/REQ-0099-local-check';issue.mkdir(parents=True)
    (issue/'capture.md').write_text('真实接口测试输入')
    (issue/'trace.md').write_text('---\nrequirement_id: REQ-0099-local-check\nstatus: captured\n---\n')
    (root/'issues/requirements/_registry.yaml').write_text('entries:\n  - id: REQ-0099-local-check\n    path: issues/requirements/plan/REQ-0099-local-check\n    title: 本地验证\n    status: captured\n')
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORIES',json.dumps([{'id':'repo','space_id':'space_owned'}]))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{'id':'repo','space_id':'space_owned','governance_root':str(root)}]))
    response=api_client.get('/api/v1/requirement-center/projects',headers=headers)
    assert response.status_code==200,response.text
    assert response.json()['data']['projects'][0]['repository_id']=='repo'
    assert str(root) not in response.text
    query={'space_id':'space_owned','repository_id':'repo'}
    response=api_client.get('/api/v1/requirement-center/context',headers=headers,params=query)
    assert response.status_code==200,response.text
    data=response.json()['data'];assert data['selected_workspace_id']=='space_owned'
    assert data['repository_id']=='repo' and len(data['snapshot_revision'])==64
    assert [item['id'] for item in data['issues']]==['REQ-0099']
    url=data['issues'][0]['document_entries'][0]['url']
    assert 'space_id=space_owned' in url and 'repository_id=repo' in url
    assert api_client.get(url,headers=headers).status_code==200
    assert api_client.get('/api/v1/requirement-center/context',headers=headers).status_code==422
