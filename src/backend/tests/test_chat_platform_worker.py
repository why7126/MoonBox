"""显式真实常驻 Worker 探针：临时SQLite和仓库，不触碰正式数据。"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import uuid
import pytest
from sqlalchemy import select
from test_chat import chat, create
from test_chat_unlimited import unlimited
from app.chat import service
from app.chat.backup import LocalBackupStore
from app.chat.platform import allowed
from app.chat.schema import turns, reservations


@pytest.mark.skipif(os.environ.get('CHAT_LIVE_PLATFORM_PROBE')!='1',reason='explicit live platform probe')
def test_real_container_worker_restart_and_unlimited_accounting(chat,tmp_path,monkeypatch):
    client,factory=chat;root=tmp_path.resolve()
    for name in ('seed','runtime','state','workspaces','backups','governance'): (root/name).mkdir(mode=0o700)
    source=root/'seed';(source/'counter.txt').write_text('0\n')
    envgit={'PATH':'/usr/bin:/bin','HOME':'/nonexistent','GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':'/dev/null'}
    for args in (['init','-q',str(source)],['-C',str(source),'add','counter.txt'],['-C',str(source),'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','seed']):
        subprocess.run(['git',*args],check=True,capture_output=True,env=envgit)
    auth=root/'auth.json'
    with (Path.home()/'.codex/auth.json').open('rb') as reader,auth.open('xb') as writer:
        auth.chmod(0o600);shutil.copyfileobj(reader,writer)
    LocalBackupStore(root/'backups',initialize=True)
    with factory() as db: database=str(db.get_bind().url)
    values={'APP_ENV':'local','DATABASE_TYPE':'sqlite','DATABASE_URL':database,'SQLITE_DATABASE_URL':database,
        'MOONBOX_CHAT_EXECUTION_MODE':'local-codex','MOONBOX_CHAT_STATE_ROOT':str(root/'state'),
        'MOONBOX_CHAT_RUNTIME_ROOT':str(root/'runtime'),'MOONBOX_CHAT_AUTH_FILE':str(auth),
        'MOONBOX_CHAT_BACKUP_ROOT':str(root/'backups'),
        'MOONBOX_CHAT_REPOSITORIES':json.dumps([{'id':'repo','space_id':'space'}]),
        'MOONBOX_CHAT_REPOSITORY_BINDINGS':json.dumps([{'id':'repo','space_id':'space','source_root':str(source),'workspace_root':str(root/'workspaces'),'governance_root':str(root/'governance')}]),
        'MOONBOX_CHAT_RETENTION':json.dumps({'executor_delete_seconds':'unlimited','backup_expiry_seconds':'unlimited'})}
    unlimited(monkeypatch); values['MOONBOX_CHAT_LIMITS']=os.environ['MOONBOX_CHAT_LIMITS']
    for key,value in values.items(): monkeypatch.setenv(key,value)
    name='moonbox-platform-probe-'+uuid.uuid4().hex[:12]
    command=['docker','run','-d','--name',name,'--user',f'{os.getuid()}:{os.getgid()}','--group-add','0',
             '--mount',f'type=bind,src={root},dst={root}', '--mount','type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock']
    for key,value in values.items():command+=['--env',key+'='+value]
    command+=['moonbox-chat-worker:verify']
    report={'real_worker_container':True,'quota_mode':'unlimited','rounds':[]}
    try:
        subprocess.run(command,check=True,capture_output=True)
        def wait_ready():
            deadline=time.monotonic()+100
            while time.monotonic()<deadline:
                with factory() as db:
                    if allowed(db,'alice','space','repo'): return
                state=subprocess.run(['docker','inspect','--format','{{.State.Running}}',name],capture_output=True,text=True)
                if state.stdout.strip()!='true':break
                time.sleep(.5)
            result=subprocess.run(['docker','logs',name],capture_output=True,text=True)
            # Worker logs have only a stable redacted failure message.
            pytest.fail('worker did not become ready: '+result.stdout[-200:]+result.stderr[-200:])
        wait_ready();cid=create(client)
        for round_id in range(2):
            if round_id:
                subprocess.run(['docker','restart','--time','90',name],check=True,capture_output=True);wait_ready()
            result=client.post(f'/api/v1/chat/conversations/{cid}/turns',json={'client_request_id':str(round_id),'prompt':'Reply with OK only. Do not modify files.'})
            assert result.status_code==200;tid=result.json()['data']['id']
            deadline=time.monotonic()+150
            while time.monotonic()<deadline:
                with factory() as db:row=db.execute(select(turns).where(turns.c.id==tid)).mappings().one()
                if row['status'] in service.TERMINAL or row['status']=='unknown':break
                time.sleep(.5)
            assert row['status']=='completed',row['error_code']
            with factory() as db:
                receipt=db.execute(select(reservations).where(reservations.c.turn_id==tid)).mappings().one()
                assert receipt['status']=='settled' and receipt['tokens']==0 and receipt['actual_tokens']>0
                report['rounds'].append({'status':row['status'],'tokens':receipt['actual_tokens'],'settled':True})
        with factory() as db:assert len(list(db.scalars(select(turns.c.id))))==2
        report['restart_without_replay']=True
        assert (source/'counter.txt').read_text()=='0\n'
        report['source_unchanged']=True
        store=LocalBackupStore(root/'backups')
        with factory() as db: backup_id=store.create(Path(db.get_bind().url.database))
        verdict=client.get(f'/api/v1/chat/conversations/{cid}/deletion-check').json()['data']
        assert verdict['allowed'],verdict['reason']
        deleted=client.delete(f'/api/v1/chat/conversations/{cid}',params={'expected_hash':verdict['workspace_hash']})
        assert deleted.status_code==200
        restored=root/'offline.sqlite';store.restore(backup_id,restored)
        import sqlite3
        with sqlite3.connect(restored) as copy:
            assert copy.execute('SELECT COUNT(*) FROM chat_turns WHERE conversation_id=?',(cid,)).fetchone()[0]==0
        assert not store.copies_cleared(cid)
        with sqlite3.connect(store.ledger) as ledger: backups=[row[0] for row in ledger.execute('SELECT id FROM backups')]
        for backup in backups:store.expire(backup)
        deadline=time.monotonic()+90
        while time.monotonic()<deadline:
            status=client.get(f'/api/v1/chat/conversations/{cid}/cleanup').json()['data']
            if status['executor_status']=='purged' and status['backup_status']=='purged':break
            time.sleep(1)
        assert status['executor_status']=='purged' and status['backup_status']=='purged',status
        assert status['executor_due_at'] is None and status['backup_due_at'] is None
        assert (root/'workspaces'/cid/'counter.txt').read_text()=='0\n'
        report['delete_restore_no_resurrection']=True
        report['executor_and_explicit_backup_cleanup']=True
    finally:
        subprocess.run(['docker','rm','-f',name],capture_output=True)
        auth.unlink(missing_ok=True)
        shutil.rmtree(root/'runtime')
        report['credential_copies_removed']=True
        Path('/tmp/moonbox-platform-worker-verification.json').write_text(json.dumps(report))
