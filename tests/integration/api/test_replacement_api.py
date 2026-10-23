"""Real authenticated API and persistent migration boundaries."""
import json
import pytest
from sqlalchemy import text, inspect
from app.db.session import get_session_factory
from test_requirement_center import _auth_headers, _seed_space_facts


def test_replacement_routes_require_session_and_scope(api_client, tmp_path, monkeypatch):
    headers=_auth_headers(api_client)
    with get_session_factory()() as db:
        actor=db.execute(text("SELECT id FROM admin_users WHERE username='superadmin'")).scalar_one()
        tables=set(inspect(db.get_bind()).get_table_names())
    assert {'replacement_proposals','replacement_authorization_events','policy_activation_operations','replacement_archive_operations'}<=tables
    _seed_space_facts(actor,actor,actor)
    root=tmp_path/'governance';root.mkdir()
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORIES',json.dumps([{'id':'repo','space_id':'space_owned'}]))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{'id':'repo','space_id':'space_owned','governance_root':str(root)}]))
    query={'space_id':'space_owned','repository_id':'repo'}
    assert api_client.get('/api/v1/chat/replacement-proposals',params=query).status_code==401
    result=api_client.get('/api/v1/chat/replacement-proposals',params=query,headers=headers)
    assert result.status_code==200,result.text
    assert result.json()['data']=={'items':[]}
    assert str(root) not in result.text
    assert api_client.get('/api/v1/chat/replacement-proposals',params={**query,'space_id':'unrelated'},headers=headers).status_code==403
    denied=api_client.post('/api/v1/chat/replacement-proposals/missing/approve',headers=headers,json={
        'expected_revision':1,'proposal_digest':'a'*64,'idempotency_key':'request','confirmed':True})
    assert denied.status_code==409
    assert denied.json()['data']['kind']=='legacy_replacement_retired'


def test_worker_actor_is_not_a_human_session(api_client,tmp_path,monkeypatch):
    from app.governance.replacement_authorization import require_owner
    from app.governance.scope import ProjectScope
    from app.chat.service import ChatError
    import pytest
    with get_session_factory()() as db:
        with pytest.raises(ChatError,match='登录确认'):
            require_owner(db,{'id':'owner'},ProjectScope('space','repo',tmp_path,'a'*64,False))


@pytest.fixture
def authenticated_proposal(api_client,tmp_path,monkeypatch):
    """Real sessions/scope/audit; evidence classification is a separate unit suite."""
    import base64
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    from sqlalchemy import insert
    from app.chat.service import identity
    from app.governance import scope,replacement_api,replacement_trust,replacement_signer
    from app.governance.replacement_schema import proposals,activations
    from app.governance.replacement_proof import PROTECTED,canonical,digest
    from test_requirement_center import _create_frontend_user,_login
    headers=_auth_headers(api_client)
    member,password=_create_frontend_user(api_client,'replacementReviewer')
    member_headers=_login(api_client,member['username'],password)
    with get_session_factory()() as db:
        owner=db.execute(text("SELECT id FROM admin_users WHERE username='superadmin'")).scalar_one()
    _seed_space_facts(owner,member['id'],owner)
    with get_session_factory()() as db:
        db.execute(text("INSERT INTO admin_space_members (id,space_id,user_id,role,created_at,updated_at) VALUES ('replacement-member','space_owned',:actor,'管理员','2026-10-22','2026-10-22')"),{'actor':member['id']});db.commit()
    root=tmp_path/'repository';root.mkdir()
    for path,body in {'issues/requirements/_registry.yaml':'entries: []\n','issues/bugs/_registry.yaml':'entries: []\n',
                      'openspec/changes/fix-sample/trace.md':'---\nstatus: applied\n---\n'}.items():
        target=root/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(body)
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORIES',json.dumps([{'id':'repo','space_id':'space_owned'}]))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{'id':'repo','space_id':'space_owned','governance_root':str(root)}]))
    private=tmp_path/'state';private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private))
    with get_session_factory()() as db:project=scope.authorize(db,owner,'space_owned','repo',write=True)
    key=Ed25519PrivateKey.generate()
    public=base64.b64encode(key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)).decode()
    trust=replacement_trust.Trust({'owner-key':public},frozenset(),{},'policy-v1','f'*64,
        {f'replacement.{action}':['owner-key'] for action in ('approve','reject','revoke')})
    monkeypatch.setattr(replacement_trust,'load',lambda root:trust)
    monkeypatch.setattr(replacement_signer,'sign',lambda payload:{'key_id':'owner-key','payload':payload,
        'signature':base64.b64encode(key.sign(canonical(payload))).decode()})
    monkeypatch.setattr(replacement_api,'validate',lambda *args:None)
    evidence={'path':'openspec/proof-evidence/review.json','sha256':'c'*64}
    body={'schema_version':1,'classification':'guarded_exception_extension','project_id':project.key,
        'binding_revision':project.binding_revision,'successor':'fix-sample','predecessors':['prior-change'],
        'capability':'archive','requirement':'归档规则','before':'原规则','after':'新增例外','delta_sha256':'d'*64,
        'acceptance_sha256':'e'*64,'delivery_sha256':'f'*64,'policy_version':'policy-v1','verifier_version':'replacement-v1',
        'obligations':[{'id':name,'source':evidence,'before':'保护保持','after':'保护保持'} for name in sorted(PROTECTED)],
        'edits':[{'profile_id':'sample','before':'原规则','after':'新增例外','exception':'compatible_append_verified'}],
        'review':evidence,'regression':evidence}
    with get_session_factory()() as db:
        db.execute(insert(activations).values(**identity(),scope_key=project.key,binding_revision=project.binding_revision,
            policy_version=trust.policy_version,state='active',manifest_hash='d'*64,manifest='{}',revision=1))
        db.execute(insert(proposals).values(**(identity()|{'id':'sample'}),scope_key=project.key,space_id='space_owned',
            repository_id='repo',binding_revision=project.binding_revision,change_id='fix-sample',digest=digest(body),
            body=canonical(body).decode(),prepared_by=owner,revision=1,state='prepared'));db.commit()
    return headers,member_headers,{'expected_revision':1,'proposal_digest':digest(body),'idempotency_key':'approval-one','confirmed':True}


