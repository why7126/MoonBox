"""The final archive write check rejects an input changed after preflight."""
import json
from types import SimpleNamespace

import pytest

from app.governance import archive_coordinator
from app.governance.archive_recovery import tree_hash


def test_concurrent_change_after_preflight_is_rejected_before_archive_write(tmp_path, monkeypatch):
    active = tmp_path / 'openspec/changes/sample-change'
    delta = active / 'specs/sample-cap/spec.md'
    delta.parent.mkdir(parents=True)
    delta.write_text('## ADDED Requirements\n### Requirement: 样本\n系统 SHALL 保留原约束。\n')
    baseline = tmp_path / 'openspec/specs'
    baseline.mkdir(parents=True)
    project = SimpleNamespace(root=tmp_path, source_root=tmp_path)
    monkeypatch.setattr(archive_coordinator, 'replacement_delivery_hash', lambda _folder: 'delivery')
    monkeypatch.setattr(archive_coordinator, 'evidence_digest', lambda _project, _folder: None)
    row = {'change_id': 'sample-change', 'stage': 'claimed', 'manifest': json.dumps({
        'delta': tree_hash(active / 'specs'), 'delivery': 'delivery',
        'acceptance': None, 'baseline': tree_hash(baseline), 'expected': 'unused',
    })}

    assert archive_coordinator.observe(project, row) == 'unmerged'
    delta.write_text(delta.read_text() + '\n#### Scenario: 并发修改\n- **WHEN** 归档前修改\n- **THEN** 拒绝旧结果\n')

    with pytest.raises(ValueError, match='^archive_inputs_changed$'):
        archive_coordinator.observe(project, row)
    assert active.is_dir()
    assert list((tmp_path / 'openspec/archive').glob('*-sample-change')) == []
