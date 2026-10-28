"""Explicit isolated Docker proof, synthetic credentials, no model call or production data."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import uuid
import pytest
from sqlalchemy import select
from test_chat import chat
from test_chat_unknown_recovery import sample, get
from app.chat import recovery, recovery_runtime
from app.chat.container_server import persistent_container_server, ContainerAppServer
from app.chat.recovery_worker import execute
from app.chat.settings import recovery_policy

pytestmark=pytest.mark.skipif(os.environ.get('CHAT_RECOVERY_DOCKER_PROBE')!='1',reason='explicit registered Docker probe')


def test_registered_docker_recovery_and_quiet_period(chat,tmp_path,monkeypatch):
    from chat_recovery_evidence import fingerprint
    input_fingerprint=fingerprint()
    run=os.environ['CHAT_RECOVERY_TEMP_RUN'];expires=os.environ['CHAT_RECOVERY_TEMP_EXPIRES']
    original=recovery_runtime.Runtime.labels
    def labels(self):
        return original(self)+['--label','moonbox.temp.managed=true','--label','moonbox.temp.run='+run,'--label','moonbox.temp.expires='+expires]
    monkeypatch.setattr(recovery_runtime.Runtime,'labels',labels)
    factory,tid,path=sample(chat,tmp_path);(path/'.git').mkdir()
    runtime=tmp_path/'runtime';runtime.mkdir(mode=0o700)
    auth=tmp_path/'auth.json';auth.write_text('{"OPENAI_API_KEY":"synthetic-invalid-key"}');auth.chmod(0o600)
    def server(workspace):return persistent_container_server(workspace,runtime,auth)
    policy={**recovery_policy(),'attempts':2,'base_seconds':10,'cap_seconds':60}
    errors=[]
    original_classify=recovery.classify
    def classify(error):
        errors.append(type(error).__name__ + ':' + str(getattr(error,'code','')))
        return original_classify(error)
    monkeypatch.setattr(recovery,'classify',classify)
    started=time.time();reports=[]
    for _ in range(2):
        deadline=time.monotonic()+120
        lease=None
        while lease is None and time.monotonic()<deadline:
            with factory() as db:lease=recovery.claim(db,policy)
            if lease is None:time.sleep(.5)
        assert lease is not None
        execute(factory,lease,lambda _: (None,path),server,policy)
        row=get(factory,tid);reports.append({key:row[key] for key in ('state','attempt_count','last_result')})
    assert reports[-1]['state']=='paused',reports
    assert reports[-1]['last_result']=='rpc_rejected',(reports,errors)
    key=hashlib.sha256(tid.encode()).hexdigest()
    def events(since):
        result=subprocess.run(['docker','events','--since',str(since),'--until',str(time.time()),
            '--filter','label=moonbox.chat.recovery='+key,'--format','{{.Action}}'],capture_output=True,text=True,timeout=10)
        assert result.returncode==0
        return result.stdout.splitlines()
    first=events(started);assert first.count('create')>=3 and first.count('create')==first.count('destroy')
    quiet_start=time.time();deadline=time.monotonic()+330
    while time.monotonic()<deadline:
        with factory() as db:assert recovery.claim(db,policy) is None
        time.sleep(1)
    assert events(quiet_start).count('create')==0
    # Real app-server normal close and exception close; initialization does not invoke a model.
    close_cases=[]
    for mode in ('success','failure','cancel'):
        case_tid='docker-'+mode
        with recovery_runtime.scope(case_tid) as context:
            try:
                with server(path) as adapter:
                    assert adapter.process.poll() is None
                    if mode=='failure':raise RuntimeError('synthetic')
                    if mode=='cancel':raise KeyboardInterrupt()
            except (RuntimeError,KeyboardInterrupt):pass
            context.cleanup();context.collect_metrics()
            assert context.metrics['containers_created']>=1
            assert context.metrics['containers_created']==context.metrics['containers_removed']
            close_cases.append(mode)
    # Orphan from interrupted controller is fenced by exact turn label and removed before retry.
    with recovery_runtime.scope('interrupted',lease_token='old') as old:
        result=subprocess.run(['docker','run','-d','--rm',*old.labels(),'alpine:3.20','sleep','120'],capture_output=True,text=True,timeout=20)
        assert result.returncode==0
    with recovery_runtime.scope('interrupted',lease_token='new') as current:current.cleanup(stale=True)
    with recovery_runtime.scope('timeout',seconds=.5) as context:
        with pytest.raises((subprocess.TimeoutExpired, recovery_runtime.ExecutorError)):
            recovery_runtime.run(['docker','run','--rm',*context.labels(),'alpine:3.20','sleep','120'],capture_output=True,timeout=60)
        context.cleanup()
    result=subprocess.run(['docker','ps','-aq','--filter','label=moonbox.temp.run='+run,'--filter','label=moonbox.chat.recovery='+key],capture_output=True,text=True,timeout=10)
    assert result.returncode==0 and not result.stdout.strip()
    assert fingerprint()==input_fingerprint
    report={'input_fingerprint':input_fingerprint,'environment':'isolated-real-docker','model_calls':0,'attempts':reports,'quiet_seconds':330,
            'quiet_creates':0,'attempt_containers_created':first.count('create'),'attempt_containers_destroyed':first.count('destroy'),
            'close_cases':close_cases,'interrupted_cleanup':True,'runtime':'current-host-source',
            'image_id':subprocess.run(['docker','image','inspect','--format','{{.Id}}',ContainerAppServer.IMAGE],capture_output=True,text=True,check=True).stdout.strip()}
    evidence=Path(os.environ['CHAT_RECOVERY_DOCKER_REPORT']);evidence.parent.mkdir(parents=True,exist_ok=True)
    report['source_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('app/chat').glob('recovery*.py')}
    evidence.write_text(json.dumps(report,indent=2)+'\n')
