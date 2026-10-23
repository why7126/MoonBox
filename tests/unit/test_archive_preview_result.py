"""归档预演必须验证退出码以外的事实，所有副作用限于临时副本。"""
import importlib.util
import shutil
from pathlib import Path
from types import SimpleNamespace
import pytest

spec = importlib.util.spec_from_file_location('preview_guard', Path(__file__).resolve().parents[2] / 'scripts/archive-recovery-guard.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

@pytest.mark.parametrize('mode', ['aborted', 'noop', 'missing_merge', 'wrong_body', 'duplicate_archive', 'changed_archive', 'nonzero', 'success'])
def test_preview_requires_real_effects(tmp_path, monkeypatch, mode):
    active = tmp_path / 'openspec/changes/probe'
    delta = active / 'specs/example/spec.md'
    delta.parent.mkdir(parents=True)
    delta.write_text('## ADDED Requirements\n\n### Requirement: 新能力\n系统 MUST 核验结果。\n\n#### Scenario: 正常\n- **THEN** 结果成立\n')
    (tmp_path / 'openspec/specs').mkdir()
    before = guard.tree_hash(tmp_path)
    def fake(argv, cwd, **kwargs):
        root = Path(cwd) / 'openspec'
        if mode in ('aborted', 'noop', 'nonzero'):
            return SimpleNamespace(returncode=1 if mode == 'nonzero' else 0, stdout='Aborted. No files were changed.' if mode == 'aborted' else '', stderr='')
        archive = root / 'archive/2026-10-20-probe'
        archive.parent.mkdir()
        shutil.move(root / 'changes/probe', archive)
        if mode == 'duplicate_archive': shutil.copytree(archive, root / 'archive/2026-10-21-probe')
        if mode == 'changed_archive': (archive / 'unexpected').write_text('changed')
        if mode != 'missing_merge':
            merged = root / 'specs/example/spec.md'; merged.parent.mkdir()
            text = delta.read_text().replace('## ADDED Requirements', '## Requirements')
            merged.write_text(text.replace('核验结果', '错误内容') if mode == 'wrong_body' else text)
        return SimpleNamespace(returncode=0, stdout='', stderr='')
    monkeypatch.setattr(guard.subprocess, 'run', fake)
    if mode == 'success': assert guard.expected_spec_hash(tmp_path, 'probe')
    else:
        with pytest.raises(ValueError): guard.expected_spec_hash(tmp_path, 'probe')
    assert guard.tree_hash(tmp_path) == before


def test_removed_effect_must_be_absent(tmp_path):
    delta = tmp_path / 'delta/example/spec.md'; delta.parent.mkdir(parents=True)
    delta.write_text('## REMOVED Requirements\n### Requirement: 旧能力\n移除\n')
    merged = tmp_path / 'specs/example/spec.md'; merged.parent.mkdir(parents=True)
    merged.write_text('### Requirement: 旧能力\n仍存在\n')
    with pytest.raises(ValueError): guard.verify_delta_effects(tmp_path / 'delta', tmp_path / 'specs')
    merged.write_text('')
    guard.verify_delta_effects(tmp_path / 'delta', tmp_path / 'specs')

@pytest.mark.parametrize('mode', ['baseline', 'changed_specs', 'archive_exists', 'preview_failure'])
def test_reprepare_preserves_prior_record_and_rejects_unsafe_state(tmp_path, monkeypatch, mode):
    import json
    active = tmp_path / 'openspec/changes/probe'; active.mkdir(parents=True)
    (active / 'tasks.md').write_text('repaired')
    specs = tmp_path / 'openspec/specs'; specs.mkdir()
    journal = tmp_path / 'openspec/archive/.archive-recovery/probe.json'; journal.parent.mkdir(parents=True)
    record = {'change_id': 'probe', 'archive_date': '2026-10-20', 'baseline_spec_hash': guard.tree_hash(specs), 'expected_spec_hash': 'a' * 64, 'active_change_hash': 'old'}
    journal.write_text(json.dumps(record)); before = journal.read_text()
    if mode == 'changed_specs': (specs / 'external').write_text('change')
    if mode == 'archive_exists': (tmp_path / 'openspec/archive/2026-10-20-probe').mkdir()
    def preview(*args):
        if mode == 'preview_failure': raise ValueError('failed preview')
        return 'verified'
    monkeypatch.setattr(guard, 'expected_spec_hash', preview)
    if mode == 'baseline':
        guard.reprepare(tmp_path, 'probe')
        result = json.loads(journal.read_text())
        assert result['previous_record'] == record
        assert result['expected_spec_hash'] == 'verified'
    else:
        with pytest.raises(ValueError): guard.reprepare(tmp_path, 'probe')
        assert journal.read_text() == before
