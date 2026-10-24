"""Rule-difference explanation cannot create an additional archive gate."""
from pathlib import Path
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, insert, select, func, text
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.chat.service import identity
from app.governance.controlled_successor import authority
from app.governance.replacement_proof import canonical, digest
from app.governance.rule_change_schema import confirmations, events


ROOT = Path(__file__).resolve().parents[3]


def owner_table(engine):
    with engine.begin() as connection:
        connection.execute(text('CREATE TABLE admin_spaces (id VARCHAR(64) PRIMARY KEY, owner_id VARCHAR(64))'))
        connection.execute(text("INSERT INTO admin_spaces VALUES ('space', 'owner')"))


def test_legacy_claimed_operation_only_resumes_its_original_path(monkeypatch):
    from app.chat.service import ChatError
    from app.governance import replacement_archive_api as legacy
    from app.governance.replacement_schema import proposals

    engine = create_engine('sqlite://')
    proposals.metadata.create_all(engine, tables=[proposals, confirmations])
    project = SimpleNamespace(space_id='space', repository_id='repo', key='legacy-scope')
    monkeypatch.setattr(legacy.scope, 'authorize', lambda *args, **kwargs: project)
    monkeypatch.setattr(legacy, 'object_access', lambda *args, **kwargs: None)
    resumed = []
    monkeypatch.setattr(legacy, 'execute', lambda _db, **kwargs: resumed.append(kwargs) or {
        'operation_id': kwargs['operation_id'], 'stage': 'completed', 'revision': 2, 'replayed': True})
    payload = legacy.ArchiveRequest(proposal_id='legacy-proposal', expected_revision=1,
        proposal_digest='a'*64, idempotency_key='original-operation', confirmed=True)
    request = SimpleNamespace(state=SimpleNamespace(chat_request_id='test-request'))
    with Session(engine) as db:
        db.execute(insert(proposals).values(**{**identity(), 'id': 'legacy-proposal'},
            scope_key='legacy-scope', space_id='space', repository_id='repo',
            binding_revision='old-binding', change_id='legacy-change', digest='a'*64,
            body='{}', prepared_by='owner', revision=1, state='prepared'))
        db.commit()
        with pytest.raises(ChatError) as blocked:
            legacy.create(payload, request, {'id': 'owner'}, db)
        assert blocked.value.status == 409 and not resumed
        db.execute(update(proposals).where(proposals.c.id == 'legacy-proposal').values(state='claimed'))
        db.commit()
        first = legacy.create(payload, request, {'id': 'owner'}, db).data
        second = legacy.create(payload, request, {'id': 'owner'}, db).data
        assert first['operation_id'] == second['operation_id']
        assert first['replayed'] and second['replayed'] and len(resumed) == 2
        assert db.scalar(select(func.count()).select_from(confirmations)) == 0


def test_bug0063_is_archived_and_not_an_active_candidate():
    from app.governance.rule_change import conflicts
    archive = ROOT/'openspec/archive/2026-10-23-fix-compatible-requirement-successor'
    assert archive.is_dir()
    assert not (ROOT/'openspec/changes/fix-compatible-requirement-successor').exists()
    project = SimpleNamespace(root=ROOT)
    with pytest.raises(ValueError, match='rule_change_candidate_missing_or_ambiguous'):
        conflicts(project, 'fix-compatible-requirement-successor')


def test_retired_decision_does_not_write_confirmation(monkeypatch):
    from app.chat.service import ChatError
    from app.governance import rule_change_api as api
    engine = create_engine('sqlite://')
    confirmations.metadata.create_all(engine, tables=[confirmations, events])
    payload = api.Decision(space_id='space', repository_id='repo',
        change_id='fix-compatible-requirement-successor', content_digest='a'*64,
        action='confirm', request_key='old-client')
    with Session(engine) as db:
        with pytest.raises(ChatError) as blocked:
            api.decide(payload, SimpleNamespace(state=SimpleNamespace()), {'id': 'owner'})
        assert blocked.value.status == 409
        assert db.scalar(select(func.count()).select_from(confirmations)) == 0
        assert db.scalar(select(func.count()).select_from(events)) == 0


def test_difference_view_follows_shared_admission_without_extra_proof(monkeypatch):
    from app.governance import rule_change_api as api, archive_admission, archive_recovery, change_index
    project = SimpleNamespace(root=ROOT, source_root=ROOT, key='test-scope',
        binding_revision='test-binding', space_id='space', repository_id='repo')
    monkeypatch.setattr(api, 'conflicts', lambda *_: [{'key': ('cap', '规则一'),
        'operation': 'MODIFIED', 'before': '原文', 'after': '修改后',
        'protected_changes': ['original'], 'supported': False}])
    monkeypatch.setattr(archive_admission, 'change_acceptance', lambda *_args, **_kwargs: {'ready': True})
    monkeypatch.setattr(archive_recovery, 'recovery_admission', lambda *_args, **_kwargs: {'ready': True})
    monkeypatch.setattr(change_index, 'ChangeIndex', lambda _root: SimpleNamespace(
        records={'new-unarchived-change': object()}, acceptance_source_reason=lambda _record, **_kwargs: None))
    engine = create_engine('sqlite://')
    with Session(engine) as db:
        view = api.describe(db, project, {'id': 'owner'}, 'new-unarchived-change')
    assert view['before'] == '原文' and view['after'] == '修改后'
    assert view['state'] == 'ready' and view['archive_ready'] is True
    assert 'can_confirm' not in view


