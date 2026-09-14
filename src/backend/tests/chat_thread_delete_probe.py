"""在临时Codex运行目录验证真实线程删除；不使用个人原始执行历史。"""
import json
import os
from pathlib import Path
import shutil
import tempfile
import time
from app.chat.local_probe import local_executor

if os.environ.get('CHAT_LIVE_ISOLATED_PROBE')!='1':raise SystemExit('explicit opt-in required')
with tempfile.TemporaryDirectory(prefix='moonbox-thread-delete-',dir='/private/tmp') as folder:
    path=Path(folder)/'work';path.mkdir();(path/'code.txt').write_text('preserve')
    with local_executor([path],executable=shutil.which('codex'),auth_source=Path.home()/'.codex/auth.json') as (factory,home):
        with factory(path) as server:
            thread=server.connect();turn=server.start_turn(thread,'Reply only OK. Do not run any tools or modify any files.')
            end=time.monotonic()+240;terminal=None
            while time.monotonic()<end:
                event=server.event(timeout=1)
                if not event:continue
                params=event.get('params',{})
                if event.get('method')=='turn/completed' and params.get('threadId')==thread and params.get('turn',{}).get('id')==turn:
                    terminal=params['turn']['status'];break
            assert terminal=='completed','no confirmed terminal'
            before=list(home.rglob('*.jsonl'));assert before,'no retained execution file'
            assert server.delete_thread(thread)
            end=time.monotonic()+5
            while any(p.exists() for p in before) and time.monotonic()<end:time.sleep(.1)
            assert not any(p.exists() for p in before),'retained execution file remains'
            assert (path/'code.txt').read_text()=='preserve'
            assert list(home.rglob('auth.json')),'credential accidentally removed'
        report={'real_model_turn':True,'thread_delete_ack':True,'execution_files_removed':True,'code_preserved':True,'credentials_preserved_during_delete':True}
    report['temporary_auth_removed']=not home.exists()
Path('/tmp/moonbox-thread-delete-probe.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
