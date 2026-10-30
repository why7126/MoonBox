"""Supplier state machine tests use synthetic Docker; live case is separately opt-in."""
import hashlib
import json
import os
from pathlib import Path
from uuid import uuid4
import pytest
from sqlalchemy import select, update
from test_chat import chat
from test_managed_worktree_git import repo, git
from app.verification.candidate_template import CandidateTemplate, CandidateError
from app.verification.candidate import CandidateSupplier, DockerEnvironment, export_candidate
from app.verification.candidate_schema import environments


@pytest.fixture(autouse=True)
def synthetic_capacity(monkeypatch):
    if os.getenv('MOONBOX_CANDIDATE_LIVE')!='1':
        monkeypatch.setattr(DockerEnvironment,'capacity_limits',staticmethod(lambda root:dict(
            available_cpu=16,available_memory=32*1024**3,available_disk=100*1024**3,hard_disk_limit=True)))


def plan(**overrides):
    data = dict(schema_version=1, template='moonbox-web-python-v1', platform='linux/arm64',
        python_image='sha256:'+'1'*64, mysql_image='sha256:'+'2'*64, browser_image='sha256:'+'3'*64,
        source_subdir='src', app_module='server:app', health_path='/', lock_path='requirements.txt',
        lock_digest=hashlib.sha256(b'fixture-lock\n').hexdigest(), migration=['python','migrate.py'],
        seed=['python','seed.py'], checks=[['python','check.py']], browser='chromium',
        viewports=[dict(width=1440,height=900),dict(width=390,height=844)], selectors=['h1'], steps=[])
    data.update(overrides)
    return CandidateTemplate.parse(data)


@pytest.mark.parametrize('change', [dict(python_image='python:latest'), dict(platform='linux/amd64'),
    dict(checks=[]), dict(lock_digest=None), dict(app_module=[]), dict(health_path=123), dict(selectors='h1'), dict(steps={}), dict(source_subdir='src//app'), dict(source_subdir='../outside'), dict(lock_digest='unknown'),dict(migration=['sh','-c','anything'])])
def test_template_rejects_unapproved_inputs(change):
    with pytest.raises(CandidateError): plan(**change)


def test_fixed_git_export_and_dependency_mismatch(repo, tmp_path):
    source, _ = repo
    (source.root/'requirements.txt').write_text('fixture-lock\n')
    git(source.root,'add','.'); git(source.root,'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','lock')
    destination=tmp_path/'export'; destination.mkdir()
    (source.root/'requirements.txt').write_text('mutable wrong lock')
    export_candidate(source.root,source.head(),destination,'requirements.txt',plan().data['lock_digest'])
    assert (destination/'requirements.txt').read_text()=='fixture-lock\n'
    with pytest.raises(CandidateError,match='dependency_mismatch'):
        export_candidate(source.root,source.head(),destination,'requirements.txt','0'*64)


def test_cleanup_failure_never_attests_pass_and_retry_reconciles(chat, repo, tmp_path, monkeypatch):
    _,factory=chat; source,_=repo
    supplier=CandidateSupplier(plan(),tmp_path/'envs')
    monkeypatch.setattr(DockerEnvironment,'daemon_id',staticmethod(lambda:'synthetic-daemon'))
    clean={'ok':False}; calls=[]
    def run(self,workspace,stage):
        calls.append(1); stage('checking'); return {'matrices':[]}
    monkeypatch.setattr(DockerEnvironment,'run',run)
    monkeypatch.setattr(DockerEnvironment,'save_evidence',lambda *_:None)
    monkeypatch.setattr(DockerEnvironment,'cleanup',lambda *_:clean['ok'])
    request=dict(candidate_id=str(uuid4()),candidate_commit=source.head(),workspace=source.root,change_id='change',factory=factory,space_id='space',repository_id='repo')
    first=supplier.validate(**request)
    assert first['reason_code']=='candidate_cleanup_pending'
    assert supplier.validate(**request)['reason_code']=='candidate_cleanup_pending'
    assert len(calls)==1
    clean['ok']=True
    result=supplier.validate(**request)
    assert result['status']=='passed'
    assert supplier.validate(**request)==result
    assert len(calls)==2
    with factory() as db:
        row=db.execute(select(environments)).mappings().one()
        assert row['cleanup_state']=='clean'
        assert 'password' not in row['result_json']


