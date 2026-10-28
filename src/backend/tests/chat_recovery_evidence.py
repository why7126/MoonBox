"""Sanitized evidence runner/verifier for BUG-0064 (explicit disposable DB only)."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
EVIDENCE=ROOT/'openspec/changes/fix-chat-unknown-recovery-container-churn/evidence'
TESTS=['test_chat_unknown_recovery.py','test_chat_recovery_cache.py','test_chat_assistant_output.py',
       'test_chat_accounting.py','test_chat_container_failure.py','test_chat_toolchain.py','test_chat_scalable.py','test_chat.py']


def fingerprint():
    files=set((ROOT/'src/backend/app').rglob('*.py'))
    files.update(ROOT/'src/backend/tests'/name for name in TESTS+['test_chat_recovery_docker.py','chat_recovery_evidence.py'])
    files.add(ROOT/'src/backend/container/seccomp-codex.json')
    return hashlib.sha256('\n'.join(str(path.relative_to(ROOT))+':'+hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(files)).encode()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',choices=('sqlite','mysql'));parser.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    if args.verify:
        for name in ('sqlite','mysql','docker-recovery'):
            report=json.loads((EVIDENCE/(name+'.json')).read_text())
            assert report['input_fingerprint']==fingerprint(), 'stale '+name
            if name=='docker-recovery':
                assert report['quiet_seconds']>=330 and report['quiet_creates']==0
                assert report['interrupted_cleanup'] and report['attempts'][-1]['state']=='paused'
                assert report['attempt_containers_created']==report['attempt_containers_destroyed']
            else:assert report['failed']==0 and report['passed']>0
        print('BUG-0064: current SQLite, MySQL and real Docker evidence verified')
        return
    if not args.run:parser.error('select --run or --verify')
    if args.run=='mysql' and not os.environ.get('CHAT_TEST_DATABASE_URL'):parser.error('explicit disposable MySQL URL required')
    if args.run=='sqlite' and os.environ.get('CHAT_TEST_DATABASE_URL'):parser.error('SQLite requires isolated fixture default')
    import pytest
    counts={'passed':0,'failed':0,'skipped':0}
    class Results:
        def pytest_runtest_logreport(self,report):
            if report.failed:counts['failed']+=1
            elif report.skipped:counts['skipped']+=1
            elif report.when=='call' and report.passed:counts['passed']+=1
    before=fingerprint();os.chdir(ROOT/'src/backend')
    sys.path.insert(0,str(ROOT/'src/backend'));sys.path.insert(0,str(ROOT/'src/backend/tests'))
    tests=TESTS if args.run=='sqlite' else ['test_chat_unknown_recovery.py']
    code=pytest.main(['-q','--tb=short',*['tests/'+name for name in tests]],plugins=[Results()])
    if code or before!=fingerprint():raise SystemExit(code or 1)
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    (EVIDENCE/(args.run+'.json')).write_text(json.dumps({'database':args.run,**counts,'input_fingerprint':before},indent=2)+'\n')


if __name__=='__main__':main()
