import json
import time
from types import SimpleNamespace
import pytest
from app.verification import chat_preflight as preflight
from app.verification.acceptance_state import Conflict
from app.api.v1.admin_auth import require_session_user
from app.main import app
from test_chat import chat


@pytest.fixture
def configured(monkeypatch,tmp_path):
    monkeypatch.setattr(preflight.chat,'conversation',lambda *args:{'space_id':'space','repository_id':'repo'})
    monkeypatch.setattr(preflight,'repository_binding',lambda *args:{'source_root':str(tmp_path)})
    monkeypatch.setattr(preflight,'inspect_authorized',lambda *args:{'status':'ready','reason_code':None,'environment_key':'a'*64,'checks':{'dependencies':True}})
    monkeypatch.setattr(preflight,'approved_template',lambda *args:SimpleNamespace(key='b'*64))
    monkeypatch.setenv('MOONBOX_VERIFICATION_STATE_ROOT',str(tmp_path))
    (tmp_path/'worker-ready.json').write_text(json.dumps({'time':time.time()}))
    return tmp_path


def test_configured_is_not_acceptance_passed(configured):
    result=preflight.inspect_conversation(None,'actor','conversation')
    assert result['status']=='configured' and result['acceptance_passed'] is False
    assert next(c for c in result['checks'] if c['name']=='python')['status']=='configured'
    assert str(configured) not in json.dumps(result)


@pytest.mark.parametrize('mode',['missing','stale','future','symlink','malformed'])
def test_missing_worker_is_independent_of_configured_python(configured,mode):
    marker=configured/'worker-ready.json'
    if mode=='missing':marker.unlink()
    elif mode=='symlink':
        marker.unlink();marker.symlink_to(configured/'elsewhere')
    elif mode=='malformed':marker.write_text('[]')
    else:marker.write_text(json.dumps({'time':time.time()+100 if mode=='future' else time.time()-100}))
    result=preflight.inspect_conversation(None,'actor','conversation')
    assert result['status']=='unavailable'
    assert next(c for c in result['checks'] if c['name']=='worker')['reason_code']=='verification_worker_unavailable'
    assert next(c for c in result['checks'] if c['name']=='python')['status']=='configured'


def test_template_failure_does_not_hide_browser(configured,monkeypatch):
    monkeypatch.setattr(preflight,'approved_template',lambda *args:(_ for _ in ()).throw(Conflict('acceptance_template_untrusted')))
    result=preflight.inspect_conversation(None,'actor','conversation')
    assert result['template_key'] is None
    assert result['checks'][0]['status']=='ready'
    assert 'untrusted' not in json.dumps(result)


def test_online_worker_browser_failure_has_distinct_safe_reason(configured,monkeypatch):
    monkeypatch.setattr(preflight,'inspect_authorized',lambda *args:{'status':'unavailable',
        'reason_code':'verification_worker_unavailable','checks':{}})
    monkeypatch.setenv('MOONBOX_VERIFICATION_IMAGE_ID','sha256:'+'a'*64)
    marker=configured/'worker-ready.json'
    for reason,expected in [('browser_probe_failed','browser_probe_failed'),
                            ('private diagnostic','verification_worker_unavailable')]:
        marker.write_text(json.dumps({'time':time.time(),'image_digest':'sha256:'+'a'*64,'browser_reason':reason}))
        result=preflight.inspect_conversation(None,'actor','conversation')
        assert result['checks'][0]['reason_code']==expected
        assert next(c for c in result['checks'] if c['name']=='worker')['status']=='ready'


def test_http_checks_conversation_authorization_before_probes(chat,monkeypatch):
    client,_=chat
    called=[]
    monkeypatch.setattr(preflight,'repository_binding',lambda *args:called.append(args))
    app.dependency_overrides[require_session_user]=lambda:{'id':'bob'}
    response=client.get('/api/v1/chat/conversations/foreign/verification-preflight')
    assert response.status_code in (403,404) and not called


def test_prompt_distinguishes_native_tool_support(configured):
    result=preflight.inspect_conversation(None,'actor','conversation')
    assert '以实际工具清单为准' in preflight.prompt_summary(result,tool_available=False)
    assert '调用moonbox_acceptance' in preflight.prompt_summary(result,tool_available=True)


def test_authorized_http_result_and_binding_revocation(chat,monkeypatch,tmp_path):
    from test_chat import create
    client,factory=chat;cid=create(client)
    monkeypatch.setattr(preflight,'repository_binding',lambda *args:{'source_root':str(tmp_path)})
    monkeypatch.setattr(preflight,'inspect_authorized',lambda *args:{'status':'unavailable','reason_code':'package_manifest_invalid','checks':{}})
    monkeypatch.delenv('MOONBOX_ACCEPTANCE_TEMPLATE',raising=False)
    response=client.get(f'/api/v1/chat/conversations/{cid}/verification-preflight')
    assert response.status_code==200
    assert response.json()['data']['acceptance_passed'] is False
    assert str(tmp_path) not in response.text
    monkeypatch.setattr(preflight,'repository_binding',lambda *args:None)
    assert client.get(f'/api/v1/chat/conversations/{cid}/verification-preflight').status_code==403


@pytest.mark.parametrize('same,fresh,expected',[(True,True,'ready'),(False,True,'configured'),(True,False,'configured')])
def test_python_probe_requires_current_template_and_fresh_worker(configured,same,fresh,expected):
    (configured/'worker-ready.json').write_text(json.dumps({'time':time.time(),'python':{
        'template_key':('b' if same else 'c')*64,'status':'ready','checked_at':time.time()-(0 if fresh else 100)}}))
    result=preflight.inspect_conversation(None,'actor','conversation')
    assert next(c for c in result['checks'] if c['name']=='python')['status']==expected
    assert result['acceptance_passed'] is False


def test_failed_python_probe_is_not_just_configured(configured):
    (configured/'worker-ready.json').write_text(json.dumps({'time':time.time(),'python':{
        'template_key':'b'*64,'status':'unavailable','checked_at':time.time(),
        'reason_code':'python_test_runtime_unavailable'}}))
    result=preflight.inspect_conversation(None,'actor','conversation')
    check=next(c for c in result['checks'] if c['name']=='python')
    assert check['status']=='unavailable' and check['reason_code']=='python_test_runtime_unavailable'
    assert next(c for c in result['checks'] if c['name']=='worker')['status']=='ready'
