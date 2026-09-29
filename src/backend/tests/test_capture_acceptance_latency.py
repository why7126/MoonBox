"""Opt-in measured API acceptance latency on an isolated representative small repository."""
import json,os,time
import pytest
from test_chat import chat
from test_governance_writer import writing
from test_capture_drafts import content

@pytest.mark.skipif(os.environ.get('CAPTURE_PERF_TEST')!='1',reason='explicit measured acceptance probe')
def test_confirmation_acceptance_p95(chat,writing):
    from app.governance import readiness
    readiness.publish();client,_=chat;scope={'space_id':'space','repository_id':'repo'};samples=[]
    for index in range(20):
        draft=client.post('/api/v1/requirement-center/capture-drafts',params=scope).json()['data']
        url='/api/v1/requirement-center/capture-drafts/'+draft['id']
        assert client.patch(url,params=scope,json={**content(),'expected_revision':1}).status_code==200
        start=time.perf_counter()
        response=client.post(url+'/confirmations',params=scope,json={'expected_revision':2,'idempotency_key':'perf-'+str(index)})
        samples.append(time.perf_counter()-start)
        assert response.status_code==202 and response.json()['data']['issue_links']==[]
    measured={'sample_count':len(samples),'p95_seconds':round(sorted(samples)[18],4),'max_seconds':round(max(samples),4),
              'boundary':'isolated API acceptance; excludes model duration and browser refresh'}
    print(json.dumps(measured))
    assert measured['p95_seconds']<=2
