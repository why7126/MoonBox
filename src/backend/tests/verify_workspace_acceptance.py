"""Validate bounded, sanitized execution evidence. Images still require visual sign-off."""
import argparse
import hashlib
import json
from pathlib import Path
from workspace_verification import ROOT, verify


def read(relative):
    path=ROOT/relative
    assert path.resolve().is_relative_to(ROOT)
    return json.loads(path.read_text())


def main(category, change):
    import re
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", change)
    base="openspec/changes/"+change+"/evidence/implementation/"
    if category in ('backend','mysql'):
        for name in (('stable-backend.json',) if category=='backend' else ('stable-mysql.json',)):
            verify(ROOT/base/name)
    elif category=='ui':
        data=read(base+'ui-regression.json')
        assert data['passed']>=5 and data['failed']==data['exit_code']==data['typecheck_exit']==0 and data['source_stable']
        for name,value in data['source_hashes'].items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==value,name
        visual=read('openspec/changes/'+change+'/evidence/ui/visual-review.json')
        assert visual['status']=='passed' and visual['source_hashes']==data['source_hashes']
        keyboard=read('openspec/changes/'+change+'/evidence/ui/workspace-keyboard.json')
        assert keyboard['insideDialog'] and keyboard['parentStillOpen'] and keyboard['childClosed']
    elif category=='model':
        data=read(base+'isolated-live-round.json')
        assert data['sample']=='isolated-real-model-synthetic-identity' and data['status']=='completed'
        assert all(data[key] for key in ('file_changed','immutable_runtime','executor_closed','files_collected','lease_released'))
        assert data['complete_points']>=2
    elif category=='api':
        verify(ROOT/base/'stable-backend.json')
        data=read(base+'live-api-flow.json')
        assert data['sample']=='live-http-api-real-git-synthetic-identity'
        assert data['permission_revoked']['http_status']==403 and data['source_changed']['http_status']==409
        assert data['no_merge_on_rejection'] and data['merge_success']['registry_written']
        assert data['merge_success']['governance_state']=='completed'
        assert data['interrupted_receipt_resume']['git_commit_count_unchanged']
        assert data['interrupted_receipt_resume']['repeat_resume_same_operation']
        assert data['environment_cleanup']=={'state':'passed','cleanup_state':'clean'}
    elif category=='performance':
        verify(ROOT/base/'stable-backend.json')
        data=read(base+'performance-sample.json')
        assert data['files']==data['restored_files']==100 and data['bytes_per_phase']==409600
        assert all(isinstance(value,(float,int)) and value>=0 for value in data['measurements'].values())
    elif category=='candidate':
        verify(ROOT/base/'stable-backend.json')
        data=read(base+'live-candidate.json')
        assert data['result']['status']=='passed' and data['cleanup_state']=='clean'
        assert data.get('source_hashes'), 'Missing executed provider source fingerprint'
        for name,value in data['source_hashes'].items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==value,name
        matrices=data['evidence']['matrices']
        assert {row['database'] for row in matrices}=={'sqlite','mysql'}
        for row in matrices:
            assert row['app_version']==data['result']['candidate_commit']
            assert row['checks_passed']>0 and row['browser']['category']=='real_browser'
            if row['database']=='mysql': assert row['version'].startswith('8.4.')
    print(json.dumps({'category':category,'evidence_checks':'passed'}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('category',choices=['backend','mysql','ui','model','performance','candidate','api'])
    parser.add_argument('--change',required=True)
    args=parser.parse_args(); main(args.category,args.change)
