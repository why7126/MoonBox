"""跨 Change 的归档恢复必须有连续证据；产品和 CLI 使用同一只读门禁。"""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src/backend'))
from app.governance import archive_recovery as proof
from app.governance.archive_admission import change_acceptance
from app.governance.direct_command_journal import archive_spec_drift

spec = importlib.util.spec_from_file_location('recovery_cli', ROOT / 'scripts/archive-recovery-guard.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


def put(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def delta(capability):
    return ('## ADDED Requirements\n\n### Requirement: ' + capability + '\n'
            '系统 SHALL 保留明确的归档事实并核对对应规格内容。\n\n'
            '#### Scenario: 核验归档\n- **WHEN** 执行归档\n- **THEN** 规格结果匹配\n')


def own(root, issue=None):
    folder = root / 'openspec/changes/own-change'
    put(folder / 'trace.md', '---\nstatus: applied\n' + (f'req_id: {issue}\n' if issue else '') + '---\n')
    put(folder / 'specs/own-cap/spec.md', delta('自身能力'))
    (root / 'openspec/specs').mkdir(parents=True)
    record = {'schema_version': 1, 'change_id': 'own-change', 'archive_date': '2026-10-20',
              'active_change_hash': proof.tree_hash(folder), 'baseline_spec_hash': proof.tree_hash(root / 'openspec/specs'),
              'expected_spec_hash': 'e' * 64}
    path = proof.journal_path(root, 'own-change')
    put(path, json.dumps(record))
    return folder, path, record


def other(root, cid='other-change', capability='other-cap', complete=True):
    specs = root / 'openspec/specs'
    before = proof.tree_hash(specs)
    archive = root / 'openspec/archive' / ('2026-10-20-' + cid)
    put(archive / 'specs' / capability / 'spec.md', delta(cid))
    put(archive / 'trace.md', '---\nstatus: ' + ('archived' if complete else 'applied') + '\n---\n')
    put(specs / capability / 'spec.md', delta(cid).replace('## ADDED Requirements', '## Requirements'))
    record = {'schema_version': 3, 'change_id': cid, 'archive_date': '2026-10-20',
              'baseline_spec_hash': before, 'expected_spec_hash': proof.tree_hash(specs),
              'delta_hash': proof.tree_hash(archive / 'specs')}
    put(proof.journal_path(root, cid), json.dumps(record))
    return archive, record


@pytest.mark.parametrize('mode', ['legal', 'two', 'missing', 'same_module', 'overlap', 'tamper', 'duplicate', 'pending', 'broken', 'symlink', 'delta_tamper'])
def test_legacy_transition_admission_and_explicit_reprepare(tmp_path, monkeypatch, mode):
    folder, journal, original = own(tmp_path)
    archive, record = other(tmp_path, capability='own-cap' if mode in ('overlap', 'same_module') else 'other-cap', complete=mode != 'pending')
    if mode == 'overlap':
        p = archive / 'specs/own-cap/spec.md'
        p.write_text(delta('自身能力'))
        record['delta_hash'] = proof.tree_hash(archive / 'specs')
        proof.journal_path(tmp_path, 'other-change').write_text(json.dumps(record))
    if mode == 'two': other(tmp_path, 'third-change', 'third-cap')
    if mode == 'missing': proof.journal_path(tmp_path, 'other-change').unlink()
    if mode == 'tamper': put(tmp_path / 'openspec/specs/unexplained/spec.md', 'unknown edit')
    if mode == 'duplicate': shutil.copytree(archive, archive.with_name('2026-10-21-other-change'))
    if mode == 'broken':
        record['baseline_spec_hash'] = 'a' * 64
        proof.journal_path(tmp_path, 'other-change').write_text(json.dumps(record))
    if mode == 'symlink':
        p = archive / 'specs/other-cap/spec.md'; p.rename(p.with_suffix('.original')); p.symlink_to(p.with_suffix('.original'))
    if mode == 'delta_tamper': (archive / 'specs/other-cap/spec.md').write_text(delta('伪造'))
    expected = mode in ('legal', 'two', 'same_module')
    before = proof.tree_hash(tmp_path) if mode != 'symlink' else journal.read_text()
    assert change_acceptance(tmp_path, 'own-change')['ready'] == expected
    cli = subprocess.run([sys.executable, str(ROOT / 'scripts/validate-issue-acceptance-ready.py'), 'own-change', '--root', str(tmp_path)], capture_output=True, text=True)
    assert (cli.returncode == 0) == expected
    assert (proof.tree_hash(tmp_path) if mode != 'symlink' else journal.read_text()) == before
    # Active evidence can legitimately be refreshed, but only explicit reprepare writes.
    put(folder / 'verification.md', '本次复验通过')
    assert not change_acceptance(tmp_path, 'own-change')['ready']
    monkeypatch.setattr(guard, 'expected_spec_hash', lambda *args: 'f' * 64)
    if expected:
        guard.reprepare(tmp_path, 'own-change')
        updated = json.loads(journal.read_text())
        assert updated['previous_record'] == original
        assert len(updated['baseline_transition']) == (2 if mode == 'two' else 1)
        assert change_acceptance(tmp_path, 'own-change')['ready']
        assert guard.classify(tmp_path, 'own-change', '2026-10-20') == 'merge'
    else:
        with pytest.raises(ValueError): guard.reprepare(tmp_path, 'own-change')
        assert json.loads(journal.read_text()) == original


@pytest.mark.parametrize('stage', ['merged', 'archived'])
def test_completed_merge_can_resume_after_unrelated_archive(tmp_path, stage):
    folder, journal, record = own(tmp_path)
    put(tmp_path / 'openspec/specs/own-cap/spec.md', delta('自身能力'))
    record['expected_spec_hash'] = proof.tree_hash(tmp_path / 'openspec/specs')
    journal.write_text(json.dumps(record))
    if stage == 'archived': shutil.move(folder, tmp_path / 'openspec/archive/2026-10-20-own-change')
    other(tmp_path)
    assert guard.classify(tmp_path, 'own-change', '2026-10-20') == ('move-only' if stage == 'merged' else 'archived')
    assert not archive_spec_drift('own-change', tmp_path)
    with pytest.raises(ValueError): guard.reprepare(tmp_path, 'own-change')
    put(tmp_path / 'openspec/specs/own-cap/spec.md', 'corrupted own result')
    assert archive_spec_drift('own-change', tmp_path)
    assert not change_acceptance(tmp_path, 'own-change')['ready']


@pytest.mark.parametrize('kind', ['REQ', 'BUG'])
def test_issue_signed_acceptance_never_hides_recovery_block(tmp_path, kind):
    oid = kind + '-9900-test'; folder, journal, record = own(tmp_path)
    (folder / 'trace.md').write_text(f'---\nstatus: applied\n{"req_id" if kind == "REQ" else "bug_id"}: {oid}\n---\n')
    record['active_change_hash'] = proof.tree_hash(folder); journal.write_text(json.dumps(record))
    domain = 'requirements' if kind == 'REQ' else 'bugs'
    acceptance = tmp_path / f'issues/{domain}/review/{oid}/acceptance.md'
    put(acceptance, '---\nacceptance_status: passed\n---\n- [x] AC-001 已核验\n')
    other(tmp_path)
    assert change_acceptance(tmp_path, 'own-change')['ready']
    put(tmp_path / 'openspec/specs/unknown/spec.md', 'unproven')
    assert not change_acceptance(tmp_path, 'own-change')['ready']


def test_reprepare_race_keeps_original_journal(tmp_path, monkeypatch):
    folder, journal, record = own(tmp_path)
    other(tmp_path)
    def preview(*args):
        put(tmp_path / 'openspec/specs/concurrent/spec.md', 'late write')
        return 'f' * 64
    monkeypatch.setattr(guard, 'expected_spec_hash', preview)
    with pytest.raises(ValueError, match='inputs changed'): guard.reprepare(tmp_path, 'own-change')
    assert json.loads(journal.read_text()) == record


def test_real_openspec_independent_archives_keep_original_recoverable(tmp_path):
    """Real CLI merge in a disposable project; no model, no formal archive."""
    if not shutil.which('openspec'): pytest.skip('OpenSpec CLI unavailable')
    for cid in ['original-change', 'independent-change']:
        folder = tmp_path / 'openspec/changes' / cid
        put(folder / 'proposal.md', '# 归档回归\n\n## 背景\n隔离归档规格。\n')
        put(folder / 'tasks.md', '# 任务\n- [x] 验证\n')
        put(folder / 'trace.md', '---\nstatus: applied\nchange_id: ' + cid + '\nexecution:\n  completed_at: 2026-10-20 12:00:00\n---\n')
        put(folder / 'specs' / cid / 'spec.md', delta(cid))
    (tmp_path / 'openspec/specs').mkdir(parents=True)
    assert guard.classify(tmp_path, 'original-change', '2026-10-20') == 'merge'
    assert guard.classify(tmp_path, 'independent-change', '2026-10-20') == 'merge'
    run = subprocess.run(['openspec', 'archive', 'independent-change', '-y'], cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
    archive = proof.archive_paths(tmp_path, 'independent-change')[0]
    # Canonical archive keeps applied metadata, just like the formal repository.
    assert 'status: applied' in (archive / 'trace.md').read_text()
    assert guard.classify(tmp_path, 'original-change', '2026-10-20') == 'merge'
    assert change_acceptance(tmp_path, 'original-change')['ready']
    run = subprocess.run(['openspec', 'archive', 'original-change', '-y'], cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
    assert proof.recovery_state(tmp_path, 'original-change')['mode'] == 'archived'


def test_other_archives_can_supersede_each_other_without_touching_own_scope(tmp_path):
    folder, journal, record = own(tmp_path)
    other(tmp_path)
    before = proof.tree_hash(tmp_path / 'openspec/specs')
    archive = tmp_path / 'openspec/archive/2026-10-20-followup-change'
    body = delta('other-change').replace('ADDED', 'MODIFIED').replace('核对对应规格内容', '核对后续合法规格内容')
    put(archive / 'trace.md', '---\nstatus: archived\n---\n')
    put(archive / 'specs/other-cap/spec.md', body)
    put(tmp_path / 'openspec/specs/other-cap/spec.md', body)
    put(proof.journal_path(tmp_path, 'followup-change'), json.dumps({
        'change_id': 'followup-change', 'archive_date': '2026-10-20',
        'baseline_spec_hash': before, 'expected_spec_hash': proof.tree_hash(tmp_path / 'openspec/specs'),
        'delta_hash': proof.tree_hash(archive / 'specs')}))
    assert guard.classify(tmp_path, 'own-change', '2026-10-20') == 'merge'
    assert change_acceptance(tmp_path, 'own-change')['ready']


@pytest.mark.parametrize('mode', ['complete', 'missing_execution', 'pending_task', 'wrong_identity'])
def test_canonical_archive_retains_first_apply_facts(tmp_path, mode):
    own(tmp_path)
    archive, _ = other(tmp_path)
    completed = "  completed_at: '2026-10-20 12:00:00'\n" if mode != 'missing_execution' else ''
    identity = 'wrong-change' if mode == 'wrong_identity' else 'other-change'
    put(archive / 'trace.md', '---\nstatus: applied\nchange_id: ' + identity + '\nexecution:\n' + completed + '---\n')
    put(archive / 'tasks.md', '- [ ] pending\n' if mode == 'pending_task' else '- [x] completed\n')
    assert change_acceptance(tmp_path, 'own-change')['ready'] == (mode == 'complete')


@pytest.mark.parametrize('mutation', ['report', 'trace', 'spec', 'tasks', 'plan', 'identity', 'evidence', 'unknown', 'symlink', 'invalid_trace'])
def test_delivery_projection_preserves_real_input_gates(tmp_path, monkeypatch, mutation):
    folder, journal, _ = own(tmp_path)
    monkeypatch.setattr(guard, 'expected_spec_hash', lambda *args: 'f' * 64)
    guard.reprepare(tmp_path, 'own-change')
    if mutation == 'report':
        put(folder / 'evidence/acceptance/new/summary.md', '再次验收通过')
    elif mutation == 'trace':
        put(folder / 'trace.md', '---\nstatus: applied\nupdated_at: today\n---\n新的验收记录\n')
    elif mutation == 'identity':
        put(folder / 'trace.md', '---\nstatus: applied\nreq_id: REQ-9999-other\n---\n')
    elif mutation == 'invalid_trace':
        put(folder / 'trace.md', '---\nidentity: [\n---\n')
    elif mutation == 'symlink':
        (folder / 'evidence/acceptance').mkdir(parents=True)
        (folder / 'evidence/acceptance/link').symlink_to(folder / 'trace.md')
    else:
        name = {'spec': 'specs/own-cap/spec.md', 'tasks': 'tasks.md',
                'plan': 'acceptance-plan.json', 'evidence': 'evidence/visual.json',
                'unknown': 'unknown.md'}[mutation]
        put(folder / name, '实质输入变更')
    result = proof.recovery_admission(tmp_path, 'own-change')
    assert result['ready'] == (mutation in {'report', 'trace'})
    if mutation not in {'report', 'trace', 'symlink', 'invalid_trace'}:
        assert result['recovery_reason'] == 'archive_delivery_inputs_changed'
    if mutation == 'invalid_trace':
        assert result['recovery_reason'] == 'archive_recovery_record_invalid'


def test_reaccept_then_real_cli_archive_preserves_outputs(tmp_path):
    """Prepare -> accept twice -> append trace -> shared gate -> real CLI move."""
    if not shutil.which('openspec'):
        pytest.skip('OpenSpec CLI unavailable')
    sys.path.insert(0, str(ROOT / 'scripts'))
    import opsx_acceptance as acceptance
    folder, journal, _ = own(tmp_path)
    journal.unlink()
    put(folder / 'tasks.md', '- [x] 已完成\n')
    put(folder / 'proposal.md', '# 隔离完整归档验收\n')
    put(tmp_path / 'input.md', '稳定交付输入')
    put(folder / 'acceptance-plan.json', json.dumps({
        'schema_version': 1, 'change_id': 'own-change', 'checks': [
            {'id': 'AC-1', 'kind': 'command', 'inputs': ['input.md'],
             'argv': [sys.executable, '-c', 'pass']}]}))
    assert guard.classify(tmp_path, 'own-change', '2026-10-20') == 'merge'
    for _ in range(2):
        result = acceptance.run_acceptance(tmp_path, 'own-change', None)
        assert result['status'] == 'passed'
        assert result['archive_ready']
        with (folder / 'trace.md').open('a') as handle:
            handle.write('\n验收与用量收尾已完成\n')
        assert change_acceptance(tmp_path, 'own-change')['ready']
    archived_tree = proof.tree_hash(folder)
    run = subprocess.run(['openspec', 'archive', 'own-change', '-y'], cwd=tmp_path, capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
    assert not folder.exists()
    assert proof.tree_hash(proof.archive_paths(tmp_path, 'own-change')[0]) == archived_tree
    assert proof.recovery_state(tmp_path, 'own-change')['mode'] == 'archived'


def test_acceptance_pass_does_not_hide_stale_legacy_record(tmp_path):
    sys.path.insert(0, str(ROOT / 'scripts'))
    import opsx_acceptance as acceptance
    folder, journal, original = own(tmp_path)
    put(tmp_path / 'input.md', '稳定输入')
    put(folder / 'acceptance-plan.json', json.dumps({
        'schema_version': 1, 'change_id': 'own-change', 'checks': [
            {'id': 'AC-1', 'kind': 'command', 'inputs': ['input.md'],
             'argv': [sys.executable, '-c', 'pass']}]}))
    original['active_change_hash'] = proof.tree_hash(folder)
    journal.write_text(json.dumps(original))
    result = acceptance.run_acceptance(tmp_path, 'own-change', None)
    assert result['status'] == 'passed'
    assert result['archive_ready'] is False
    assert result['archive_admission']['recovery_reason'] == 'archive_legacy_record_stale'
    assert json.loads(journal.read_text()) == original


def test_derived_manifest_tampering_still_blocks_acceptance(tmp_path, monkeypatch):
    sys.path.insert(0, str(ROOT / 'scripts'))
    import opsx_acceptance as acceptance
    folder, journal, _ = own(tmp_path)
    put(tmp_path / 'input.md', '稳定输入')
    put(folder / 'acceptance-plan.json', json.dumps({
        'schema_version': 1, 'change_id': 'own-change', 'checks': [
            {'id': 'AC-1', 'kind': 'command', 'inputs': ['input.md'],
             'argv': [sys.executable, '-c', 'pass']}]}))
    monkeypatch.setattr(guard, 'expected_spec_hash', lambda *args: 'f' * 64)
    guard.reprepare(tmp_path, 'own-change')
    result = acceptance.run_acceptance(tmp_path, 'own-change', None)
    assert result['archive_ready']
    path = tmp_path / result['path'] / 'manifest.json'
    record = json.loads(path.read_text())
    record['checks'][0]['fingerprint'] = '0' * 64
    path.write_text(json.dumps(record))
    assert proof.recovery_admission(tmp_path, 'own-change')['ready']
    assert not change_acceptance(tmp_path, 'own-change')['ready']


@pytest.mark.parametrize('mode', ['moved', 'verification', 'tampered', 'ambiguous', 'incomplete', 'active_missing', 'symlink'])
def test_linked_archive_evidence_keeps_original_hash_gate(tmp_path, mode):
    import hashlib
    from app.governance.acceptance_evidence import artifacts_match
    archive = tmp_path / 'openspec/archive/2026-10-20-related-change'
    put(archive / 'trace.md', '---\nchange_id: related-change\nstatus: archived\n---\n')
    relative = 'verification.md' if mode == 'verification' else 'evidence/proof.json'
    artifact = archive / relative
    put(artifact, 'original')
    row = {'artifacts': [{'path': 'openspec/changes/related-change/' + relative,
                         'sha256': hashlib.sha256(b'original').hexdigest()}]}
    if mode == 'tampered': put(artifact, 'changed')
    if mode == 'ambiguous': shutil.copytree(archive, archive.with_name('2026-10-21-related-change'))
    if mode == 'incomplete': put(archive / 'trace.md', '---\nstatus: applied\n---\n')
    if mode == 'active_missing': (tmp_path / 'openspec/changes/related-change').mkdir(parents=True)
    if mode == 'symlink':
        put(archive / 'original.json', 'original')
        artifact.unlink()
        artifact.symlink_to(archive / 'original.json')
        with pytest.raises(ValueError): artifacts_match(tmp_path, row)
    else:
        assert artifacts_match(tmp_path, row) == (mode in {'moved', 'verification'})

@pytest.mark.parametrize('kind', ['REQ', 'BUG'])
@pytest.mark.parametrize('damage', [None, 'artifact', 'coverage', 'duplicate', 'delta'])
def test_cross_day_migrated_evidence_and_idempotent_resume(tmp_path, kind, damage):
    import hashlib
    oid = kind + '-9901-cross-day'
    folder, journal, record = own(tmp_path, oid)
    domain = 'requirements' if kind == 'REQ' else 'bugs'
    put(tmp_path / f'issues/{domain}/review/{oid}/acceptance.md',
        '---\nacceptance_status: passed\n---\n- [ ] AC-001 自动证据通过\n')
    artifact = 'openspec/changes/own-change/evidence/result.txt'
    put(folder / 'evidence/result.txt', 'verified')
    plan = {'schema_version': 1, 'change_id': 'own-change', 'issue_id': oid,
            'checks': [{'id': 'AC-001', 'kind': 'command', 'inputs': ['source.txt'],
                        'argv': ['true'], 'artifacts': [artifact]}]}
    put(folder / 'acceptance-plan.json', json.dumps(plan))
    manifest = {'status': 'passed', 'run_id': 'run1', 'checks': [{'id': 'AC-001', 'status': 'passed',
        'artifacts': [{'path': artifact, 'sha256': hashlib.sha256(b'verified').hexdigest()}]}]}
    put(folder / 'evidence/acceptance/run1/manifest.json', json.dumps(manifest))
    put(tmp_path / 'openspec/specs/own-cap/spec.md', delta('自身能力'))
    record.update(schema_version=4, input_projection=1, delivery_input_hash=proof.delivery_input_hash(folder),
                  delta_hash=proof.tree_hash(folder/'specs'), expected_spec_hash=proof.tree_hash(tmp_path/'openspec/specs'))
    journal.write_text(json.dumps(record))
    archived = tmp_path / 'openspec/archive/2026-10-21-own-change'
    shutil.move(folder, archived)
    if damage == 'artifact': (archived/'evidence/result.txt').write_text('tampered')
    if damage == 'coverage':
        manifest['checks'] = []; (archived/'evidence/acceptance/run1/manifest.json').write_text(json.dumps(manifest))
    if damage == 'duplicate': shutil.copytree(archived, archived.with_name('2026-10-22-own-change'))
    if damage == 'delta': (archived/'specs/own-cap/spec.md').write_text('tampered')
    result = change_acceptance(tmp_path, 'own-change')
    assert result['ready'] == (damage is None)
    if damage is None:
        assert result['source'] == 'evidence' and result['done'] == 1
        specs_before = proof.tree_hash(tmp_path/'openspec/specs')
        assert guard.classify(tmp_path, 'own-change', '2026-10-22') == 'archived'
        first = journal.read_bytes()
        assert json.loads(first)['archive_date'] == '2026-10-21'
        assert json.loads(first)['prepared_archive_date'] == '2026-10-20'
        assert guard.classify(tmp_path, 'own-change', '2026-10-23') == 'archived'
        assert journal.read_bytes() == first
        assert proof.tree_hash(tmp_path/'openspec/specs') == specs_before
