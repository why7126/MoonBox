#!/usr/bin/env python3
"""Disposable, credential-free Docker integration; no live service modification."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run', required=True)
    parser.add_argument('--expires', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args=parser.parse_args()
    spec=importlib.util.spec_from_file_location('builder',ROOT/'scripts/build-archive-tools.py')
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    with tempfile.TemporaryDirectory(prefix='archive-routing-') as temporary:
        base=Path(temporary);base.chmod(0o755)
        package=base/'tools';digest=builder.build(ROOT,package)
        config=base/'config.json'
        config.write_text(json.dumps({'schema_version':1,'root':'/opt/moonbox/archive-tools',
            'host_root':'/opt/moonbox/archive-tools','digest':digest}));config.chmod(0o444)
        work=base/'work';work.mkdir();work.chmod(0o777)
        (work/'unknown.json').write_text('{"state":"unknown","occupied":true}')
        (work/'historical-evidence').write_text('immutable synthetic history')
        before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in work.iterdir()}
        common=['docker','run','--rm','--network','none','--read-only','--user','10001:10001',
            '--cap-drop','ALL','--security-opt','no-new-privileges:true','--pids-limit','128','--memory','512m',
            '--label','moonbox.temp.managed=true','--label','moonbox.temp.run='+args.run,
            '--label','moonbox.temp.expires='+args.expires,'--tmpfs','/tmp:rw,nosuid,size=64m',
            '--env','HOME=/tmp','--env','CODEX_HOME=/tmp/codex','--workdir','/work','--mount',f'type=bind,src={work},dst=/work',
            '--mount',f'type=bind,src={config},dst=/etc/moonbox/archive-tools.json,readonly']
        mount=['--mount',f'type=bind,src={package},dst=/opt/moonbox/archive-tools,readonly']
        image='moonbox-chat-executor:0.153.4-test'
        bootstrap="import sys;sys.path.insert(0,'/opt/moonbox/archive-tools/src/backend');"
        probe=bootstrap+'''import json,os,subprocess
from pathlib import Path
from types import SimpleNamespace
from app.governance.archive_tools import selected,business_root
from app.governance.replacement_executor import ArchiveDriver
from app.chat.container_server import ContainerAppServer
p=selected();d=ArchiveDriver(SimpleNamespace(root=Path('/work')))
assert d.package.digest==p.digest
cli=subprocess.run([sys.executable,'/opt/moonbox/archive-tools/scripts/archive-tool-route.py','--check'],capture_output=True,text=True)
assert cli.returncode==0 and cli.stdout.strip()==p.digest
Path('/tmp/codex').mkdir(exist_ok=True)
s=object.__new__(ContainerAppServer);s.archive_package=p
command=s.archive_launch()
# This is the actual production app-server startup command, with stdin closed;
# no account, prompt, model call, database or live project is supplied.
child=subprocess.run(command,input='',capture_output=True,text=True,timeout=30)
assert child.returncode==0,(child.returncode,child.stderr[-200:])
os.environ['MOONBOX_ARCHIVE_ROUTED']='1'
assert business_root(p.root)==Path('/work')
assert not os.access(p.root,os.W_OK)
print(json.dumps({'digest':p.digest,'cli':True,'service_driver':True,'actual_child_startup':True,'readonly':True,'business_root_preserved':True}))
'''
        result=subprocess.run(common+mount+[image,'python','-B','-c',probe],capture_output=True,text=True,timeout=90)
        if result.returncode:
            print(result.stderr[-2000:],file=sys.stderr);return 1
        positive=json.loads(result.stdout)
        config.chmod(0o644)
        config.write_text(json.dumps({'schema_version':1,'root':'/opt/moonbox/archive-tools',
            'host_root':'/opt/moonbox/archive-tools','digest':'0'*64}));config.chmod(0o444)
        rejected=subprocess.run(common+mount+[image,'python','-B','-c',bootstrap+'from app.governance.archive_tools import selected;selected()'],capture_output=True,text=True,timeout=30)
        assert rejected.returncode!=0 and 'archive_tool_digest_mismatch' in rejected.stderr
        # Missing runtime tool package fails before any workload can be started.
        missing=subprocess.run(common+[image,'python','-B','-c',bootstrap+'from app.governance.archive_tools import selected;assert selected()'],capture_output=True,text=True,timeout=30)
        assert missing.returncode!=0
        after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in work.iterdir()}
        assert before==after
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps({'schema_version':1,'environment':'isolated-docker',
            'positive':positive,'digest_mismatch_rejected':True,'missing_package_rejected':True,
            'history_unknown_occupancy_unchanged':True,'model_calls':0,
            'scope':'real CLI/service driver/production child startup; synthetic business facts, no live product archive'},indent=2)+'\n')
        # Package is immutable during execution; make disposable directories removable.
        for path in package.rglob('*'):
            if path.is_dir():path.chmod(0o755)
        package.chmod(0o755)
    print('archive tool Docker integration passed')
    return 0

if __name__=='__main__':raise SystemExit(main())
