"""Opt-in local integration: temporary DB/repository, real MinIO and model, synthetic material."""
import base64,json,os,subprocess
from types import SimpleNamespace
import pytest
from test_chat import chat
from test_governance_writer import writing
from test_capture_media import png
from app.governance import capture_media,capture_organizer

REMOTE='''import json,sys,base64
from app.core.object_storage import get_object_storage
from types import SimpleNamespace
r=json.load(sys.stdin);s=get_object_storage()
if r['op']=='put':s.put(r['key'],base64.b64decode(r['data']),r['mime']);print('{}')
elif r['op']=='remove':s.remove(r['key']);print('{}')
elif r['op']=='get':
 v=s.get(r['key']);print(json.dumps({'data':base64.b64encode(v.data).decode(),'mime':v.content_type}))
else:
 from app.governance.capture_executor import execute
 images=[(i['id'],SimpleNamespace(data=base64.b64decode(i['data']),content_type=i['mime'])) for i in r['images']]
 print(json.dumps({'result':execute(r['prompt'],images)}))
'''

def remote(payload):
    result=subprocess.run(['docker','exec','-i','moonbox-chat-worker','python','-c',REMOTE],input=json.dumps(payload),
        capture_output=True,text=True,timeout=340)
    if result.returncode:raise RuntimeError('local_live_probe_failed')
    return json.loads(result.stdout)

@pytest.mark.skipif(os.environ.get('CAPTURE_LIVE_TEST')!='1',reason='explicit local integration only')
def test_real_upload_preview_model_and_owner_boundary(chat,writing,monkeypatch):
    from app.main import app
    from app.api.v1.admin_auth import require_session_user
    from app.governance.snapshot import stable
    keys=[]
    class Storage:
        def put(self,key,content,mime):keys.append(key);remote({'op':'put','key':key,'data':base64.b64encode(content).decode(),'mime':mime})
        def get(self,key):
            r=remote({'op':'get','key':key});return SimpleNamespace(data=base64.b64decode(r['data']),content_type=r['mime'])
    monkeypatch.setattr(capture_media,'get_object_storage',Storage)
    client,factory=chat;_,project,before,*_=writing;query={'space_id':'space','repository_id':'repo'}
    try:
        draft=client.post('/api/v1/requirement-center/capture-drafts',params=query).json()['data']
        url='/api/v1/requirement-center/capture-drafts/'+draft['id']
        response=client.post(url+'/materials',params=query,files={'file':('synthetic.png',png(),'image/png')})
        assert response.status_code==200
        image=response.json()['data'];assert 'object_key' not in image
        preview=client.get(image['preview_url'],params=query)
        assert preview.content==png() and preview.headers['cache-control']=='private, no-store'
        assert client.patch(url,params=query,json={'expected_revision':1,'text':'希望新增草稿保存能力，附件是占位示意图，不应推断图中存在错误。','media_ids':[image['media_id']]}).status_code==200
        with factory() as db:task=capture_organizer.start(db,'alice',project,draft['id'],2)
        def executor(prompt,images):
            return remote({'op':'model','prompt':prompt,'images':[{'id':mid,'data':base64.b64encode(im.data).decode(),'mime':im.content_type} for mid,im in images]})['result']
        capture_organizer.run(factory,task['id'],executor)
        with factory() as db:result=capture_organizer.status(db,'alice',project,draft['id'],task['id'])
        assert result['state']=='ready' and result['result']['candidates'][0]['type']=='requirement'
        assert stable(project.root).files==before
        app.dependency_overrides[require_session_user]=lambda:{'id':'bob'}
        assert client.get(image['preview_url'],params=query).status_code in (403,404)
    finally:
        for key in keys:remote({'op':'remove','key':key})
