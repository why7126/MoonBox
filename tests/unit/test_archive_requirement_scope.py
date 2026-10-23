"""BUG-0062: requirement scope, evidence facts and zero-write close rejection."""
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from test_archive_baseline_transition import own, other, put, delta, proof, ROOT
from app.governance.acceptance_evidence import archived_readiness
from app.governance.archive_admission import change_acceptance
from app.governance.sprint_archive_admission import close_blockers


@pytest.mark.parametrize('text', [
    '', '## UNKNOWN Requirements\n'+delta('A'),
    delta('A')+delta('A'), delta('A')+'\n## RENAMED Requirements\nFROM: A\nTO: B\n',
    '## ADDED Requirements\n### Requirement: \nbody\n',
    '# Title\nUnrepresented module edit\n'+delta('A'),
    '## ADDED Requirements\nmodule edit\n'+delta('A').split('\n',1)[1],
    delta('A')+'\n### Other heading\nunknown',
])
def test_ambiguous_delta_rejected(tmp_path, text):
    put(tmp_path/'specs/cap/spec.md', text)
    with pytest.raises(ValueError): proof.delta_scope(tmp_path)


@pytest.mark.parametrize('kind', ['ADDED', 'MODIFIED', 'REMOVED'])
def test_same_title_conflict_has_safe_identity(tmp_path, kind):
    folder, journal, record = own(tmp_path)
    archived, successor = other(tmp_path, capability='own-cap')
    put(archived/'specs/own-cap/spec.md', delta('自身能力').replace('ADDED',kind))
    successor['delta_hash'] = proof.tree_hash(archived/'specs')
    proof.journal_path(tmp_path, 'other-change').write_text(json.dumps(successor))
    result = proof.recovery_admission(tmp_path, 'own-change')
    # The active baseline is a merge candidate; expected-state fallback must retain
    # the real overlap diagnosis when neither candidate proves safe.
    assert not result['ready']
    assert result['recovery_reason']=='archive_spec_baseline_changed'
    assert str(tmp_path) not in json.dumps(result)


def archived_sample(root, count=36):
    folder, journal, record = own(root, 'REQ-9900-scope')
    put(root/'issues/requirements/review/REQ-9900-scope/acceptance.md',
        '---\nacceptance_status: passed\n---\n'+''.join(f'- [ ] AC-{i:03} 自动验收\n' for i in range(count)))
    checks=[]; rows=[]
    for i in range(count):
        artifact=f'openspec/changes/own-change/evidence/acceptance/original/item-{i}.txt'
        put(root/artifact, 'verified')
        checks.append(dict(id=f'AC-{i:03}', kind='command', argv=['true'], inputs=['source.txt'],artifacts=[artifact]))
        rows.append(dict(id=f'AC-{i:03}', status='passed',artifacts=[dict(path=artifact,sha256=hashlib.sha256(b'verified').hexdigest())]))
    put(folder/'acceptance-plan.json', json.dumps(dict(schema_version=1, change_id='own-change',issue_id='REQ-9900-scope',checks=checks)))
    put(folder/'evidence/acceptance/original/manifest.json',json.dumps(dict(run_id='original',status='passed',checks=rows)))
    put(root/'openspec/specs/own-cap/spec.md',delta('自身能力'))
    record.update(schema_version=4,input_projection=1,expected_spec_hash=proof.tree_hash(root/'openspec/specs'),
                  delta_hash=proof.tree_hash(folder/'specs'),delivery_input_hash=proof.delivery_input_hash(folder))
    journal.write_text(json.dumps(record))
    archived=root/'openspec/archive/2026-10-21-own-change'
    shutil.move(folder,archived)
    return archived


@pytest.mark.parametrize('damage,done', [('none',36),('baseline',36),('artifact',35),('coverage',0)])
def test_real_progress_is_independent_of_recovery(tmp_path,damage,done):
    archived=archived_sample(tmp_path)
    if damage=='baseline': put(tmp_path/'openspec/specs/unknown/spec.md','unknown')
    if damage=='artifact': put(archived/'evidence/acceptance/original/item-0.txt','corrupt')
    if damage=='coverage':
        p=archived/'evidence/acceptance/original/manifest.json'; m=json.loads(p.read_text());m['checks']=[];p.write_text(json.dumps(m))
    before=proof.tree_hash(tmp_path)
    for _ in range(2):
        result=change_acceptance(tmp_path,'own-change')
        assert result['done']==done and result['total']==36
        assert result['ready']==(damage=='none')
        if damage=='baseline': assert result['recovery_reason']=='archive_spec_baseline_changed'
    assert proof.tree_hash(tmp_path)==before


@pytest.mark.parametrize('target',['specs','journal','delivery','artifact'])
def test_changes_during_proof_cannot_publish_ready(tmp_path,monkeypatch,target):
    archived=archived_sample(tmp_path)
    original=proof._recovery_state
    def race(*args,**kwargs):
        result=original(*args,**kwargs)
        path={'specs':tmp_path/'openspec/specs/own-cap/spec.md',
              'journal':proof.journal_path(tmp_path,'own-change'),
              'delivery':archived/'proposal.md',
              'artifact':archived/'evidence/acceptance/original/item-0.txt'}[target]
        put(path,'changed')
        return result
    monkeypatch.setattr(proof,'_recovery_state',race)
    assert not change_acceptance(tmp_path,'own-change')['ready']


