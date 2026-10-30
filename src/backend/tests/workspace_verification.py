"""Stable verification evidence for the workspace Changes, with exact source hashes.

This records executed tests and supports later AC evidence checks without rerunning
identical commands. Visual sign-off and real Docker/model observations remain separate.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]


def inputs():
    paths = set()
    for directory in ('moonbox_core','moonbox_app_server','moonbox_exec','moonbox_exec_server','moonbox_rollout','moonbox_worktree','verification'):
        paths.update((ROOT/'src/backend/app'/directory).glob('*.py'))
    for relative in ('chat/admission.py','chat/api.py','chat/backup.py','chat/cleanup.py','chat/container_server.py',
                     'chat/content_store.py','chat/execution.py','chat/local_worker.py','chat/observability.py',
                     'chat/platform_worker.py','chat/preparation_failure.py','chat/result_reader.py','chat/schema.py',
                     'chat/service.py','chat/resource_guard.py','chat/snapshot_store.py','chat/worker.py','chat/write_profiles.py',
                     'governance/reader.py','schemas/requirement_center.py'):
        paths.add(ROOT/'src/backend/app'/relative)
    paths.update((ROOT/'src/backend/tests').glob('test_workspace*.py'))
    paths.add(Path(__file__).resolve())
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths) if p.is_file()}


def run(suite, report):
    if suite == 'backend':
        files = sorted(str(p.relative_to(ROOT)) for p in (ROOT/'src/backend/tests').glob('test_workspace*.py'))
        names = ['managed_worktree_git','recovery_catalog','candidate_supplier','chat','chat_workspace','chat_content_store',
                 'chat_scalable','chat_backup','permission_governance_contract','governance_read_cache','verification_runner']
        files += ['src/backend/tests/test_'+name+'.py' for name in names]
    else:
        if not os.getenv('CHAT_TEST_DATABASE_URL','').startswith('mysql+pymysql://'):
            raise SystemExit('Dedicated temporary MySQL URL required')
        files = ['src/backend/tests/test_'+name+'.py' for name in ('workspace_integration','workspace_restore_operation',
            'workspace_api','workspace_legacy_points','candidate_supplier','chat_content_store','chat_scalable')]
    before = inputs()
    for name in files:
        before[name] = hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='moonbox-check-') as folder:
        xml = Path(folder)/'result.xml'
        env = dict(os.environ, PYTHONPATH=str(ROOT/'src/backend')+os.pathsep+str(ROOT/'src/backend/tests'))
        argv = [sys.executable,'-m','pytest',*files,'-q','--junitxml='+str(xml)]
        result = subprocess.run(argv,cwd=ROOT,env=env)
        suites = ET.parse(xml).getroot().findall('.//testsuite') if xml.exists() else []
        counts = {key:sum(int(item.get(key,'0')) for item in suites) for key in ('tests','failures','errors','skipped')}
        seconds = sum(float(item.get('time','0')) for item in suites)
        cases = [dict(name=case.get('name'),status='failed' if case.find('failure') is not None or case.find('error') is not None else 'skipped' if case.find('skipped') is not None else 'passed') for item in suites for case in item.findall('testcase')]
    stable = all((ROOT/name).is_file() and hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==value for name,value in before.items())
    data = dict(schema_version=1,suite=suite,sample='synthetic-regression-real-git-files-database',
        database='mysql-8.4-temporary' if suite=='mysql' else 'sqlite',exit_code=result.returncode,
        source_stable=stable,counts=counts,seconds=seconds,cases=cases,source_hashes=before)
    report.parent.mkdir(parents=True,exist_ok=True); report.write_text(json.dumps(data,ensure_ascii=False,indent=2))
    return result.returncode or (0 if stable else 1)


def verify(report):
    data=json.loads(report.read_text())
    assert data['exit_code']==0 and data['source_stable']
    assert data['counts']['tests']>0 and data['counts']['failures']==data['counts']['errors']==0
    for relative,value in data['source_hashes'].items():
        path=ROOT/relative
        assert path.resolve().is_relative_to(ROOT) and hashlib.sha256(path.read_bytes()).hexdigest()==value, relative
    print(json.dumps({'suite':data['suite'],'counts':data['counts'],'source_matches':True}))
    return 0


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--run',choices=['backend','mysql']); parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    raise SystemExit(run(args.run,args.report) if args.run else verify(args.report))
