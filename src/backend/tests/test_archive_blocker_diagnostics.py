from app.chat.api import _chat_error_data
from app.chat.service import ChatError
import json
import pytest
from app.governance.archive_recovery import RecoveryBlocked, transition_chain


def test_archive_diagnostics_are_bounded_and_visible():
    valid = dict(type='change', id='fix-example', status='archive_requirement_conflict',
                 message='原条文兼容证明未通过', action_hint='核验原约束与新增场景', visible=True)
    hidden = {**valid, 'visible': False}
    private = {**valid, 'message': '/Users/example/secret'}
    oversized = {**valid, 'message': 'a' * 1501}
    error = ChatError(2509, '未就绪', 409, kind='archive_blocked',
                      details={'archive_blockers': [valid, hidden, private, oversized, {'type': 'unknown'}]})
    data = _chat_error_data(error, 'request')
    assert data['archive_blockers'] == [valid]
    assert data['request_id'] == 'request'


def test_plain_errors_keep_existing_shape():
    assert _chat_error_data(ChatError(2509, '未就绪', 409), 'request') is None


def test_overlapping_successor_without_valid_acceptance_reports_reviewable_conflict(tmp_path):
    root = tmp_path
    current = root / 'openspec/changes/current/specs/sample/spec.md'
    current.parent.mkdir(parents=True)
    current.write_text('## MODIFIED Requirements\n### Requirement: 样本规则\n系统 SHALL 核验。\n')
    archive = root / 'openspec/archive/2026-10-24-successor'
    delta = archive / 'specs/sample/spec.md'
    delta.parent.mkdir(parents=True)
    delta.write_text('## MODIFIED Requirements\n### Requirement: 样本规则\n系统 SHALL 核验并记录。\n')
    (archive / 'trace.md').write_text('---\nstatus: archived\n---\n')
    journal = root / 'openspec/archive/.archive-recovery/successor.json'
    journal.parent.mkdir(parents=True)
    journal.write_text(json.dumps({'change_id': 'successor', 'baseline_spec_hash': 'a' * 64,
                                   'expected_spec_hash': 'b' * 64}))
    with pytest.raises(RecoveryBlocked) as blocked:
        transition_chain(root, 'current', 'a' * 64, 'b' * 64, current.parents[2])
    assert blocked.value.code == 'archive_requirement_conflict'
    assert blocked.value.diagnostics == [{'change_id': 'successor', 'capability': 'sample', 'requirement': '样本规则'}]
