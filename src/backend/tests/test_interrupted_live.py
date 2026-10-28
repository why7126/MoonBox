"""Opt-in isolated product interruption, external CLI completion and real follow-up."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import pytest
from sqlalchemy import select
from test_chat import chat, create
from test_governance_writer import writing
from test_direct_completion import files, OID, BASE, CHANGE, md


@pytest.mark.skipif(os.environ.get('CHAT_LIVE_ISOLATED_PROBE') != '1', reason='isolated live opt-in')
def test_interrupted_live_chain(writing, chat, tmp_path, monkeypatch):
    from app.chat import worker
    from app.chat.execution import run_claim
    from app.chat.local_probe import local_executor
    from app.chat.schema import turns, events
    from app.governance import store, execution_guard as guards
    from app.governance.direct_command_journal import record_id
    factory, project, *_ = writing
    client, _ = chat
    for path in project.root.rglob('*'):
        if path.is_file(): path.unlink()
    for name, body in files().items():
        path = project.root/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(body)
    folder = project.root/'openspec/changes'/CHANGE
    for name in ('sprint.md','release-note.md','acceptance-report.md'):
        (project.root/'iterations/change/sprint-012'/name).write_text('# 隔离迭代样本\n')
    (project.root/BASE/'bug.md').write_bytes(md(bug_id=OID,status='in_sprint',title='隔离中断样本',severity='high'))
    (project.root/BASE/'trace.md').write_bytes(md(bug_id=OID,status='in_sprint',iteration='sprint-012',openspec_changes=[{'change_id':CHANGE,'status':'proposed'}]))
    (project.root/BASE/'root-cause.md').write_text('---\nstatus: confirmed\n---\n# 隔离样本机制\n\n## 证据链\n\n| id | type | source | 摘要 |\n|---|---|---|---|\n| E1 | code_path | app/chat/service.py interrupt | 排队停止不执行同步命令；本测试随后用真实接口观察该行为 |\n')
    (folder/'trace.md').write_bytes(md(change_id=CHANGE,status='proposed',bug_id=OID,iteration='sprint-012',execution=dict(schema_version=1,started_at=None,completed_at=None,last_event='bug.opsx')))
    (project.root/BASE/'acceptance.md').write_bytes(md(acceptance_status='not_started')+b'\n- [x] AC-001 sample\n')
    source = Path(__file__).resolve().parents[3]
    for relative in ('scripts', 'src/backend/app'):
        shutil.copytree(source/relative, project.root/relative, ignore=shutil.ignore_patterns('__pycache__'), dirs_exist_ok=True)
    (project.root/'scripts/sample-check.py').write_text("from pathlib import Path\nassert '- [x] task' in Path('openspec/changes/fix-sample/tasks.md').read_text()\nprint('sample delivered')\n")
    inputs = [str(p.relative_to(project.root)) for p in project.root.rglob('*.md')
              if str(p.relative_to(project.root)).startswith((BASE+'/', 'openspec/changes/'+CHANGE+'/')) and p.name not in ('trace.md','tasks.md')]
    inputs.append('issues/bugs/_registry.yaml')
    (folder/'acceptance-plan.json').write_text(json.dumps(dict(schema_version=1,change_id=CHANGE,issue_id=OID,checks=[dict(id='AC-001',kind='command',inputs=inputs,argv=['bash','scripts/project-python.sh','scripts/sample-check.py'])])))
    monkeypatch.setattr('app.chat.isolated.allowed', lambda *a: True)
    cid = create(client)
    response = client.post(f'/api/v1/chat/conversations/{cid}/turns',json={'client_request_id':'interrupted-live','prompt':'/opsx-apply '+OID})
    assert response.status_code == 200, response.text
    tid = response.json()['data']['id']
    stopped = client.post(f'/api/v1/chat/turns/{tid}/interrupt')
    assert stopped.status_code == 200 and stopped.json()['data']['status'] == 'stopped', stopped.text
    rid = record_id(cid, 'interrupted-live')
    before = store.read(rid, 'operation')
    assert not any(s.get('sync_succeeded') for s in before['steps'])
    with factory() as db:
        history = list(db.execute(select(events).where(events.c.turn_id == tid)).mappings())
    env = {**os.environ,'PYTHON_BIN':sys.executable}
    def cli(*args):
        result = subprocess.run(['bash','scripts/project-python.sh',*args],cwd=project.root,env=env,text=True,capture_output=True)
        assert result.returncode == 0, result.stdout+result.stderr
    cli('scripts/sync-workflow-status.py','--event','opsx.start','--change',CHANGE,'--sprint','auto')
    (folder/'tasks.md').write_text('- [x] task')
    cli('scripts/sync-workflow-status.py','--event','opsx.apply','--change',CHANGE,'--sprint','auto')
    cli('scripts/opsx_acceptance.py','--change',CHANGE)
    cli('scripts/sync-workflow-status.py','--event','opsx.accept','--change',CHANGE,'--sprint','auto')
    url = f'/api/v1/chat/turns/{tid}/completion-verification'
    state = client.get(url).json()['data']
    verified = client.post(url,json={'expected_version':state['version']})
    assert verified.status_code == 200, verified.text
    assert store.read(rid,'operation')['steps'] == before['steps']
    with factory() as db:
        assert list(db.execute(select(events).where(events.c.turn_id == tid)).mappings()) == history
        assert db.scalar(select(turns.c.status).where(turns.c.id == tid)) == 'stopped'
    follow = client.post(f'/api/v1/chat/conversations/{cid}/turns',json={'client_request_id':'successor-followup','prompt':'Reply exactly: successor completion verified. Do not use tools or modify files.'})
    assert follow.status_code == 200, follow.text
    work = tmp_path.resolve()/cid; work.mkdir()
    subprocess.run(['git','init','-q',str(work)],check=True)
    with factory() as db: token = worker.claim(db,'successor-live')
    with local_executor([work], executable=os.environ.get('BUG0069_CODEX_BIN') or shutil.which('codex'), auth_source=Path.home()/'.codex/auth.json') as (server, auth_home):
        terminal = run_claim(factory,token,work,server,max_seconds=120)
    result={'passed':terminal=='completed','original_turn_id':tid,'followup_turn_id':follow.json()['data']['id'],'original_status':'stopped','original_queued_interruption':True,'original_model_started':False,'external_standard_cli':True,'verification_http':verified.status_code,'send_http':follow.status_code,'followup_status':terminal,'real_executor':True,'history_preserved':True,'temporary_auth_removed':not auth_home.exists(),'database':factory.kw['bind'].dialect.name,'successor_evidence':verified.json()['data']['successor_evidence']}
    destination=os.environ.get('BUG0069_LIVE_EVIDENCE')
    if destination: Path(destination).write_text(json.dumps(result,indent=2)+'\n')
    assert terminal == 'completed', result
