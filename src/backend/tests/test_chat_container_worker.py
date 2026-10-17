"""适配器接入真实claim执行链路；本地凭证仅用于显式隔离测试。"""
import json
import os
from pathlib import Path
import subprocess
import pytest
from sqlalchemy import select
from test_chat import chat, create, governance, allow_governed_write
from test_chat_local_execution import LIMITS
from app.chat import worker
from app.chat.admission import enqueue
from app.chat.execution import run_claim
from app.chat.container_server import persistent_container_server
from app.chat.schema import reservations


@pytest.mark.skipif(os.environ.get('CHAT_CONTAINER_PROBE') != '1', reason='Explicit offline Docker toolchain probe')
def test_governance_openspec_commands_in_real_sandbox(tmp_path):
    work = tmp_path.resolve() / 'work'; work.mkdir()
    for directory in ('.git', 'issues', 'iterations', 'docs/spec-logs',
                      'openspec/changes', 'openspec/specs', 'openspec/archive'):
        (work / directory).mkdir(parents=True, exist_ok=True)
    (work / 'openspec/config.yaml').write_text('schema: spec-driven\n')
    runtime = tmp_path.resolve() / 'runtime'; runtime.mkdir(mode=0o700)
    auth = tmp_path / 'auth.json'; auth.write_text('{"OPENAI_API_KEY":"synthetic-invalid-key"}'); auth.chmod(0o600)
    # Use the same factory, profiles and non-root container as product claims, without a model call.
    with persistent_container_server(work, runtime, auth) as server:
        def cli(*args, profile='moonbox-governance'):
            result = subprocess.run([server.docker, 'exec', server.container_name,
                'codex', 'sandbox', '-P', profile, '-C', '/work', '/usr/bin/env',
                'HOME=/tmp', 'OPENSPEC_TELEMETRY=0', 'DO_NOT_TRACK=1', 'openspec', *args],
                capture_output=True, text=True, timeout=30)
            assert result.returncode == 0, result.stderr
            return result.stdout
        cli('new', 'change', 'verify-toolchain')
        status = json.loads(cli('status', '--change', 'verify-toolchain', '--json'))
        assert status['changeName'] == 'verify-toolchain'
        assert json.loads(cli('instructions', 'proposal', '--change', 'verify-toolchain', '--json'))['artifactId'] == 'proposal'
        change = work / 'openspec/changes/verify-toolchain'
        (change / 'specs/executor').mkdir(parents=True)
        (change / 'proposal.md').write_text('## Why\nTools are required.\n## What Changes\nInclude tools.\n## Capabilities\n### New Capabilities\n- executor: toolchain\n### Modified Capabilities\nNone.\n## Impact\nExecutor image.\n')
        (change / 'specs/executor/spec.md').write_text('## ADDED Requirements\n### Requirement: Tool availability\nThe executor SHALL provide OpenSpec.\n#### Scenario: Offline execution\n- **WHEN** a command starts\n- **THEN** tools are available\n')
        cli('validate', 'verify-toolchain', '--strict')
        assert 'verify-toolchain' in cli('list', '--json', profile='moonbox-read')
        probe = subprocess.run([server.docker, 'exec', server.container_name,
            'codex', 'sandbox', '-P', 'moonbox-archive', '-C', '/work',
            'python', '-c',
            "import json; from pathlib import Path; "
            "parents=('issues','iterations','openspec/changes','openspec/specs','openspec/archive','docs/spec-logs'); "
            "print(json.dumps({f'{parent}/{name}': (Path('/work')/parent/name).is_dir() "
            "and not any((Path('/work')/parent/name).iterdir()) "
            "for parent in parents for name in ('.agents','.codex')}))"],
            capture_output=True, text=True, timeout=30)
        assert probe.returncode == 0, probe.stderr
        assert all(json.loads(probe.stdout).values())
    assert (change / 'proposal.md').is_file()
    from app.chat.execution import _check_workspace_tool_dirs_outside_sandbox
    _check_workspace_tool_dirs_outside_sandbox(work)
    assert not any((work / parent / name).exists() for parent in
                   ('issues', 'iterations', 'openspec/changes', 'openspec/specs',
                    'openspec/archive', 'docs/spec-logs') for name in ('.agents', '.codex'))


