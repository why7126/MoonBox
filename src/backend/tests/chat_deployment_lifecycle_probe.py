"""已启动独立Chat环境的真实登录/备份/删除/停止补验，不发送模型任务。"""
import argparse
import json
from pathlib import Path
import sqlite3
import time
import urllib.request
from app.chat.deployment import control_root,existing,stop
from app.chat.backup import LocalBackupStore


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--scope',required=True);args=parser.parse_args()
    control=control_root(args.scope);active=existing(control)
    assert active and active['ready'] and not active['turns']
    root=Path(active['root']);credentials=json.loads((root/'browser.json').read_text());base=credentials['url'];token=None
    def api(path,body=None,method=None):
        headers={'Content-Type':'application/json'}
        if token:headers['Authorization']='Bearer '+token
        request=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers,method=method)
        with urllib.request.urlopen(request,timeout=5) as response:return json.load(response)['data']
    report={}
    try:
        token=api('/api/v1/auth/login',{'username':'alice','password':credentials['password']})['access_token']
        assert api('/api/v1/chat/capabilities?space_id=space')['execution_ready']
        cid=api('/api/v1/chat/conversations',{'space_id':'space','repository_id':'repo'})['id']
        store=LocalBackupStore(root/'backups');backup=store.create(root/'chat.db')
        assert api('/api/v1/chat/conversations/'+cid,method='DELETE')['backup_status']=='pending'
        restored=root/'restored.sqlite';store.restore(backup,restored)
        with sqlite3.connect(restored) as db:
            assert db.execute('SELECT deleted_at FROM chat_conversations WHERE id=?',(cid,)).fetchone()[0]
        store.expire(backup)
        deadline=time.monotonic()+40
        while time.monotonic()<deadline:
            if api('/api/v1/chat/conversations/'+cid+'/cleanup')['backup_status']=='purged':break
            time.sleep(.5)
        else:raise RuntimeError('backup cleanup worker did not confirm inventory')
        assert (root/'seed/counter.txt').read_text()=='0\n'
        report={'real_login':True,'execution_gate_ready':True,'backup_initialized':True,
                'deleted_chat_not_resurrected':True,'worker_confirmed_backup_purge':True,'seed_code_preserved':True,
                'model_turns_sent':0}
    finally:
        stopped=stop(control)
    assert stopped['test_data_removed'] and not root.exists()
    report['test_services_and_data_removed']=True
    Path('/tmp/moonbox-deployment-lifecycle.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
