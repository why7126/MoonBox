"""Stable scoped verification entry; synthetic regression is not product acceptance."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def main():
    root=Path(__file__).resolve().parents[3]
    backend=root/'src/backend'
    names=['test_acceptance_orchestration.py','test_acceptance_snapshot.py','test_acceptance_source.py',
           'test_acceptance_api.py','test_acceptance_runtime.py','test_acceptance_worker.py',
           'test_candidate_supplier.py','test_verification_runner.py','test_acceptance_tool.py',
           'test_acceptance_delivery.py','test_acceptance_archive.py','test_chat_app_server.py',
           'test_acceptance_proof.py','test_acceptance_product_adaptation.py','test_chat_unknown_recovery.py']
    command=[sys.executable,'-m','pytest',*[str(backend/'tests'/name) for name in names],'-q']
    result=subprocess.run(command,cwd=backend,capture_output=True,text=True,timeout=180)
    sources=[*sorted((backend/'app/verification').glob('acceptance_*.py')),*[backend/'tests'/name for name in names],
             backend/'app/verification/candidate.py',backend/'app/verification/runner.py',
             backend/'app/chat/api.py',backend/'app/chat/schema.py']
    report={'category':'synthetic_regression','status':'passed' if result.returncode==0 else 'failed',
            'exit_code':result.returncode,'summary':result.stdout[-6000:].replace(str(root),'workspace'),
            'source_hashes':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    target=root/'openspec/changes/add-chat-isolated-acceptance-orchestration/evidence/implementation/backend-regression.json'
    target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'category':report['category']},ensure_ascii=False))
    return result.returncode


if __name__=='__main__':raise SystemExit(main())
