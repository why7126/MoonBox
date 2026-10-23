"""Real authenticated HTTP projection over disposable governance sources."""
import json
import yaml
from sqlalchemy import text
from app.db.session import get_session_factory


def test_card_info_refresh_and_authorization(api_client, tmp_path, monkeypatch):
    login = api_client.post('/api/v1/auth/login', json={'username':'superadmin','password':'example-test-password','remember_me':False})
    assert login.status_code == 200
    headers = {'Authorization':'Bearer '+login.json()['data']['access_token']}
    with get_session_factory()() as db:
        actor = db.execute(text("SELECT id FROM admin_users WHERE username='superadmin'")).scalar_one()
    space = api_client.post('/api/v1/admin/spaces', headers=headers, json={'name':'标签隔离样本','code':'card-info','owner_id':actor,'product_id':'card-info','product_name':'标签样本','expiry_type':'long_term'}).json()['data']['id']
    root = tmp_path/'governance'
    (root/'issues/requirements').mkdir(parents=True)
    (root/'issues/requirements/_registry.yaml').write_text('entries: []\n')
    oid = 'BUG-9100-card-info'
    folder = root/'issues/bugs/archive'/oid
    folder.mkdir(parents=True)
    (folder/'trace.md').write_text('---\nstatus: done\niteration: sprint-001\n---\n')
    cause = folder/'root-cause.md'
    cause.write_text('---\nstatus: probable\n---\n## 根因分析\n缓存读取遗漏。\n')
    (root/'issues/bugs/_registry.yaml').write_text(yaml.safe_dump({'entries':[{'id':oid,'path':str(folder.relative_to(root)),'status':'done','iteration':'sprint-001','title':'标签样本'}]}))
    sprint = root/'iterations/archive/sprint-001/sprint.yaml'
    sprint.parent.mkdir(parents=True)
    sprint.write_text(yaml.safe_dump({'bugs':[oid],'scope_estimates':[{'id':oid,'estimated_person_days':0}]}))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORIES',json.dumps([{'id':'card-info','space_id':space}]))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{'id':'card-info','space_id':space,'governance_root':str(root)}]))
    query = {'space_id':space,'repository_id':'card-info'}
    def card():
        response = api_client.get('/api/v1/requirement-center/context',headers=headers,params=query)
        assert response.status_code == 200, response.text
        assert '缓存读取遗漏' not in response.text
        return response.json()['data']['issues'][0]
    initial = card()
    assert initial['estimated_person_days']==0 and initial['root_cause_state']=='pending'
    # Same byte count and same state: the reason must still change.
    cause.write_text(cause.read_text().replace('probable','nonsense'))
    assert card()['root_cause_reason']=='missing'
    cause.write_text(cause.read_text().replace('nonsense','confirmed'))
    assert card()['root_cause_state']=='confirmed'
    sprint.write_text(sprint.read_text().replace('estimated_person_days: 0','estimated_person_days: 3.25'))
    assert card()['estimated_person_days']==3.25
    url=f'/api/v1/requirement-center/issues/{oid}/documents/root-cause.md'
    assert api_client.get(url,headers=headers,params=query).status_code==200
    assert api_client.get(url,params=query).status_code==401
    cause.unlink()
    assert card()['root_cause_state']=='absent'
    assert api_client.get(url,headers=headers,params=query).status_code==404
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS','[]')
    response=api_client.get('/api/v1/requirement-center/context',headers=headers,params=query)
    assert response.status_code!=200 or not response.json()['data'].get('issues')
