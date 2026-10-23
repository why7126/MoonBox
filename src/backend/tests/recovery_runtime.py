"""Restart only an explicitly selected disposable recovery deployment, preserving its DB."""
import json,os,sys,sqlite3,subprocess,hashlib,time
from pathlib import Path
root=Path(sys.argv[1]).resolve()
if root.parent!=Path('/private/tmp') or not root.name.startswith('moonbox-governance-live-'):
    raise SystemExit('isolated root required')
environment=json.loads((root/'environment.json').read_text())
os.environ.update(environment)
os.environ['GOVERNANCE_TAIL_PROBE']='1'
if '--copy' in sys.argv:
    with sqlite3.connect(root/'moonbox.db') as db:
        if db.execute('select count(*) from chat_turns').fetchone()[0]:raise SystemExit('mode switch requires empty fixture')
    bindings=json.loads(os.environ['MOONBOX_CHAT_REPOSITORY_BINDINGS'])
    for binding in bindings:binding['workspace_mode']='copy'
    os.environ['MOONBOX_CHAT_REPOSITORY_BINDINGS']=json.dumps(bindings)
    environment['MOONBOX_CHAT_REPOSITORY_BINDINGS']=os.environ['MOONBOX_CHAT_REPOSITORY_BINDINGS']
    from app.db.session import get_session_factory
    from app.governance.scope import authorize
    with get_session_factory()() as db:scope=authorize(db,'alice','space','moonbox-validation')
    permit=root/'private/maintenance.json';data=json.loads(permit.read_text());data.update(scope_key=scope.key,binding_revision=scope.binding_revision,expires_at=time.time()+3500);permit.write_text(json.dumps(data))
    (root/'environment.json').write_text(json.dumps(environment))
children=[]
project=Path(__file__).resolve().parents[3]

def stop():
    for child in reversed(children):
        if child.poll() is None:
            child.terminate()
            try:child.wait(timeout=60)
            except subprocess.TimeoutExpired:child.kill();child.wait()
    children.clear()

def start():
    files=list((project/'src/backend/app/governance').glob('*.py'))+list((project/'src/backend/app/chat').glob('*.py'))+list((project/'src/web/dist/assets').glob('*'))
    (root/'runtime-fingerprints.json').write_text(json.dumps({str(p.relative_to(project)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}))
    commands=[['-m','governance_stage_worker_probe'],['-m','app.governance.controller'],[str(Path(__file__).with_name('governance_recovery_live_harness.py')),'serve']]
    for i,args in enumerate(commands):children.append(subprocess.Popen([sys.executable,*args],stdout=(root/f'restarted-{i}.log').open('a'),stderr=subprocess.STDOUT))
    print(json.dumps({'started':True,'preserved_database':True,'workspace_mode':json.loads(os.environ['MOONBOX_CHAT_REPOSITORY_BINDINGS'])[0]['workspace_mode']}),flush=True)
try:
    start()
    for line in sys.stdin:
        if line.strip()=='cleanup':break
        if line.strip()=='crash':
            for child in children:
                if child.poll() is None:child.kill()
            for child in children:child.wait()
            children.clear()
            print('isolated processes interrupted; database preserved',flush=True)
        if line.strip()=='restart':stop();start()
        if line.strip()=='status':print(json.dumps({'alive':[p.poll() is None for p in children]}),flush=True)
finally:stop();print('isolated runtime stopped',flush=True)