def test_difference_view_keeps_acceptance_blocker(monkeypatch):
    from app.governance import rule_change_api as api, archive_admission, archive_recovery, change_index
    project = SimpleNamespace(root=ROOT, source_root=ROOT, key='test-scope',
        binding_revision='test-binding', space_id='space', repository_id='repo')
    monkeypatch.setattr(api, 'conflicts', lambda *_: [{'key': ('cap', '规则一'),
        'operation': 'MODIFIED', 'before': '原文', 'after': '修改后',
        'protected_changes': ['original']}])
    monkeypatch.setattr(archive_admission, 'change_acceptance', lambda *_args, **_kwargs:
                        {'ready': False, 'reason': '验收证据不完整'})
    monkeypatch.setattr(archive_recovery, 'recovery_admission', lambda *_args, **_kwargs: {'ready': True})
    monkeypatch.setattr(change_index, 'ChangeIndex', lambda _root: SimpleNamespace(
        records={'new-unarchived-change': object()}, acceptance_source_reason=lambda _record, **_kwargs: None))
    engine = create_engine('sqlite://')
    with Session(engine) as db:
        view = api.describe(db, project, {'id': 'owner'}, 'new-unarchived-change')
    assert view['archive_ready'] is False and view['archive_reason'] == '验收证据不完整'


def test_difference_view_keeps_delivery_source_blocker(monkeypatch):
    from app.governance import rule_change_api as api, archive_admission, archive_recovery, change_index
    project = SimpleNamespace(root=ROOT, source_root=ROOT, key='test-scope',
        binding_revision='test-binding', space_id='space', repository_id='repo')
    monkeypatch.setattr(api, 'conflicts', lambda *_: [{'key': ('cap', '规则一'),
        'operation': 'MODIFIED', 'before': '原文', 'after': '修改后',
        'protected_changes': ['original']}])
    monkeypatch.setattr(archive_admission, 'change_acceptance', lambda *_args, **_kwargs: {'ready': True})
    monkeypatch.setattr(archive_recovery, 'recovery_admission', lambda *_args, **_kwargs: {'ready': True})
    monkeypatch.setattr(change_index, 'ChangeIndex', lambda _root: SimpleNamespace(
        records={'new-unarchived-change': object()},
        acceptance_source_reason=lambda _record, **_kwargs: '验收来源待核实：未找到交付验证记录'))
    with Session(create_engine('sqlite://')) as db:
        view = api.describe(db, project, {'id': 'owner'}, 'new-unarchived-change')
    assert view['archive_ready'] is False
    assert view['archive_reason'] == '验收来源待核实：未找到交付验证记录'


def test_existing_v2_archived_proof_remains_readable(tmp_path, monkeypatch):
    from app.governance import rule_change
    from app.governance.archive_recovery import tree_hash
    change = 'fix-legacy'
    key = ('cap', 'rule')
    folder = tmp_path/'openspec/archive'/change
    (folder/'specs').mkdir(parents=True)
    (folder/'specs'/'delta.md').write_text('legacy')
    project = SimpleNamespace(root=tmp_path, key='scope', binding_revision='binding')
    content = {'change_id': change, 'capability': key[0], 'requirement': key[1],
        'before': 'old', 'after': 'new', 'delta_sha256': tree_hash(folder/'specs')}
    monkeypatch.setattr(rule_change, 'supported', lambda *_: True)
    engine = create_engine('sqlite://')
    confirmations.metadata.create_all(engine, tables=[confirmations])
    owner_table(engine)
    record = {**identity(), 'scope_key': project.key, 'space_id': 'space',
        'repository_id': 'repo', 'binding_revision': project.binding_revision,
        'change_id': change, 'content_digest': digest(content),
        'body': canonical(content).decode(), 'state': 'confirmed',
        'revision': 1, 'actor_id': 'owner', 'reason': ''}
    with Session(engine) as db:
        db.execute(insert(confirmations).values(**record)); db.commit()
        proof = rule_change.proof_path(tmp_path, change, key)
        proof.parent.mkdir(parents=True)
        proof.write_bytes(canonical({'schema_version': 2, 'content': content,
                                     'confirmation_id': record['id']}))
        with authority(db, project, 'owner'):
            certificate = rule_change.verify(tmp_path, change, folder, key, 'old', 'new')
            assert certificate['rule_change']['schema_version'] == 2
            assert certificate['proof_sha256']
        proof.write_text('tampered')
        with authority(db, project, 'owner'), pytest.raises((ValueError, TypeError)):
            rule_change.verify(tmp_path, change, folder, key, 'old', 'new')


def test_candidate_preflight_uses_normal_acceptance_without_extra_certificate(tmp_path, monkeypatch):
    from app.governance import compatible_successor
    archived = tmp_path/'openspec/archive/2026-10-23-old-change'
    active = tmp_path/'openspec/changes/new-change'
    for folder, body in ((archived, '旧规则'), (active, '修改后的规则')):
        spec = folder/'specs/sample-cap/spec.md'
        spec.parent.mkdir(parents=True)
        spec.write_text('## MODIFIED Requirements\n\n### Requirement: 样本规则\n系统 SHALL '+body+'。\n'
                        '\n#### Scenario: 样本\n- **WHEN** 输入有效\n- **THEN** 输出安全结果\n')
    (archived/'trace.md').write_text('---\nchange_id: old-change\nstatus: archived\n---\n')
    called = []
    monkeypatch.setattr(compatible_successor, 'acceptance_binding',
                        lambda *_args, **_kwargs: called.append('normal') or 'accepted')
    assert compatible_successor.preflight(tmp_path, 'new-change') == []
    assert called == ['normal']
    monkeypatch.setattr(compatible_successor, 'acceptance_binding',
                        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError('missing acceptance')))
    blockers = compatible_successor.preflight(tmp_path, 'new-change')
    assert len(blockers) == 1 and '正常验收' in blockers[0]['reason']
