"""Same-scenario regression: progress, reuse, evidence and interruption boundaries."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import opsx_acceptance as acceptance


def setup(tmp_path, checks, **extra):
    directory = tmp_path / 'openspec/changes/probe'
    directory.mkdir(parents=True)
    (tmp_path / 'input.md').write_text('# 条件\n\n## A\n甲\n\n## B\n乙\n')
    plan = {'schema_version': 1, 'orchestration_version': 1, 'change_id': 'probe', 'checks': checks, **extra}
    (directory / 'acceptance-plan.json').write_text(json.dumps(plan))
    return directory


def check(name, **extra):
    return {'id': name, 'kind': 'command', 'inputs': ['input.md'],
            'argv': [sys.executable, '-c', 'pass'], **extra}


def manifest(root, result):
    return json.loads((root / result['path'] / 'manifest.json').read_text())


def test_local_missing_evidence_does_not_block_independent_check(tmp_path):
    setup(tmp_path, [check('AC-1', artifacts=['missing.md']), check('AC-2')])
    result = acceptance.run_acceptance(tmp_path, 'probe', None)
    rows = manifest(tmp_path, result)['checks']
    assert [r['status'] for r in rows] == ['blocked', 'passed']
    assert rows[0]['collection_state'] == 'pending_collection'
    assert result['scope'] == 'diagnostic'
    assert acceptance.readiness(tmp_path, 'probe')['status'] == 'blocked'
    (tmp_path / 'missing.md').write_text('已采集')
    full = acceptance.run_acceptance(tmp_path, 'probe', None)
    assert full['status'] == 'passed' and full['metrics']['reused'] == 1


def test_pending_turn_queue_is_not_a_fake_turn(tmp_path):
    setup(tmp_path, [{'id': 'AC-1', 'kind': 'product_turn', 'inputs': ['input.md'],
                      'turn_id': None, 'command_contains': 'probe'}])
    import sqlite3
    db = tmp_path / 'product.db'
    sqlite3.connect(db).close()
    queue = acceptance.acceptance_queue(tmp_path, 'probe', db)
    assert queue['pending_collection'] == ['AC-1']
    run = acceptance.run_acceptance(tmp_path, 'probe', db)
    assert run['pending_collection'] == ['AC-1']
    assert run['status'] == 'blocked'


def test_dependencies_topological_order_and_local_block(tmp_path):
    setup(tmp_path, [check('AC-2', depends_on=['AC-1']), check('AC-1', artifacts=['missing.md']), check('AC-3')])
    rows = manifest(tmp_path, acceptance.run_acceptance(tmp_path, 'probe', None))['checks']
    assert rows[0]['reason'] == 'dependency-blocked'
    assert rows[2]['status'] == 'passed'


def test_cycles_rejected_before_execution(tmp_path):
    directory = setup(tmp_path, [check('AC-1', depends_on=['AC-2']), check('AC-2', depends_on=['AC-1'])])
    with pytest.raises(ValueError, match='cyclic'):
        acceptance.read_plan(directory)


def test_sections_invalidate_only_affected_ac_and_dependents(tmp_path):
    setup(tmp_path, [check('AC-1', input_sections={'input.md': ['## A']}),
                     check('AC-2', input_sections={'input.md': ['## B']}),
                     check('AC-3', depends_on=['AC-1'], input_sections={'input.md': ['## B']})])
    assert acceptance.run_acceptance(tmp_path, 'probe', None)['status'] == 'passed'
    p = tmp_path / 'input.md'
    p.write_text(p.read_text().replace('甲', '甲修改'))
    assert acceptance.readiness(tmp_path, 'probe')['stale'] == ['AC-1', 'AC-3']
    assert acceptance.run_acceptance(tmp_path, 'probe', None)['metrics']['reused'] == 1


def test_ambiguous_section_fails_closed(tmp_path):
    setup(tmp_path, [check('AC-1', input_sections={'input.md': ['## A']})])
    (tmp_path / 'input.md').write_text('## A\n甲\n## A\n乙\n')
    with pytest.raises(ValueError, match='ambiguous'):
        acceptance.run_acceptance(tmp_path, 'probe', None)


def test_same_scenarios_dedupe_and_per_ac_effects(tmp_path):
    directory = setup(tmp_path, [check('AC-1'), check('AC-2'), check('AC-3')])
    baseline = acceptance.run_acceptance(tmp_path, 'probe', None)
    assert baseline['metrics']['command_executions'] == 3
    path = directory / 'acceptance-plan.json'
    plan = json.loads(path.read_text())
    for c in plan['checks']:
        c['deduplicate'] = True
    plan['checks'][2]['effects'] = [{'kind': 'exists', 'path': 'missing-effect.md'}]
    path.write_text(json.dumps(plan))
    optimized = acceptance.run_acceptance(tmp_path, 'probe', None)
    assert optimized['metrics']['command_executions'] == 1
    assert optimized['metrics']['deduplicated'] == 2
    assert optimized['status'] == 'failed'
    rows = manifest(tmp_path, optimized)['checks']
    assert [r['status'] for r in rows] == ['passed', 'passed', 'failed']


def test_checkpoint_survives_interruption(tmp_path, monkeypatch):
    setup(tmp_path, [check('AC-1'), check('AC-2')])
    real = acceptance.run_command
    calls = []
    def interrupted(c, root):
        calls.append(c)
        if len(calls) == 2:
            raise KeyboardInterrupt()
        return real(c, root)
    monkeypatch.setattr(acceptance, 'run_command', interrupted)
    with pytest.raises(KeyboardInterrupt):
        acceptance.run_acceptance(tmp_path, 'probe', None)
    assert acceptance.readiness(tmp_path, 'probe')['status'] == 'blocked'
    monkeypatch.setattr(acceptance, 'run_command', real)
    resumed = acceptance.run_acceptance(tmp_path, 'probe', None)
    assert resumed['status'] == 'passed'
    assert resumed['metrics']['command_executions'] == 1
    assert resumed['metrics']['reused'] == 1


def test_database_alias_used_in_preflight(tmp_path, monkeypatch):
    setup(tmp_path, [{'id': 'AC-1', 'kind': 'product_turn', 'inputs': ['input.md'],
                      'turn_id': 'actual-turn', 'command_contains': 'probe', 'product_db': 'isolated'}])
    db = tmp_path / 'test.db'; db.touch()
    seen = []
    def read(c, database):
        seen.append(database)
        return {'status': 'passed', 'reason': 'same-turn-complete'}
    monkeypatch.setattr(acceptance, 'run_product_turn', read)
    assert acceptance.run_acceptance(tmp_path, 'probe', None, db_aliases={'isolated': db})['status'] == 'passed'
    assert seen == [db]


def test_environment_change_invalidates_results(tmp_path):
    directory = setup(tmp_path, [check('AC-1')], environment='isolated')
    assert acceptance.run_acceptance(tmp_path, 'probe', None)['status'] == 'passed'
    path = directory / 'acceptance-plan.json'; plan = json.loads(path.read_text())
    plan['environment'] = 'original-deployment'; path.write_text(json.dumps(plan))
    assert acceptance.readiness(tmp_path, 'probe')['stale'] == ['AC-1']


def test_environment_contract_requires_safe_lifecycle(tmp_path):
    directory = setup(tmp_path, [check('AC-1')], environment_contract={'deployment': 'isolated'})
    with pytest.raises(ValueError, match='environment_contract'):
        acceptance.read_plan(directory)


def test_archive_preview_does_not_write_source_or_journal(tmp_path, monkeypatch):
    script = Path(__file__).resolve().parents[2] / 'scripts/archive-recovery-guard.py'
    spec = importlib.util.spec_from_file_location('archive_guard', script)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    directory = setup(tmp_path, [check('AC-1')])
    (tmp_path / 'openspec/specs').mkdir()
    before = module.tree_hash(tmp_path)
    def fake_run(argv, cwd, **kwargs):
        assert Path(cwd) != tmp_path
        (Path(cwd) / 'openspec/specs/merged.md').write_text('临时规格')
        archive = Path(cwd) / 'openspec/archive/2026-10-20-probe'
        archive.parent.mkdir(parents=True)
        __import__('shutil').move(Path(cwd) / 'openspec/changes/probe', archive)
        return type('Result', (), {'returncode': 0, 'stdout': '', 'stderr': ''})()
    monkeypatch.setattr(module.subprocess, 'run', fake_run)
    assert module.expected_spec_hash(tmp_path, 'probe')
    assert module.tree_hash(tmp_path) == before
    assert not (tmp_path / 'openspec/archive/.archive-recovery').exists()


def test_command_can_produce_its_declared_evidence(tmp_path):
    setup(tmp_path, [check('AC-1', argv=[sys.executable, '-c', "from pathlib import Path; Path('result.md').write_text('证据')"],
                          artifacts=['result.md'], produces_artifacts=['result.md'])])
    assert acceptance.run_acceptance(tmp_path, 'probe', None)['status'] == 'passed'


def test_pending_collection_cannot_be_passed_by_command_probe(tmp_path):
    setup(tmp_path, [check('AC-1', collection={'state': 'pending'})])
    result = acceptance.run_acceptance(tmp_path, 'probe', None)
    assert result['pending_collection'] == ['AC-1']
    assert result['metrics']['command_executions'] == 0


def test_activity_rejects_raw_text_and_aggregates_phases(tmp_path):
    p = tmp_path / 'activity.json'
    p.write_text(json.dumps([{'phase': 'collection', 'duration_ms': 45, 'human_intervention': True}]))
    assert acceptance.activity_summary(p)['phase_ms']['collection'] == 45
    assert acceptance.activity_summary(p)['human_interventions'] == 1
    p.write_text(json.dumps([{'phase': 'collection', 'duration_ms': 45, 'prompt': 'private'}]))
    with pytest.raises(ValueError, match='raw text'):
        acceptance.activity_summary(p)


def test_skill_contract_detects_stop_and_sync_regressions(tmp_path, monkeypatch):
    script = Path(__file__).resolve().parents[2] / 'scripts/validate-agent-context-budget.py'
    spec = importlib.util.spec_from_file_location('budget_validator', script)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    actual = module.SKILLS_DIR
    for name in ['opsx-accept', 'opsx-archive', 'workflow-sync']:
        p = tmp_path / name / 'SKILL.md'; p.parent.mkdir()
        p.write_text((actual / name / 'SKILL.md').read_text())
    monkeypatch.setattr(module, 'SKILLS_DIR', tmp_path)
    assert module.validate_acceptance_orchestration_contract() == []
    p = tmp_path / 'opsx-accept/SKILL.md';p.write_text(p.read_text().replace('--queue', '--old'))
    assert module.validate_acceptance_orchestration_contract()


def test_legacy_plan_fingerprint_is_unchanged(tmp_path):
    import hashlib
    directory = setup(tmp_path, [check('AC-1')], environment='old-environment', preflight=[[sys.executable, '-c', 'pass']])
    path = directory / 'acceptance-plan.json';plan = json.loads(path.read_text());plan.pop('orchestration_version');path.write_text(json.dumps(plan))
    original = plan['checks'][0]
    digest = hashlib.sha256(json.dumps(original, ensure_ascii=False, sort_keys=True).encode())
    for relative in original['inputs']:
        digest.update(relative.encode());digest.update((tmp_path / relative).read_bytes())
    assert acceptance.fingerprint(tmp_path, acceptance.read_plan(directory)['checks'][0]) == digest.hexdigest()


def test_collection_blocker_is_distinct_from_pending(tmp_path):
    setup(tmp_path, [check('AC-1', collection={'state': 'blocked'})])
    assert acceptance.acceptance_queue(tmp_path, 'probe', None)['queue'][0]['state'] == 'blocked'
    result = acceptance.run_acceptance(tmp_path, 'probe', None)
    assert result['scope'] == 'diagnostic'
    assert result['pending_collection'] == []


def test_failed_common_preflight_cannot_publish_complete_pass_from_cache(tmp_path):
    setup(tmp_path, [check('AC-1')], preflight=[[sys.executable, '-c', "from pathlib import Path; exit(0 if Path('healthy').exists() else 1)"]])
    healthy = tmp_path / 'healthy';healthy.touch()
    assert acceptance.run_acceptance(tmp_path, 'probe', None)['status'] == 'passed'
    healthy.unlink()
    result = acceptance.run_acceptance(tmp_path, 'probe', None)
    assert result['status'] == 'blocked' and result['scope'] == 'diagnostic'
    assert result['metrics']['command_executions'] == 0
