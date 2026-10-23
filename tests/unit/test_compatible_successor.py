"""Compatible append certificates: acceptance, safe structure and immutable chain."""
import hashlib
import json
from pathlib import Path

import pytest
from test_archive_baseline_transition import put, delta, proof
from app.governance import compatible_successor as compatible


ADDITION = '\n#### Scenario: 新场景\n- **WHEN** 出现新的执行\n- **THEN** 保留原保护并拒绝旧回调\n'


def certificate(root, folder, before, after, cid='next-change', key=('cap','能力')):
    artifact = folder/'evidence/acceptance/run/result.txt';put(artifact,'passed')
    relative=artifact.relative_to(root).as_posix()
    plan={'schema_version':1,'change_id':cid,'checks':[{'id':'AC-001','kind':'command','argv':['true'],'inputs':['rules/global.md'],'artifacts':[relative]}]}
    if not (root/'rules/global.md').exists():put(root/'rules/global.md', 'test rules')
    put(folder/'acceptance-plan.json',json.dumps(plan))
    manifest={'schema_version':1,'run_id':'run','status':'passed','checks':[{'id':'AC-001','status':'passed','artifacts':[{'path':relative,'sha256':hashlib.sha256(b'passed').hexdigest()}]}]}
    from app.governance.acceptance_evidence import fingerprint
    manifest['checks'][0]['fingerprint'] = fingerprint(root, plan['checks'][0])
    put(folder/'evidence/acceptance/run/manifest.json',json.dumps(manifest))
    expected=dict(schema_version=1,successor=cid,capability=key[0],requirement=key[1],before_sha256=compatible.digest(before),after_sha256=compatible.digest(after),added_scenarios=compatible.append_only(before,after),classification='compatible_append')
    record={**expected,'delta_sha256':proof.tree_hash(folder/'specs'),'acceptance_sha256':compatible.acceptance_binding(root,folder)}
    for name,extra in [('review',dict(reviewer='test-reviewer',rationale='原约束及场景保留，追加执行竞争拒绝场景。',contradictions=[])),('regression',dict(checks=['original_contract','added_scenarios','destructive_changes','broken_chain','concurrent_change']))]:
        path=root/f'openspec/changes/proof-review/evidence/{cid}-{name}.json'
        data={**expected,'status':'passed',**extra};put(path,json.dumps(data));record[name]={'path':path.relative_to(root).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    put(compatible.proof_path(root,cid,key),json.dumps(record))
    return record


def scene(root):
    old=root/'openspec/archive/2026-10-21-old-change';new=root/'openspec/archive/2026-10-22-next-change'
    initial=delta('能力');next_text=initial.replace('ADDED','MODIFIED')+ADDITION
    for folder,text in [(old,initial),(new,next_text)]:
        put(folder/'specs/cap/spec.md',text);put(folder/'trace.md','---\nstatus: archived\n---\n')
    put(root/'openspec/specs/cap/spec.md',initial)
    baseline=proof.tree_hash(root/'openspec/specs')
    put(root/'openspec/specs/cap/spec.md',next_text)
    current=proof.tree_hash(root/'openspec/specs')
    put(proof.journal_path(root,'old-change'),json.dumps(dict(change_id='old-change',expected_spec_hash=baseline,delta_hash=proof.tree_hash(old/'specs'))))
    put(proof.journal_path(root,'next-change'),json.dumps(dict(change_id='next-change',baseline_spec_hash=baseline,expected_spec_hash=current,delta_hash=proof.tree_hash(new/'specs'))))
    before=proof.delta_operations(old)[('cap','能力')][1];after=proof.delta_operations(new)[('cap','能力')][1]
    record=certificate(root,new,before,after)
    return old,new,record


def test_append_complete_chain_and_immutable_repeat(tmp_path):
    scene(tmp_path);before=proof.tree_hash(tmp_path)
    for _ in range(2):
        result=proof.recovery_admission(tmp_path,'old-change')
        assert result['ready'],result
        assert result['chain'][0]['compatibility'] == []
    assert proof.tree_hash(tmp_path)==before


@pytest.mark.parametrize('damage',['missing','version','review','contradiction','regression','artifact','delta','chain','identity','original','scenario','proof-symlink'])
def test_fail_closed(tmp_path,damage):
    old,new,record=scene(tmp_path);path=compatible.proof_path(tmp_path,'next-change',('cap','能力'))
    if damage=='missing':path.unlink()
    elif damage=='version':record['schema_version']=2;path.write_text(json.dumps(record))
    elif damage in {'review','regression'}:(tmp_path/record[damage]['path']).write_text('{}')
    elif damage=='contradiction':
        item=record['review'];asset=tmp_path/item['path'];data=json.loads(asset.read_text());data['contradictions']=['conflict'];asset.write_text(json.dumps(data));item['sha256']=hashlib.sha256(asset.read_bytes()).hexdigest();path.write_text(json.dumps(record))
    elif damage=='artifact':put(new/'evidence/acceptance/run/result.txt','tampered')
    elif damage=='delta':put(new/'specs/cap/spec.md','unknown')
    elif damage=='chain':proof.journal_path(tmp_path,'next-change').unlink()
    elif damage=='identity':put(tmp_path/'openspec/changes/next-change/trace.md','---\nstatus: applied\n---\n')
    elif damage=='original':put(old/'specs/cap/spec.md',delta('能力').replace('保留','删除'))
    elif damage=='scenario':record['added_scenarios']=[];path.write_text(json.dumps(record))
    elif damage=='proof-symlink':path.rename(path.with_suffix('.original'));path.symlink_to(path.with_suffix('.original'))
    expected_ready = damage in {'missing', 'version', 'review', 'contradiction', 'regression', 'scenario'}
    assert proof.recovery_admission(tmp_path,'old-change')['ready'] == expected_ready


@pytest.mark.parametrize('after',['系统 SHALL 删除。 #### Scenario: 原场景 - **WHEN** 执行 - **THEN** 删除',
 '系统 SHALL 保留。 #### Scenario: 原场景 - **WHEN** 执行 - **THEN** 保留 #### Scenario: 原场景 - **WHEN** 重复 - **THEN** 拒绝',
 '系统 SHALL 保留。 #### Scenario: 原场景 - **WHEN** 执行 - **THEN** 保留 #### Unknown: 内容'])
def test_unsupported_and_destructive_structure(after):
    before='系统 SHALL 保留。 #### Scenario: 原场景 - **WHEN** 执行 - **THEN** 保留'
    with pytest.raises(ValueError):compatible.append_only(before,after)


def test_certificate_race_rejected(tmp_path,monkeypatch):
    scene(tmp_path);original=proof._recovery_state
    def race(*args,**kwargs):
        result=original(*args,**kwargs)
        compatible.proof_path(tmp_path,'next-change',('cap','能力')).write_text('{}')
        return result
    monkeypatch.setattr(proof,'_recovery_state',race)
    assert not proof.recovery_admission(tmp_path,'old-change')['ready']


def test_optional_review_dependency_does_not_block(tmp_path, monkeypatch):
    _, _, record = scene(tmp_path)
    original = proof._recovery_state
    def race(*args, **kwargs):
        result = original(*args, **kwargs)
        (tmp_path / record['review']['path']).write_text('{}')
        return result
    monkeypatch.setattr(proof, '_recovery_state', race)
    assert proof.recovery_admission(tmp_path, 'old-change')['ready']


def test_multihop_uses_latest_protected_view(tmp_path):
    _, second, _ = scene(tmp_path)
    third = tmp_path / 'openspec/archive/2026-10-23-third-change'
    text = (second / 'specs/cap/spec.md').read_text() + ADDITION.replace('新场景', '第三场景')
    put(third / 'specs/cap/spec.md', text)
    put(third / 'trace.md', '---\nstatus: archived\n---\n')
    baseline = proof.tree_hash(tmp_path / 'openspec/specs')
    put(tmp_path / 'openspec/specs/cap/spec.md', text)
    current = proof.tree_hash(tmp_path / 'openspec/specs')
    put(proof.journal_path(tmp_path, 'third-change'), json.dumps(dict(change_id='third-change', baseline_spec_hash=baseline, expected_spec_hash=current, delta_hash=proof.tree_hash(third/'specs'))))
    before = proof.delta_operations(second)[('cap', '能力')][1]
    after = proof.delta_operations(third)[('cap', '能力')][1]
    certificate(tmp_path, third, before, after, 'third-change')
    result = proof.recovery_admission(tmp_path, 'old-change')
    assert result['ready'], result
    assert len(result['chain']) == 2


def test_candidate_destructive_preflight_does_not_write(tmp_path):
    scene(tmp_path)
    folder = tmp_path / 'openspec/changes/candidate'
    put(folder / 'specs/cap/spec.md', delta('能力').replace('ADDED', 'REMOVED'))
    before = proof.tree_hash(tmp_path)
    conflicts = compatible.preflight(tmp_path, 'candidate')
    assert conflicts and conflicts[0]['protected_changes'] == ['next-change', 'old-change']
    assert proof.recovery_admission(tmp_path, 'candidate')['ready']
    assert before == proof.tree_hash(tmp_path)


def test_candidate_append_is_not_archived_fact(tmp_path):
    old, archived, _ = scene(tmp_path)
    active = tmp_path / 'openspec/changes/next-change'
    active.parent.mkdir(exist_ok=True)
    archived.rename(active)
    put(active / 'trace.md', '---\nstatus: applied\n---\n')
    put(tmp_path / 'openspec/specs/cap/spec.md', (old / 'specs/cap/spec.md').read_text())
    before = proof.delta_operations(old)[('cap','能力')][1]
    after = proof.delta_operations(active)[('cap','能力')][1]
    certificate(tmp_path, active, before, after)
    assert compatible.preflight(tmp_path, 'next-change') == []
    assert not proof.archive_paths(tmp_path, 'next-change')
    put(tmp_path / 'rules/global.md', 'changed after acceptance')
    assert compatible.preflight(tmp_path, 'next-change')


def test_proof_producer_idempotent_and_no_history_mutation(tmp_path):
    import subprocess, sys
    old, new, record = scene(tmp_path)
    target = compatible.proof_path(tmp_path, 'next-change', ('cap','能力'))
    target.unlink()
    historical = [old, new, proof.journal_path(tmp_path, 'old-change').parent]
    hashes = [proof.tree_hash(p) for p in historical]
    command = [sys.executable, str(Path(__file__).resolve().parents[2] / 'scripts/record-compatible-successor.py'),
               '--root', str(tmp_path), '--predecessor', 'old-change', '--successor', 'next-change',
               '--capability', 'cap', '--requirement', '能力', '--review', record['review']['path'],
               '--regression', record['regression']['path']]
    for _ in range(2):
        result = subprocess.run(command, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
    assert hashes == [proof.tree_hash(p) for p in historical]
    assert proof.recovery_admission(tmp_path, 'old-change')['ready']


def test_review_symlink_and_moved_archive_evidence(tmp_path):
    _, _, record = scene(tmp_path)
    path = tmp_path / record['review']['path']
    original = path.with_suffix('.original')
    path.rename(original)
    path.symlink_to(original)
    assert proof.recovery_admission(tmp_path, 'old-change')['ready']
    path.unlink(); original.rename(path)
    folder = tmp_path / 'openspec/changes/proof-review'
    put(folder / 'trace.md', '---\nstatus: archived\n---\n')
    folder.rename(tmp_path / 'openspec/archive/2026-10-24-proof-review')
    assert proof.recovery_admission(tmp_path, 'old-change')['ready']


def test_candidate_projected_source_inputs(tmp_path):
    from app.governance.acceptance_evidence import fingerprint
    old, archived, _ = scene(tmp_path)
    active = tmp_path / 'openspec/changes/next-change'
    active.parent.mkdir(exist_ok=True); archived.rename(active)
    put(active / 'trace.md', '---\nstatus: applied\n---\n')
    put(tmp_path / 'openspec/specs/cap/spec.md', (old / 'specs/cap/spec.md').read_text())
    before=proof.delta_operations(old)[('cap','能力')][1]
    after=proof.delta_operations(active)[('cap','能力')][1]
    record=certificate(tmp_path, active, before, after)
    source=tmp_path/'trusted-source';put(source/'src/check.py','validated input')
    plan_path=active/'acceptance-plan.json';plan=json.loads(plan_path.read_text())
    plan['checks'][0]['inputs']=['src/check.py'];put(plan_path,json.dumps(plan))
    manifest_path=active/'evidence/acceptance/run/manifest.json';manifest=json.loads(manifest_path.read_text())
    manifest['checks'][0]['fingerprint']=fingerprint(tmp_path,plan['checks'][0],source_root=source)
    put(manifest_path,json.dumps(manifest))
    record['acceptance_sha256']=compatible.acceptance_binding(tmp_path,active,source_root=source)
    put(compatible.proof_path(tmp_path,'next-change',('cap','能力')),json.dumps(record))
    assert compatible.preflight(tmp_path,'next-change')
    assert compatible.preflight(tmp_path,'next-change',source_root=source)==[]
    put(source/'src/check.py','changed input')
    assert compatible.preflight(tmp_path,'next-change',source_root=source)


def test_real_candidate_archive_without_optional_proof_merges(tmp_path):
    """Exercise the real CLI boundary, not just a successful classification."""
    import shutil
    import subprocess
    from test_archive_baseline_transition import guard
    if not shutil.which('openspec'):
        pytest.skip('OpenSpec CLI required for real merge integration')
    root = tmp_path.resolve()
    old, archived, _ = scene(root)
    active = root / 'openspec/changes/next-change'
    active.parent.mkdir(parents=True, exist_ok=True)
    archived.rename(active)
    put(active / 'trace.md', '---\nstatus: applied\n---\n')
    put(active / 'proposal.md', '# 隔离验证\n\n## 背景\n验证兼容追加归档。\n')
    put(active / 'tasks.md', '- [x] 验证\n')
    original = (old / 'specs/cap/spec.md').read_text().replace('## ADDED Requirements', '## Requirements')
    put(root / 'openspec/specs/cap/spec.md', '# 能力规格\n\n## Purpose\n用于隔离验证完整兼容追加归档流程。\n\n' + original)
    key = ('cap', '能力')
    certificate(root, active, proof.delta_operations(old)[key][1], proof.delta_operations(active)[key][1])
    proof.journal_path(root, 'next-change').unlink()
    journal = proof.journal_path(root, 'old-change')
    record = json.loads(journal.read_text())
    record['expected_spec_hash'] = proof.tree_hash(root / 'openspec/specs')
    journal.write_text(json.dumps(record))
    path = compatible.proof_path(root, 'next-change', key)
    saved = path.read_bytes()
    path.unlink()
    before = proof.tree_hash(root)
    assert guard.classify(root, 'next-change', '2026-10-22') == 'merge'
    run = subprocess.run(['openspec', 'archive', 'next-change', '-y'], cwd=root, capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
    archives = proof.archive_paths(root, 'next-change')
    assert len(archives) == 1 and not active.exists(), run.stdout
    proof.verify_delta_effects(archives[0] / 'specs', root / 'openspec/specs')


@pytest.mark.parametrize('kind', ['MODIFIED', 'REMOVED'])
def test_same_requirement_successor_without_certificate_preserves_history(tmp_path, kind):
    old, new, _ = scene(tmp_path)
    compatible.proof_path(tmp_path, 'next-change', ('cap', '能力')).unlink()
    text = delta('能力').replace('ADDED', kind).replace('保留', '更新')
    put(new / 'specs/cap/spec.md', text)
    put(tmp_path / 'openspec/specs/cap/spec.md', text if kind == 'MODIFIED' else '')
    path = proof.journal_path(tmp_path, 'next-change')
    record = json.loads(path.read_text())
    record['delta_hash'] = proof.tree_hash(new / 'specs')
    record['expected_spec_hash'] = proof.tree_hash(tmp_path / 'openspec/specs')
    path.write_text(json.dumps(record))
    before = proof.tree_hash(tmp_path)
    assert proof.recovery_admission(tmp_path, 'old-change')['ready']
    assert proof.tree_hash(tmp_path) == before
    put(new / 'evidence/acceptance/run/result.txt', 'corrupt')
    assert not proof.recovery_admission(tmp_path, 'old-change')['ready']
