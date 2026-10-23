"""真实输入形态的投影回归；隔离样本，不替代部署页面验收。"""
import json
import shutil
import pytest
from app.governance.acceptance_evidence import fingerprint, input_bytes, readiness, readiness_reason
from app.governance.archive_admission import change_acceptance


def sample(tmp_path):
    source, projection = tmp_path / 'source', tmp_path / 'projection'
    change = 'fix-projection-sample'
    folder = source / 'openspec/changes' / change
    folder.mkdir(parents=True)
    (folder / 'trace.md').write_text('---\nstatus: applied\n---\n')
    inputs = ['AGENTS.md', '.gitignore', 'tests/unit/check.py']
    for relative in inputs:
        p = source / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('original')
    check = {'id': 'AC-001', 'kind': 'command', 'argv': ['check'], 'inputs': inputs}
    (folder / 'acceptance-plan.json').write_text(json.dumps({'schema_version': 1, 'change_id': change, 'checks': [check]}))
    evidence = folder / 'evidence/acceptance/run'
    evidence.mkdir(parents=True)
    (evidence / 'manifest.json').write_text(json.dumps({'run_id': 'run', 'status': 'passed', 'scope': 'complete',
        'checks': [{'id': 'AC-001', 'status': 'passed', 'fingerprint': fingerprint(source, check)}]}))
    shutil.copytree(source / 'openspec', projection / 'openspec')
    return source, projection, change


@pytest.mark.parametrize('relative', ['AGENTS.md', '.gitignore', 'tests/unit/check.py'])
@pytest.mark.parametrize('mutation', ['unchanged', 'changed', 'missing', 'escape'])
def test_deployed_root_inputs_and_diagnostics(tmp_path, relative, mutation):
    source, projection, change = sample(tmp_path)
    p = source / relative
    if mutation == 'changed':
        p.write_text('new')
    elif mutation == 'missing':
        p.unlink()
    elif mutation == 'escape':
        outside = tmp_path / 'private'; outside.write_text('secret')
        p.unlink(); p.symlink_to(outside)
    result = readiness(projection, change, source_root=source)
    admission = change_acceptance(projection, change, source_root=source)
    assert admission['ready'] == (mutation == 'unchanged')
    assert admission['reason'] == readiness_reason(result)
    if mutation == 'unchanged':
        assert result['status'] == 'ready' and admission['reason'] is None
    else:
        assert result['stale'] == ['AC-001']
        assert 'AC-001' in admission['reason'] and '验收报告' in admission['reason']
        assert str(tmp_path) not in admission['reason'] and 'secret' not in admission['reason']
        assert {'changed': '已变化', 'missing': '输入缺失', 'escape': '不可读取'}[mutation] in admission['reason']


def test_missing_manifest_and_unknown_reason(tmp_path):
    source, projection, change = sample(tmp_path)
    shutil.rmtree(projection / 'openspec/changes' / change / 'evidence')
    result = change_acceptance(projection, change, source_root=source)
    assert not result['ready'] and '尚无完整验收记录' in result['reason']
    assert '待核查' in readiness_reason({'status': 'blocked'})
    (projection / 'openspec/changes' / change / 'acceptance-plan.json').write_text('invalid')
    result = change_acceptance(projection, change, source_root=source)
    assert not result['ready'] and '待核查' in result['reason']


def test_reason_redacts_untrusted_paths_and_codes():
    reason = readiness_reason({'status': 'blocked', 'diagnostics': [
        {'ac_id': 'AC-001', 'code': '/private/secret', 'paths': ['/private/password', '../escape', '.env', '.aws/key', 'tests/check.py']}]})
    assert 'tests/check.py' in reason
    for secret in ['/private', 'password', '../', '.env', '.aws']:
        assert secret not in reason
    assert '待核查' in reason


def test_governance_root_not_replaced_and_missing_binding_blocks(tmp_path):
    source, projection, change = sample(tmp_path)
    assert readiness(projection, change)['status'] == 'blocked'
    (source / 'rules').mkdir(); (source / 'rules/a.md').write_text('source')
    assert input_bytes(projection, {}, 'rules/a.md', source_root=source) == b'<missing>'
    (projection / 'rules').mkdir(); (projection / 'rules/a.md').write_text('projection')
    assert input_bytes(projection, {}, 'rules/a.md', source_root=source) == b'projection'
