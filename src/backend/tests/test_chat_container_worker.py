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