def test_sprint_and_sync_fail_before_any_projection_write(tmp_path,monkeypatch):
    archived_sample(tmp_path)
    put(tmp_path/'openspec/specs/unknown/spec.md','unproven')
    put(tmp_path/'iterations/change/sprint-099/sprint.yaml','id: sprint-099\nstatus: active\nchanges:\n  - own-change\n')
    put(tmp_path/'openspec/archive/2026-10-21-own-change/tasks.md','- [x] done\n')
    expected=close_blockers(tmp_path,['own-change'])
    assert expected
    spec=importlib.util.spec_from_file_location('scope_sprint_readiness',ROOT/'scripts/validate-sprint-archive-readiness.py')
    gate=importlib.util.module_from_spec(spec);sys.modules[spec.name]=gate;spec.loader.exec_module(gate)
    assert expected[0] in gate.evaluate_sprint(tmp_path,'sprint-099').changes[0].blocker
    assert gate.main(['--root',str(tmp_path),'--sprint','sprint-099','--force','--json'])==1
    from scripts.workflow_sync import engine, title_gate
    monkeypatch.setattr(engine,'ROOT',tmp_path)
    monkeypatch.setattr(engine,'resolve_sprint_id',lambda *a,**k:('sprint-099',None))
    monkeypatch.setattr(engine,'load_all_issues',lambda:{})
    monkeypatch.setattr(engine,'run_openspec_list',lambda:{})
    monkeypatch.setattr(engine,'load_sprint',lambda _:SimpleNamespace(changes=['own-change']))
    monkeypatch.setattr(title_gate,'validate_generated',lambda *a:[])
    before=proof.tree_hash(tmp_path)
    for dry in (True,False):
        report=engine.SyncEngine(dry_run=dry)._run(event='sprint.archive',sprint_id='sprint-099')
        assert report.errors==expected and not report.ok
        assert proof.tree_hash(tmp_path)==before
    cli=subprocess.run([sys.executable,str(ROOT/'scripts/validate-issue-acceptance-ready.py'),'own-change','--root',str(tmp_path)],capture_output=True,text=True)
    assert cli.returncode==1


def test_product_progress_and_sprint_use_shared_deep_gate(tmp_path,monkeypatch):
    from app.services import requirement_center as service
    archived_sample(tmp_path)
    put(tmp_path/'issues/requirements/review/REQ-9900-scope/trace.md',
        '---\nrelated_change: own-change\n---\n')
    put(tmp_path/'openspec/specs/unknown/spec.md','unknown')
    monkeypatch.setattr(service,'_governance_root',lambda:tmp_path)
    monkeypatch.setattr(service,'_change_status',lambda _: 'archived')
    monkeypatch.setattr(service,'_sprint_acceptance_signed_off',lambda _:True)
    progress=service._acceptance_readiness(tmp_path/'issues/requirements/review/REQ-9900-scope')
    assert progress[:2]==(0,36) and '基线' in progress[2]
    blockers=service._sprint_archive_blockers('sprint-099',{'changes':['own-change']})
    assert len(blockers)==1 and blockers[0].status=='archive_spec_baseline_changed'
    assert blockers[0].message==change_acceptance(tmp_path,'own-change')['reason']


def test_successor_delivery_tamper_and_race_rejected(tmp_path,monkeypatch):
    own(tmp_path)
    archive,record=other(tmp_path)
    record.update(schema_version=4,input_projection=1,delivery_input_hash=proof.delivery_input_hash(archive))
    proof.journal_path(tmp_path,'other-change').write_text(json.dumps(record))
    assert proof.recovery_admission(tmp_path,'own-change')['ready']
    put(archive/'design.md','unrecorded edit')
    assert not proof.recovery_admission(tmp_path,'own-change')['ready']
    (archive/'design.md').unlink()
    original=proof.verify_chain_effects
    def concurrent(*args):
        original(*args)
        put(archive/'design.md','late edit')
    monkeypatch.setattr(proof,'verify_chain_effects',concurrent)
    assert not proof.recovery_admission(tmp_path,'own-change')['ready']


def test_successor_journal_changes_between_parse_and_snapshot(tmp_path,monkeypatch):
    own(tmp_path)
    other(tmp_path)
    original=proof.read_record
    def concurrent(path):
        record=original(path)
        if path.stem=='other-change':
            changed={**record,'baseline_spec_hash':'b'*64}
            path.write_text(json.dumps(changed))
        return record
    monkeypatch.setattr(proof,'read_record',concurrent)
    assert not proof.recovery_admission(tmp_path,'own-change')['ready']


def test_fix_delta_does_not_conflict_with_retained_original_requirements():
    current=ROOT/'openspec/changes/fix-archive-requirement-scope-conflict'
    if not current.exists():
        matches=proof.archive_paths(ROOT,current.name)
        assert len(matches)==1
        current=matches[0]
    originals=proof.archive_paths(ROOT,'fix-chat-unified-run-status-verification')
    assert len(originals)==1
    assert proof.delta_scope(current).isdisjoint(proof.delta_scope(originals[0]))