@pytest.mark.skipif(os.environ.get('CHAT_CONTAINER_PROBE')!='1',reason='Explicit synthetic Docker probe')
def test_container_factory_preflight_two_private_sessions(tmp_path):
    runtime=tmp_path.resolve()/'runtime';runtime.mkdir(mode=0o700)
    source=tmp_path.resolve()/'auth.json';source.write_text('{"OPENAI_API_KEY":"synthetic-invalid-key"}');source.chmod(0o600)
    names=[]
    for index in range(2):
        work=tmp_path.resolve()/str(index);work.mkdir(mode=0o700)
        (work/'.git').mkdir();(work/'write-probe').write_text('preserve existing file')
        with persistent_container_server(work,runtime,source) as server:
            names.append(server.container_name)
        assert (work/'write-probe').read_text()=='preserve existing file'
    assert len(set(names))==2
    assert len(list(runtime.iterdir()))==2


@pytest.mark.skipif(os.environ.get('CHAT_LIVE_ISOLATED_PROBE')!='1',reason='Explicit disposable real container execution only')
def test_container_worker_claim_diff_and_accounting(chat,tmp_path,governance):
    client,factory=chat;cid=create(client);allow_governed_write(client,cid,governance)
    work=tmp_path.resolve()/cid;work.mkdir(mode=0o700)
    runtime=tmp_path.resolve()/'runtime';runtime.mkdir(mode=0o700)
    subprocess.run(['git','init','-q',str(work)],check=True)
    (work/'counter.txt').write_text('0\n')
    with factory() as db:
        row=enqueue(db,'alice',cid,'container-claim','Set counter.txt to exactly 1 followed by newline. Modify no other files. Do not commit. Reply done.',LIMITS)
        token=worker.claim(db,'container-test')
    def server(path):return persistent_container_server(path,runtime,Path.home()/'.codex/auth.json')
    try:
        assert run_claim(factory,token,work,server,max_seconds=180)=='completed'
        assert (work/'counter.txt').read_text()=='1\n'
        diff=client.get(f"/api/v1/chat/turns/{row['id']}/diff").json()['data']
        assert '-0\n+1\n' in diff['files'][0]['patch']
        with factory() as db:
            receipt=db.execute(select(reservations).where(reservations.c.turn_id==row['id'])).mappings().one()
            if receipt['actual_tokens'] is None:assert receipt['status']=='reserved'
            else:assert receipt['status']=='settled' and receipt['actual_tokens']>0
        report={'real_container_claim':True,'file_changed':True,'diff_persisted':True,'accounting_status':receipt['status'],'actual_tokens':receipt['actual_tokens']}
    finally:
        import shutil
        shutil.rmtree(runtime)
        shutil.rmtree(work)
    report['temporary_runtime_removed']=not runtime.exists()
    Path('/tmp/moonbox-container-worker.json').write_text(json.dumps(report,indent=2)+'\n')


