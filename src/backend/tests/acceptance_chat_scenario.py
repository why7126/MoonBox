"""Explicit fault probes against the local disposable product API, no DB state injection."""
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import uuid
from urllib.request import Request,urlopen
from urllib.error import HTTPError


def main():
    root=Path(os.environ['MOONBOX_CHAT_TEST_ROOT']).resolve()
    if root.parent!=Path('/private/tmp') or not root.name.startswith('moonbox-chat-e2e-'):
        raise RuntimeError('isolated_root_required')
    mode=sys.argv[1]
    if mode not in {'executor-loss','cleanup-failure','visual-stages','application-loss','failed-source','acl','revocation'}:raise ValueError('invalid_scenario')
    browser=json.loads((root/'browser.json').read_text())
    base='http://127.0.0.1:39048'
    token=None
    def api(path,data=None,method=None):
        headers={'Content-Type':'application/json'}
        if token:headers['Authorization']='Bearer '+token
        request=Request(base+path,data=json.dumps(data).encode() if data is not None else None,headers=headers,method=method)
        with urlopen(request,timeout=30) as response:return json.load(response)['data']
    token=api('/api/v1/auth/login',{'username':browser['username'],'password':browser['password']})['access_token']
    ids=json.loads((root/'ids.json').read_text())
    if mode=='acl':
        operation=api('/api/v1/chat/conversations/'+ids['conversation_id']+'/acceptance-operations')['items'][0]
        token=api('/api/v1/auth/login',{'username':'bob','password':browser['password']})['access_token']
        observed=[]
        prefix='/api/v1/chat/acceptance-operations/'+operation['id']
        for path,data in [(prefix,None),(prefix+'/evidence',None),(prefix+'/evidence/archive',None),
                          (prefix+'/stop',{'version':operation['version']})]:
            try:api(path,data)
            except HTTPError as error:observed.append(error.code)
            else:raise AssertionError('cross_actor_access_allowed')
        assert all(code in {403,404} for code in observed),observed
        token=api('/api/v1/auth/login',{'username':browser['username'],'password':browser['password']})['access_token']
        after=api(prefix)
        assert after['version']==operation['version'] and after['status']==operation['status']
        report=dict(scenario='acl',operation_id=operation['id'],unauthorized_statuses=observed,version_unchanged=True)
        (root/'acl.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
        return
    request_id=mode+'-'+uuid.uuid4().hex[:12]
    chat=api('/api/v1/chat/workspaces/sessions',dict(space_id=browser.get('space_id','space'),repository_id='repo',workspace_id=ids['workspace_id'],request_id=request_id))
    api('/api/v1/chat/conversations/'+chat['id']+'/relations',dict(primary='REQ-9001-local-moonbox-acceptance',references=[]),'PUT')
    prompt=('这是本机隔离验收测试。不要调用工具、不要修改文件。若消息包含隔离验收结果，直接用中文报告该结果，否则简短回复已准备好。'
            if mode=='failed-source' else '这是本机隔离验收测试。调用 moonbox_acceptance 一次，等待结果后简述结果及回收情况，不执行 shell、不修改文件。若本轮消息已包含隔离验收结果，则直接汇报该结果，不重复调用工具。')
    turn=api('/api/v1/chat/conversations/'+chat['id']+'/turns',dict(client_request_id=request_id,prompt=prompt))
    print(json.dumps({'scenario':mode,'conversation':chat['id'],'turn':turn['id']}),flush=True)
    database=sqlite3.connect('file:'+str(root/'chat.db')+'?mode=ro',uri=True)
    database.row_factory=sqlite3.Row
    if mode=='failed-source':
        # Corrupt only this disposable turn's private journal. The actual product
        # completion guard must derive failure; never inject a terminal DB row.
        record=str(uuid.uuid5(uuid.NAMESPACE_URL,'moonbox.command-baseline.v1:'+chat['id']+':'+request_id))
        fault=root/'private'/record;fault.mkdir(mode=0o700)
        (fault/'operation.json').write_text('{}');(fault/'operation.json').chmod(0o600)
        deadline=time.time()+180
        while time.time()<deadline:
            original=database.execute('SELECT status,error_code FROM chat_turns WHERE id=?',(turn['id'],)).fetchone()
            receipt=database.execute('SELECT executor_closed,files_collected FROM moonbox_execution_receipts WHERE turn_id=?',(turn['id'],)).fetchone()
            if original['status']=='failed' and receipt and all(receipt):break
            time.sleep(.5)
        if original['status']!='failed' or original['error_code']!='direct_command_operation_invalid':
            raise RuntimeError('real_completion_guard_failure_not_observed')
        operation=api('/api/v1/chat/acceptance-operations',dict(conversation_id=chat['id'],source_turn_id=turn['id'],
            change_id='local-moonbox-acceptance',client_request_id=request_id))
        deadline=time.time()+600
        while time.time()<deadline:
            linked=database.execute('SELECT d.target_turn_id,t.status FROM verification_result_deliveries d JOIN chat_turns t ON t.id=d.target_turn_id WHERE d.operation_id=?',(operation['id'],)).fetchone()
            if linked and linked['status'] in {'completed','failed','stopped','unknown'}:break
            time.sleep(1)
        if not linked:raise RuntimeError('continuation_not_observed')
        report=dict(scenario=mode,conversation_id=chat['id'],source_turn_id=turn['id'],operation_id=operation['id'],
            fault='private_journal_invalid',source_status=original['status'],source_error=original['error_code'],
            target_turn_id=linked['target_turn_id'],target_status=linked['status'],database_rows_injected=False)
        (root/(mode+'.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
        return
    deadline=time.time()+180
    operation=None
    while time.time()<deadline:
        operation=database.execute('SELECT * FROM verification_operations WHERE source_turn_id=?',(turn['id'],)).fetchone()
        if operation and operation['status']=='running':break
        time.sleep(.5)
    if not operation or operation['status']!='running':raise RuntimeError('real_operation_not_running')
    run=os.environ['MOONBOX_TEMP_RUN'];expires=os.environ['MOONBOX_TEMP_EXPIRES']
    peer=None
    if mode=='revocation':
        # Only change the disposable actor's authorization input. All execution,
        # cancellation and resource states must be produced by the live workers.
        with sqlite3.connect(root/'chat.db') as fault_db:
            fault_db.execute("UPDATE admin_users SET status='已冻结',status_before_freeze='正常' WHERE id='alice'")
        revoked_at=time.monotonic()
        try:
            api('/api/v1/chat/acceptance-operations/'+operation['id'])
        except HTTPError as error:assert error.code in {401,403,404}
        else:raise AssertionError('revoked_actor_allowed')
    elif mode in {'executor-loss','application-loss'}:
        container=(database.execute('SELECT executor_id FROM moonbox_execution_receipts WHERE turn_id=?',(turn['id'],)).fetchone()[0]
                   if mode=='executor-loss' else 'moonbox-candidate-'+operation['attempt_id']+'-app')
        inspected=json.loads(subprocess.check_output(['docker','inspect',container],text=True))[0]
        assert inspected['Config']['Labels'].get('moonbox.temp.run')==run
        subprocess.run(['docker','kill',container],check=True,capture_output=True)
    elif mode=='cleanup-failure':
        peer='moonbox-acceptance-cleanup-peer-'+operation['attempt_id']
        subprocess.run(['docker','run','-d','--name',peer,'--network','moonbox-candidate-'+operation['attempt_id']+'-net',
            '--label','moonbox.temp.managed=true','--label','moonbox.temp.run='+run,'--label','moonbox.temp.expires='+expires,
            '--read-only','--cap-drop','ALL','--security-opt','no-new-privileges:true','--memory','32m','--cpus','0.1',
            '--pids-limit','16','--log-driver','none','node:24-trixie-slim','sleep','600'],check=True,capture_output=True)
    deadline=time.time()+600
    while time.time()<deadline:
        current=dict(database.execute('SELECT * FROM verification_operations WHERE id=?',(operation['id'],)).fetchone())
        if current['status'] in {'passed','failed','blocked','cancelled'} and current['cleanup_state'] in {'released','cleanup_failed'}:break
        time.sleep(1)
    report=dict(scenario=mode,operation_id=operation['id'],source_turn_id=turn['id'],conversation_id=chat['id'],
        status=current['status'],cleanup_state=current['cleanup_state'],peer=peer)
    if mode=='revocation':
        deadline=time.time()+90
        while time.time()<deadline:
            source=database.execute('SELECT status FROM chat_turns WHERE id=?',(turn['id'],)).fetchone()
            receipt=database.execute('SELECT executor_closed,files_collected FROM moonbox_execution_receipts WHERE turn_id=?',(turn['id'],)).fetchone()
            if source['status'] in {'failed','stopped','unknown'} and receipt and receipt['executor_closed']:break
            time.sleep(.5)
        report.update(source_status=source['status'],executor_closed=bool(receipt['executor_closed']),
                      resume_count=current['resume_count'],revoke_to_release_seconds=round(time.monotonic()-revoked_at,2),
                      fault='isolated_actor_frozen',terminal_rows_injected=False)
        assert (report['source_status'] in {'failed','stopped','unknown'} and report['executor_closed']
                and report['resume_count']==0 and current['cleanup_state']=='released'
                and report['revoke_to_release_seconds']<=60),report
        with sqlite3.connect(root/'chat.db') as fault_db:
            fault_db.execute("UPDATE admin_users SET status='正常',status_before_freeze=NULL WHERE id='alice'")
    (root/(mode+'.json')).write_text(json.dumps(report,indent=2))
    print(json.dumps(report),flush=True)


if __name__=='__main__':main()
