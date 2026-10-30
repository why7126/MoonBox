"""Synthetic stdio peer; only used by adapter unit tests."""
import json
import os
from pathlib import Path
import sys
if '--version' in sys.argv:
    print('codex-cli 0.153.4');sys.exit()
def send(value):
    print(json.dumps(value),flush=True)
for line in sys.stdin:
    request=json.loads(line)
    if 'method' not in request:
        if request.get('id')==99 and request.get('result',{}).get('success'):
            send({'method':'item/completed','params':{'threadId':'thread','turnId':'turn','item':{'id':'call-test','type':'dynamicToolCall','tool':'moonbox_acceptance','success':True,'status':'completed'}}})
        continue
    method=request['method']
    if 'id' not in request:continue
    result={};params=request.get('params',{})
    mode=Path('fixture-mode').read_text() if Path('fixture-mode').exists() else ''
    if method in ('thread/start','thread/resume','thread/read'):
        result={'thread':{'id':'thread','cwd':'/mismatched' if mode=='mismatch' else os.getcwd(),'turns':[]}}
    if method=='turn/start':
        if mode=='acceptance':send({'id':99,'method':'item/tool/call','params':{'threadId':'thread','turnId':'turn','callId':'call-test','tool':'moonbox_acceptance','arguments':{}}})
        if mode=='disconnect':sys.exit(0)
        if mode=='interactive':send({'id':99,'method':'item/commandExecution/requestApproval','params':{}});continue
        if mode=='oversized':print('x'*262145,flush=True);continue
        send({'method':'item/agentMessage/delta','params':{'threadId':'thread','turnId':'turn','delta':'synthetic output'}})
        result={'turn':{'id':'turn'}}
    if method=='turn/interrupt' and mode=='interrupt-without-ack':
        send({'method':'turn/completed','params':{'threadId':'thread','turn':{'id':'turn','status':'interrupted'}}});continue
    send({'id':request['id'],'result':result})
    if method=='turn/start' and mode not in ('interrupt-without-ack','acceptance'):send({'method':'turn/completed','params':{'threadId':'thread','turn':{'id':'turn','status':'completed'}}})