@pytest.mark.skipif(os.environ.get('CHAT_LIVE_ISOLATED_PROBE')!='1', reason='Explicit disposable real BUG apply execution only')
def test_bug_alias_apply_writes_source_with_same_turn_permission_event(chat,tmp_path,governance):
    from app.chat.schema import events
    client,factory=chat
    root,_=governance
    oid='BUG-0029-synthetic'; change='fix-chat-workbench-nonempty-page-scroll'; sprint='sprint-999'
    folder=root/f'issues/bugs/review/{oid}';folder.mkdir(parents=True)
    (folder/'bug.md').write_text('受控 BUG：仅修改 counter.txt。')
    registry=root/'issues/bugs/_registry.yaml';registry.parent.mkdir(parents=True,exist_ok=True)
    registry.write_text(json.dumps({'entries':[{'id':oid,'title':'受控源码写入','path':f'issues/bugs/review/{oid}',
        'status':'in_sprint','related_change':change,'iteration':sprint}]}))
    trace=root/'openspec/changes'/change/'trace.md';trace.parent.mkdir(parents=True)
    trace.write_text(f'---\nstatus: in_progress\nbug_id: {oid}\niteration: {sprint}\n---\n')
    plan=root/'iterations/change'/sprint/'sprint.yaml';plan.parent.mkdir(parents=True)
    plan.write_text(json.dumps({'changes':[change],'bugs':[oid]}))
    cid=create(client)
    assert client.put(f'/api/v1/chat/conversations/{cid}/relations',json={'primary':oid}).status_code==200
    work=tmp_path.resolve()/cid;work.mkdir(mode=0o700)
    runtime=tmp_path.resolve()/'runtime';runtime.mkdir(mode=0o700)
    subprocess.run(['git','init','-q',str(work)],check=True)
    (work/'counter.txt').write_text('0\n')
    with factory() as db:
        row=enqueue(db,'alice',cid,'bug-apply','Set counter.txt to exactly 1 followed by newline. Modify no other files. Do not commit. Reply done.',LIMITS)
        token=worker.claim(db,'bug-apply-test')
    def server(path):return persistent_container_server(path,runtime,Path.home()/'.codex/auth.json')
    try:
        assert run_claim(factory,token,work,server,max_seconds=180)=='completed'
        assert (work/'counter.txt').read_text()=='1\n'
        with factory() as db:
            payloads=[json.loads(value) for value in db.scalars(select(events.c.payload).where(events.c.turn_id==row['id']))]
        decisions=[item['permission_decision'] for item in payloads if 'permission_decision' in item]
        assert any(item['write_scope']=='implementation_write' and item['selected_profile']=='moonbox-write' for item in decisions)
        assert any(item['phase']=='acknowledged' and item['acknowledged_profile']=='moonbox-write' for item in decisions)
        assert all(item['turn_id']==row['id'] for item in decisions)
    finally:
        import shutil
        shutil.rmtree(runtime)
        shutil.rmtree(work)


@pytest.mark.skipif(os.environ.get('CHAT_LIVE_ISOLATED_PROBE')!='1',reason='Explicit real usage scope probe')
def test_resumed_container_usage_matches_process_total(chat,tmp_path):
    from app.chat.schema import conversations
    client,factory=chat;cid=create(client)
    work=tmp_path.resolve()/cid;work.mkdir(mode=0o700);(work/'.git').mkdir()
    runtime=tmp_path.resolve()/'runtime';runtime.mkdir(mode=0o700)
    totals=[];settled=[];threads=[]
    def server(path):
        adapter=persistent_container_server(path,runtime,Path.home()/'.codex/auth.json')
        read=adapter.event
        def event(timeout):
            value=read(timeout)
            if value and value.get('method')=='thread/tokenUsage/updated':
                total=value.get('params',{}).get('tokenUsage',{}).get('total',{}).get('totalTokens')
                if type(total) is int:totals[-1].append(total)
            return value
        adapter.event=event;return adapter
    try:
        for index in range(2):
            totals.append([])
            with factory() as db:
                row=enqueue(db,'alice',cid,f'scope-{index}','Reply exactly OK. Do not use tools or read files.',LIMITS)
                token=worker.claim(db,'scope-test')
            assert run_claim(factory,token,work,server,max_seconds=120)=='completed'
            with factory() as db:
                value=db.scalar(select(reservations.c.actual_tokens).where(reservations.c.turn_id==row['id']))
                assert totals[-1] and value==max(totals[-1])
                settled.append(value);threads.append(db.scalar(select(conversations.c.thread_id).where(conversations.c.id==cid)))
        assert threads[0]==threads[1]
    finally:
        import shutil
        shutil.rmtree(runtime);shutil.rmtree(work)
    Path('/tmp/moonbox-token-scope-integration.json').write_text(json.dumps({'same_thread':True,'raw_process_totals':totals,'settled_tokens':settled,'temporary_runtime_removed':not runtime.exists()},indent=2)+'\n')