def test_unknown_prior_execution_is_not_replayed(chat,repo,tmp_path,monkeypatch):
    _,factory=chat;source,_=repo
    supplier=CandidateSupplier(plan(),tmp_path/'envs')
    monkeypatch.setattr(DockerEnvironment,'daemon_id',staticmethod(lambda:'synthetic-daemon'))
    monkeypatch.setattr(DockerEnvironment,'run',lambda *_: (_ for _ in ()).throw(RuntimeError('hidden secret')))
    monkeypatch.setattr(DockerEnvironment,'cleanup',lambda *_:True)
    request=dict(candidate_id=str(uuid4()),candidate_commit=source.head(),workspace=source.root,change_id='change',factory=factory,space_id='space',repository_id='repo')
    assert supplier.validate(**request)==dict(status='failed',reason_code='candidate_checks_failed')
    with factory.begin() as db: db.execute(update(environments).values(state='checking',cleanup_state='pending'))
    assert supplier.validate(**request)['reason_code']=='candidate_interrupted'
    with factory() as db: assert db.scalar(select(environments.c.state))=='interrupted'


@pytest.mark.skipif(os.getenv('MOONBOX_CANDIDATE_LIVE')!='1',reason='Registered disposable Docker environment required')
def test_real_candidate_sqlite_mysql_browser_and_cleanup(chat,repo,tmp_path):
    _,factory=chat;source,_=repo
    (source.root/'src').mkdir()
    (source.root/'requirements.txt').write_text('fixture-lock\n')
    (source.root/'src/server.py').write_text("from fastapi import FastAPI\nfrom fastapi.responses import HTMLResponse\napp=FastAPI()\n@app.get('/',response_class=HTMLResponse)\ndef home(): return '<h1>Isolated candidate</h1>'\n")
    (source.root/'src/migrate.py').write_text("import os\nfrom sqlalchemy import create_engine,text\nwith create_engine(os.environ['DATABASE_URL']).begin() as db: db.execute(text('CREATE TABLE sample (id INTEGER PRIMARY KEY, value VARCHAR(32))'))\n")
    (source.root/'src/seed.py').write_text("import os\nfrom sqlalchemy import create_engine,text\nwith create_engine(os.environ['DATABASE_URL']).begin() as db: db.execute(text(\"INSERT INTO sample VALUES (1, 'synthetic')\"))\n")
    (source.root/'src/check.py').write_text("import os\nfrom sqlalchemy import create_engine,text\nwith create_engine(os.environ['DATABASE_URL']).connect() as db: assert db.scalar(text('SELECT value FROM sample WHERE id=1'))=='synthetic'\n")
    git(source.root,'add','.');git(source.root,'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','synthetic candidate')
    template=plan(python_image=os.environ['CANDIDATE_PYTHON_IMAGE'],mysql_image=os.environ['CANDIDATE_MYSQL_IMAGE'],browser_image=os.environ['CANDIDATE_BROWSER_IMAGE'])
    project = Path(__file__).resolve().parents[3]
    sources = [*sorted((project/'src/backend/app/verification').glob('*.py')), project/'src/backend/container/verification_acceptance.cjs', Path(__file__).resolve()]
    hashes = {str(p.relative_to(project)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    supplier=CandidateSupplier(template,tmp_path/'envs')
    result=supplier.validate(candidate_id=str(uuid4()),candidate_commit=source.head(),workspace=source.root,change_id='change',factory=factory,space_id='space',repository_id='repo')
    with factory() as db: row=dict(db.execute(select(environments)).mappings().one())
    report=dict(sample='real-docker-synthetic-project',result=result,cleanup_state=row['cleanup_state'])
    evidence=tmp_path/'envs'/row['id']/'evidence.json'
    if evidence.exists(): report['evidence']=json.loads(evidence.read_text())
    target=os.getenv('MOONBOX_CANDIDATE_REPORT')
    report['source_hashes'] = hashes
    report['source_stable'] = all(hashlib.sha256((project/name).read_bytes()).hexdigest()==value for name,value in hashes.items())
    if target:
        import shutil
        destination=Path(target); destination.parent.mkdir(parents=True,exist_ok=True)
        for index,picture in enumerate(sorted((tmp_path/'envs'/row['id']).rglob('*.png'))):
            shutil.copy2(picture,destination.parent/('candidate-browser-'+str(index)+'.png'))
        destination.write_text(json.dumps(report,indent=2))
    assert report['source_stable']
    assert result['status']=='passed',report
    assert row['cleanup_state']=='clean'
    assert {x['database'] for x in report['evidence']['matrices']}=={'sqlite','mysql'}


def test_reconciler_cleans_owned_interruption_without_replaying(chat,repo,tmp_path,monkeypatch):
    _,factory=chat;source,_=repo
    supplier=CandidateSupplier(plan(),tmp_path/'envs')
    monkeypatch.setattr(DockerEnvironment,'daemon_id',staticmethod(lambda:'synthetic-daemon'))
    monkeypatch.setattr(DockerEnvironment,'run',lambda *_: (_ for _ in ()).throw(RuntimeError('interrupted')))
    monkeypatch.setattr(DockerEnvironment,'cleanup',lambda *_:False)
    request=dict(candidate_id=str(uuid4()),candidate_commit=source.head(),workspace=source.root,change_id='change',factory=factory,space_id='space',repository_id='repo')
    supplier.validate(**request)
    monkeypatch.setattr(DockerEnvironment,'cleanup',lambda *_:True)
    assert supplier.reconcile(factory)==1
    assert supplier.reconcile(factory)==0
    with factory() as db:
        row=db.execute(select(environments)).mappings().one()
        assert row['state']=='interrupted' and row['cleanup_state']=='clean'


def test_manifest_symlink_is_not_followed(repo,tmp_path):
    source,_=repo
    (source.root/'requirements.txt').write_text('fixture-lock\n')
    (source.root/'escape').symlink_to('/etc/passwd')
    git(source.root,'add','.');git(source.root,'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','unsafe link')
    target=tmp_path/'export';target.mkdir()
    with pytest.raises(CandidateError,match='source_unsafe'):
        export_candidate(source.root,source.head(),target,'requirements.txt',plan().data['lock_digest'])


def test_capability_requires_present_pinned_images_with_approved_platform(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from app.verification import candidate
    template=plan(); supplier=CandidateSupplier(template,tmp_path/'envs')
    monkeypatch.setattr(candidate.shutil,'which',lambda _: '/synthetic/docker')
    output={'returncode':1,'stdout':''}
    monkeypatch.setattr(candidate.subprocess,'run',lambda *args,**kwargs: SimpleNamespace(**output))
    assert supplier.capability()['available'] is False
    output.update(returncode=0,stdout='\n'.join(template.data[key]+' linux/arm64' for key in ('python_image','mysql_image','browser_image'))+'\n')
    assert supplier.capability()['available'] is True
    output['stdout']=output['stdout'].replace('linux/arm64','linux/amd64')
    assert supplier.capability()['reason_code']=='candidate_images_unavailable'


def test_controller_does_not_shadow_application_server_module(tmp_path):
    import subprocess
    import sys
    from app.verification.candidate import _SERVER
    source=tmp_path/'source'; source.mkdir()
    control=tmp_path/'control'; control.mkdir()
    (source/'server.py').write_text('app = object()\n')
    (source/'uvicorn.py').write_text('def run(*a, **kw): print("started")\n')
    entry=control/'server.py'
    entry.write_text(_SERVER.replace("plan=json.load(open('/control/plan.json'))", "plan={'app':'server:app','commit':'fixed'}"))
    result=subprocess.run([sys.executable,str(entry)],env={**os.environ,'PYTHONPATH':str(source)},capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert result.stdout.strip()=='started'


def test_capacity_scope_expiry_and_live_lock_are_fail_closed(chat,repo,tmp_path,monkeypatch):
    import time
    from app.verification.candidate import locked
    _,factory=chat; source,_=repo
    supplier=CandidateSupplier(plan(),tmp_path/'envs')
    monkeypatch.setattr(DockerEnvironment,'daemon_id',staticmethod(lambda:'synthetic-daemon'))
    monkeypatch.setattr(DockerEnvironment,'run',lambda *_: {'matrices':[]})
    monkeypatch.setattr(DockerEnvironment,'save_evidence',lambda *_:None)
    monkeypatch.setattr(DockerEnvironment,'cleanup',lambda *_:False)
    request=dict(candidate_id=str(uuid4()),candidate_commit=source.head(),workspace=source.root,change_id='change',factory=factory,space_id='space',repository_id='repo')
    assert supplier.validate(**request)['reason_code']=='candidate_cleanup_pending'
    second={**request,'candidate_id':str(uuid4())}
    assert supplier.validate(**second)['reason_code']=='candidate_capacity_unavailable'
    second['space_id']='other'
    assert supplier.validate(**second)['reason_code']=='candidate_cleanup_pending'
    assert supplier.validate(**{**second,'space_id':'third','candidate_id':str(uuid4())})['reason_code']=='candidate_capacity_unavailable'
    assert supplier.validate(**{**request,'repository_id':'foreign'})['reason_code']=='candidate_environment_stale'
    with locked(supplier.root,'candidate-'+request['candidate_id']):
        assert supplier.validate(**request)['reason_code']=='candidate_environment_busy'
    with factory.begin() as db:
        db.execute(update(environments).values(cleanup_state='clean',state='failed',expires_at=int(time.time())-1))
    assert supplier.validate(**request)['reason_code']=='candidate_environment_expired'


def test_candidate_and_chat_acceptance_share_slots_and_space_limit(chat,repo,tmp_path,monkeypatch):
    import time
    from app.verification.acceptance_resources import reserve,release,GIB
    _,factory=chat;source,_=repo
    limits=dict(available_cpu=16,available_memory=32*GIB,available_disk=100*GIB,hard_disk_limit=True)
    first=dict(id='acceptance-one',space_id='space',expires_at=int(time.time())+600)
    second=dict(id='acceptance-two',space_id='second',expires_at=int(time.time())+600)
    reserve(factory,first,**limits);reserve(factory,second,**limits)
    monkeypatch.setattr(DockerEnvironment,'daemon_id',staticmethod(lambda:'synthetic-daemon'))
    monkeypatch.setattr(DockerEnvironment,'run',lambda *_:{'matrices':[]})
    monkeypatch.setattr(DockerEnvironment,'cleanup',lambda *_:True)
    monkeypatch.setattr(DockerEnvironment,'save_evidence',lambda *_:None)
    supplier=CandidateSupplier(plan(),tmp_path/'envs')
    request=dict(candidate_id=str(uuid4()),candidate_commit=source.head(),workspace=source.root,
                 change_id='change',factory=factory,space_id='third',repository_id='repo')
    assert supplier.validate(**request)['reason_code']=='candidate_capacity_unavailable'
    release(factory,second['id'],resources_confirmed_absent=True)
    assert supplier.validate(**{**request,'space_id':'space'})['reason_code']=='candidate_capacity_unavailable'
    assert supplier.validate(**request)['status']=='passed'
