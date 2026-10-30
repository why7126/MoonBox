"""Registered synthetic project: real Docker/SQL/login/browsers, no model round.

The source exporter is the only substituted boundary; source authority is covered
separately. No product acceptance or model-continuation claim comes from this test.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
import time
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.verification.acceptance_schema import TABLES
from app.verification.acceptance_state import AcceptanceState
from app.verification.acceptance_template import AcceptanceTemplate
from app.verification.acceptance_runtime import DockerRuntime
from app.verification.acceptance_controller import Controller
from test_candidate_supplier import plan

APP = '''import os,time,secrets
from fastapi import FastAPI,Request,HTTPException
from fastapi.responses import HTMLResponse,JSONResponse
from sqlalchemy import create_engine,text
engine=create_engine(os.environ['DATABASE_URL'])
app=FastAPI()
@app.post('/login')
async def login(request:Request):
    value=await request.json()
    with engine.begin() as db:
        row=db.execute(text('SELECT password,role,expires FROM identities WHERE username=:u'),{'u':value.get('username')}).mappings().first()
    if not row or row['expires']<=time.time() or not secrets.compare_digest(row['password'],value.get('password','')):raise HTTPException(401)
    response=JSONResponse({'ok':True});response.set_cookie('synthetic_user',value['username'],httponly=True,samesite='strict');return response
@app.get('/',response_class=HTMLResponse)
def home(request:Request):
    with engine.connect() as db:
        row=db.execute(text('SELECT role,expires FROM identities WHERE username=:u'),{'u':request.cookies.get('synthetic_user','')}).mappings().first()
    if not row or row['expires']<=time.time():raise HTTPException(401)
    return '<h1>Isolated acceptance</h1><p id="role">'+row['role']+'</p>'
@app.get('/health',response_class=HTMLResponse)
def health(request:Request):return home(request) if request.cookies.get('synthetic_user') else HTMLResponse('<h1>Healthy</h1>')
'''
MIGRATE = '''import os
from sqlalchemy import create_engine,text
with create_engine(os.environ['DATABASE_URL']).begin() as db:
    db.execute(text('CREATE TABLE identities (username VARCHAR(64) PRIMARY KEY,password VARCHAR(128),role VARCHAR(16),expires BIGINT)'))
    db.execute(text('CREATE TABLE sample (id INTEGER PRIMARY KEY,value VARCHAR(32))'))
'''
SEED = '''import os
from sqlalchemy import create_engine,text
with create_engine(os.environ['DATABASE_URL']).begin() as db:db.execute(text("INSERT INTO sample VALUES (1,'synthetic')"))
'''
IDENTITY = '''import os,sys,json
from sqlalchemy import create_engine,text
p=json.load(sys.stdin)
with create_engine(os.environ['DATABASE_URL']).begin() as db:
    if sys.argv[1]=='issue':db.execute(text('INSERT INTO identities VALUES (:username,:password,:role,:expires_at)'),p)
    else:db.execute(text('DELETE FROM identities WHERE username=:username'),p)
'''
CHECK = '''import os,json,sys,urllib.request
from sqlalchemy import create_engine,text
p=json.load(sys.stdin)
with create_engine(os.environ['DATABASE_URL']).connect() as db:
    assert db.scalar(text('SELECT value FROM sample WHERE id=1'))=='synthetic'
    assert db.scalar(text('SELECT role FROM identities WHERE username=:username'),p)==p['role']
r=urllib.request.Request('http://127.0.0.1:8000/login',data=json.dumps(p).encode(),headers={'Content-Type':'application/json'})
assert urllib.request.urlopen(r).status==200
'''

@pytest.mark.skipif(os.getenv('MOONBOX_ACCEPTANCE_LIVE')!='1',reason='Registered synthetic Docker matrix is opt-in')
def test_registered_runtime_matrix(tmp_path,monkeypatch):
    assert os.environ.get('MOONBOX_TEMP_RUN') and os.environ.get('MOONBOX_TEMP_EXPIRES')
    project=Path(__file__).resolve().parents[3]
    inputs=[*sorted((project/'src/backend/app/verification').glob('acceptance_*.py')),
            project/'src/backend/app/verification/runner.py',project/'src/backend/app/verification/candidate.py',
            project/'src/backend/container/verification_acceptance.cjs',Path(__file__).resolve()]
    hashes={str(path.relative_to(project)):hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs}
    root=tmp_path.resolve();source=root/'synthetic-source';(source/'src').mkdir(parents=True)
    for name,value in {'server.py':APP,'migrate.py':MIGRATE,'seed.py':SEED,'identity.py':IDENTITY,'check.py':CHECK}.items():
        (source/'src'/name).write_text(value)
    (source/'requirements.txt').write_text('fixture-lock\n')
    base=plan(python_image=os.environ['CANDIDATE_PYTHON_IMAGE'],mysql_image=os.environ['CANDIDATE_MYSQL_IMAGE'],
              browser_image=os.environ['CANDIDATE_BROWSER_IMAGE'],health_path='/health',selectors=['h1','#role']).data
    versions=json.loads(os.environ['ACCEPTANCE_RUNTIME_VERSIONS'])
    template=AcceptanceTemplate.parse(dict(schema_version=1,template='moonbox-chat-acceptance-v1',base=base,
        node_image=os.environ['CANDIDATE_NODE_IMAGE'],runtime_versions=versions,roles=['member','reader'],
        checks={'AC-001':{'argv':['python','check.py'],'database':'sqlite','role':'member'},
                'AC-002':{'argv':['python','check.py'],'database':'mysql','role':'reader'}},
        disk_strategy='bounded-tmpfs',deployment_digest='d'*64,
        identity_adapter={'issue':['python','identity.py','issue'],'revoke':['python','identity.py','revoke'],
                          'login':{'path':'/login','username_field':'username','password_field':'password'}}))
    def export(factory,reference,destination,approved):shutil.copytree(source,destination)
    monkeypatch.setattr('app.verification.acceptance_runtime.export_checkpoint',export)
    engine=create_engine('sqlite:///'+str(root/'state.db'))
    for table in TABLES:table.create(engine)
    state=AcceptanceState(sessionmaker(engine))
    item=state.create(actor='synthetic',space='synthetic-space',repository='synthetic-repo',conversation='synthetic-chat',
        turn='synthetic-turn',change='synthetic-change',request_key='runtime-matrix',binding='b'*64,input_digest='a'*64,
        plan={'checks':[{'id':ac,'inputs':['src/server.py']} for ac in template.data['checks']]},
        source_ref={'head_commit':'a'*40})
    runtime=DockerRuntime(state,template,root/'environments')
    stopped=threading.Event();samples=[];cancelled_at=[]
    def inspect_limits():
        while not stopped.wait(2):
            if not runtime.engine:continue
            try:
                ids=subprocess.check_output(['docker','ps','-q','--filter','label=moonbox.candidate.environment='+item['attempt_id']],text=True,timeout=15).split()
                if not ids:continue
                rows=json.loads(subprocess.check_output(['docker','inspect',*ids],text=True,timeout=15))
                sample=[]
                for row in rows:
                    host=row['HostConfig']
                    sample.append({'cpu_nanos':host['NanoCpus'],'memory':host['Memory'],
                        'readonly':host['ReadonlyRootfs'],'pids':host['PidsLimit'],'tmpfs':host.get('Tmpfs',{}),
                        'published_ports':bool(host.get('PortBindings')),'log_driver':host['LogConfig']['Type'],
                        'kind':'browser' if row['Name'].startswith('/moonbox-verification-') else 'application_or_database'})
                samples.append(sample)
                if os.getenv('ACCEPTANCE_CANCEL_AFTER_START')=='1' and not cancelled_at:
                    current=state.get(item['id'])
                    state.cancel(item['id'],current['version'])
                    cancelled_at.append(time.monotonic())
            except (OSError,ValueError,subprocess.SubprocessError):pass
    monitor=threading.Thread(target=inspect_limits,daemon=True);monitor.start()
    try:result=Controller(state,runtime,lambda oid:None).run(item['id'],'synthetic-worker')
    finally:stopped.set();monitor.join(timeout=35)
    report={'category':'synthetic_project_real_runtime','source_authority':'substituted exporter',
            'model_round':'not_exercised','status':result['status'],'cleanup':result['cleanup_state'],
            'reason_code':result['reason_code'],'checks':[{'ac_id':x['ac_id'],'status':x['status'],'reason_code':x['reason_code']} for x in result['checks']],
            'observed_limits':samples,'runtime_versions':versions,'template_digest':template.key}
    report['source_hashes']=hashes
    if cancelled_at:report['cancel_to_release_seconds']=round(time.monotonic()-cancelled_at[0],2)
    report['source_stable']=all(hashlib.sha256((project/name).read_bytes()).hexdigest()==digest for name,digest in hashes.items())
    report_path=Path(os.environ.get('MOONBOX_ACCEPTANCE_RUNTIME_REPORT','/tmp/req0048-runtime-report.json'))
    report['screenshots']=[]
    for index,picture in enumerate(sorted((root/'environments').rglob('*.png'))):
        name=report_path.stem+'-'+str(index)+'.png';shutil.copy2(picture,report_path.parent/name)
        report['screenshots'].append({'file':name,'sha256':hashlib.sha256(picture.read_bytes()).hexdigest()})
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    assert result['cleanup_state']=='released',report
    assert report['source_stable'],'runtime inputs changed during observation'
    assert samples,'runtime limits were not observed'
    for sample in samples:
        assert sum(row['cpu_nanos'] for row in sample)<=4_000_000_000
        assert sum(row['memory'] for row in sample)<=8*1024**3
        assert all(row['readonly'] and not row['published_ports'] and row['log_driver']=='none' for row in sample)
    if os.getenv('ACCEPTANCE_CANCEL_AFTER_START')=='1':
        assert result['status']=='cancelled' and result['cancel_requested'],report
        assert result['resume_count']==0
        assert report['cancel_to_release_seconds']<=60,report
    elif os.getenv('ACCEPTANCE_EXPECT_BROWSER_BLOCKED')=='1':
        assert result['status']=='blocked',report
        assert all(check['reason_code']=='browser_acceptance_failed' for check in result['checks']),report
    else:
        assert result['status']=='passed',report
