"""An accepted successor cannot remove obligations from a completed rule."""
from pathlib import Path

from app.governance.archive_admission import change_acceptance, protected_rule_integrity


def _sample(root: Path, operation: str, body: str) -> None:
    historical = root / 'openspec/archive/2026-10-24-protected-rule'
    old = historical / 'specs/sample-cap/spec.md'
    old.parent.mkdir(parents=True)
    old.write_text('''## ADDED Requirements

### Requirement: 保留验收保护
系统 SHALL 检查权限和验收证据。

#### Scenario: 原场景
- **WHEN** 对象归档
- **THEN** 检查权限和验收证据
''')
    (historical / 'trace.md').write_text('---\nstatus: archived\nchange_id: protected-rule\n---\n# 历史记录\n')
    (historical / 'tasks.md').write_text('# 任务\n- [x] 完成\n')
    candidate = root / 'openspec/changes/next-rule'
    delta = candidate / 'specs/sample-cap/spec.md'
    delta.parent.mkdir(parents=True)
    delta.write_text(f'## {operation} Requirements\n\n### Requirement: 保留验收保护\n{body}\n')
    (candidate / 'trace.md').write_text('---\nstatus: applied\n---\n# 当前记录\n')
    baseline = root / 'openspec/specs/sample-cap/spec.md'
    baseline.parent.mkdir(parents=True)
    baseline.write_text('''## Purpose
隔离规则。

## Requirements

### Requirement: 保留验收保护
系统 SHALL 检查权限和验收证据。

#### Scenario: 原场景
- **WHEN** 对象归档
- **THEN** 检查权限和验收证据
''')


def test_destructive_successor_is_blocked_even_with_other_evidence_ready(tmp_path):
    _sample(tmp_path, 'MODIFIED', '''系统 SHALL 只记录操作，不检查验收证据。

#### Scenario: 弱化场景
- **WHEN** 对象归档
- **THEN** 忽略权限和验收证据''')
    result = change_acceptance(tmp_path, 'next-rule')
    assert result['ready'] is False
    assert result['recovery_reason'] == 'archive_requirement_conflict'
    assert result['diagnostics'][0]['protected_changes'] == ['protected-rule']


def test_scenario_append_preserves_original_obligations(tmp_path):
    _sample(tmp_path, 'MODIFIED', '''系统 SHALL 检查权限和验收证据。

#### Scenario: 原场景
- **WHEN** 对象归档
- **THEN** 检查权限和验收证据

#### Scenario: 新场景
- **WHEN** 新对象归档
- **THEN** 继续检查权限和验收证据''')
    assert protected_rule_integrity(tmp_path, 'next-rule') == {'ready': True}


def test_removing_protected_requirement_is_blocked(tmp_path):
    _sample(tmp_path, 'REMOVED', '''系统 SHALL 检查权限和验收证据。

#### Scenario: 原场景
- **WHEN** 对象归档
- **THEN** 检查权限和验收证据''')
    assert protected_rule_integrity(tmp_path, 'next-rule')['recovery_reason'] == 'archive_requirement_conflict'