@pytest.mark.parametrize('action', ['approve', 'reject', 'revoke'])
def test_legacy_decisions_are_readable_but_cannot_write(api_client, authenticated_proposal, action):
    from sqlalchemy import select, func
    from app.governance.replacement_schema import proposals, events, commits
    owner_headers, member_headers, payload = authenticated_proposal
    query = {'space_id': 'space_owned', 'repository_id': 'repo'}
    for headers in (owner_headers, member_headers):
        historical = api_client.get('/api/v1/chat/replacement-proposals', headers=headers, params=query)
        assert historical.status_code == 200, historical.text
        assert historical.json()['data']['items'][0]['id'] == 'sample'
        result = api_client.post(f'/api/v1/chat/replacement-proposals/sample/{action}',
                                 headers=headers, json=payload)
        assert result.status_code == 409, result.text
        assert result.json()['data']['kind'] == 'legacy_replacement_retired'
    with get_session_factory()() as db:
        assert db.scalar(select(proposals.c.state)) == 'prepared'
        assert db.scalar(select(func.count()).select_from(events)) == 0
        assert not db.execute(select(commits)).first()


def test_legacy_installation_preview_is_retired_without_writes(api_client, authenticated_proposal):
    from sqlalchemy import select, func
    from app.governance.replacement_schema import activations, events
    owner_headers, member_headers, _ = authenticated_proposal
    payload = {'space_id': 'space_owned', 'repository_id': 'repo', 'mechanism_change': 'fix-sample'}
    assert api_client.post('/api/v1/chat/replacement-policy/preview', json=payload).status_code == 401
    with get_session_factory()() as db:
        before_activations = db.scalar(select(func.count()).select_from(activations))
        before_events = db.scalar(select(func.count()).select_from(events))
    for headers in (owner_headers, member_headers):
        result = api_client.post('/api/v1/chat/replacement-policy/preview',
                                 headers=headers, json=payload)
        assert result.status_code == 409, result.text
        assert result.json()['data']['kind'] == 'legacy_installation_retired'
    with get_session_factory()() as db:
        assert db.scalar(select(func.count()).select_from(activations)) == before_activations
        assert db.scalar(select(func.count()).select_from(events)) == before_events


def test_current_rule_confirmation_requires_owner_and_exact_content(api_client, authenticated_proposal, monkeypatch):
    from sqlalchemy import select, func
    from app.governance import rule_change_api
    from app.governance.replacement_proof import digest
    from app.governance.rule_change_schema import confirmations, events
    from app.governance.replacement_schema import archive_operations

    owner_headers, member_headers, _ = authenticated_proposal
    content = {'schema_version': 2, 'change_id': 'fix-sample', 'before': '原规则',
               'after': '允许新增场景', 'binding_revision': 'current-binding'}
    monkeypatch.setattr(rule_change_api, 'candidate', lambda *_: dict(content))
    payload = {'space_id': 'space_owned', 'repository_id': 'repo', 'change_id': 'fix-sample',
               'content_digest': digest(content), 'action': 'confirm', 'request_key': 'owner-confirm-1'}
    endpoint = '/api/v1/chat/rule-changes/decision'
    assert api_client.post(endpoint, json=payload).status_code == 401
    denied = api_client.post(endpoint, headers=member_headers, json=payload)
    assert denied.status_code == 403, denied.text
    accepted = api_client.post(endpoint, headers=owner_headers, json=payload)
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()['data'] == {'state': 'confirmed', 'replayed': False}
    replay = api_client.post(endpoint, headers=owner_headers, json=payload)
    assert replay.status_code == 200 and replay.json()['data']['replayed'] is True
    content['after'] = '另一版本'
    stale = api_client.post(endpoint, headers=owner_headers,
                            json={**payload, 'request_key': 'owner-confirm-2'})
    assert stale.status_code == 409, stale.text
    with get_session_factory()() as db:
        assert db.scalar(select(func.count()).select_from(confirmations)) == 1
        assert db.scalar(select(func.count()).select_from(events)) == 1
        assert not db.execute(select(archive_operations)).first()
