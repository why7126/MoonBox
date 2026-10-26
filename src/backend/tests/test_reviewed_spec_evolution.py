"""Isolated acceptance trees prove evolution without waiving evidence/history."""
import hashlib
import json
import shutil
from types import SimpleNamespace

import pytest

from app.governance.acceptance_evidence import fingerprint
from app.governance.archive_admission import change_acceptance, protected_rule_integrity
from test_protected_rule_integrity import _sample

CHANGE = 'next-rule'
DELTA = f'openspec/changes/{CHANGE}/specs/sample-cap/spec.md'
BODY = '''系统 SHALL 按已评审的新业务策略执行并保留权限和验收。

#### Scenario: 新业务策略
- **WHEN** 执行业务
- **THEN** 使用新策略且检查权限和验收证据'''


def accepted(root, *, inputs=None, sections=None):
    _sample(root, 'MODIFIED', BODY)
    folder = root / 'openspec/changes' / CHANGE
    check = {'id': 'AC-001', 'kind': 'command', 'argv': ['isolated-test'],
             'inputs': inputs or [DELTA]}
    if sections:
        check['input_sections'] = sections
    (root / 'AGENTS.md').write_text('trusted source input')
    plan = {'schema_version': 1, 'change_id': CHANGE, 'checks': [check]}
    (folder / 'acceptance-plan.json').write_text(json.dumps(plan))
    evidence = folder / 'evidence/acceptance/run'
    evidence.mkdir(parents=True)
    manifest = {'run_id': 'run', 'status': 'passed', 'scope': 'complete',
                'checks': [{'id': 'AC-001', 'status': 'passed',
                            'fingerprint': fingerprint(root, check)}]}
    (evidence / 'manifest.json').write_text(json.dumps(manifest))
    return folder, evidence, manifest


@pytest.mark.parametrize('inputs', [[DELTA], [f'openspec/changes/{CHANGE}/specs']])
def test_current_evidence_allows_replacement_not_a_write(tmp_path, inputs):
    accepted(tmp_path, inputs=inputs)
    before = (tmp_path / 'openspec/specs/sample-cap/spec.md').read_bytes()
    assert change_acceptance(tmp_path, CHANGE)['ready']
    assert (tmp_path / DELTA).is_file()
    assert (tmp_path / 'openspec/specs/sample-cap/spec.md').read_bytes() == before
    assert not list((tmp_path / 'openspec/archive').glob(f'*-{CHANGE}'))


@pytest.mark.parametrize('fault', ['missing', 'failed', 'changed', 'tampered', 'uncovered', 'sections'])
def test_bad_evidence_or_partial_binding_cannot_allow_replacement(tmp_path, fault):
    inputs = ['AGENTS.md'] if fault == 'uncovered' else [DELTA]
    sections = {DELTA: ['### Requirement: 保留验收保护']} if fault == 'sections' else None
    folder, evidence, manifest = accepted(tmp_path, inputs=inputs, sections=sections)
    if fault == 'missing':
        (evidence / 'manifest.json').unlink()
    elif fault == 'failed':
        manifest['checks'][0]['status'] = 'failed'
        (evidence / 'manifest.json').write_text(json.dumps(manifest))
    elif fault == 'changed':
        (tmp_path / DELTA).write_text((tmp_path / DELTA).read_text() + '\n业务变化\n')
    elif fault == 'tampered':
        manifest['checks'][0]['artifacts'] = [{'path': str((evidence / 'result.txt').relative_to(tmp_path)),
                                              'sha256': hashlib.sha256(b'original').hexdigest()}]
        (evidence / 'result.txt').write_text('tampered')
        (evidence / 'manifest.json').write_text(json.dumps(manifest))
    assert not protected_rule_integrity(tmp_path, CHANGE)['ready']
    assert not change_acceptance(tmp_path, CHANGE)['ready']


@pytest.mark.parametrize('fault', ['duplicate', 'incomplete', 'malformed'])
def test_completed_unique_parseable_history_is_still_required(tmp_path, fault):
    accepted(tmp_path)
    old = tmp_path / 'openspec/archive/2026-10-24-protected-rule'
    if fault == 'duplicate':
        shutil.copytree(old, old.with_name('2026-10-25-protected-rule'))
    elif fault == 'incomplete':
        (old / 'trace.md').write_text('---\nstatus: in_progress\n---\n')
    else:
        (old / 'specs/sample-cap/spec.md').write_text('unparseable')
    assert not change_acceptance(tmp_path, CHANGE)['ready']


def test_removal_with_current_pass_still_cannot_use_modification_path(tmp_path):
    folder, evidence, manifest = accepted(tmp_path)
    path = tmp_path / DELTA
    path.write_text(path.read_text().replace('MODIFIED', 'REMOVED'))
    check = json.loads((folder / 'acceptance-plan.json').read_text())['checks'][0]
    manifest['checks'][0]['fingerprint'] = fingerprint(tmp_path, check)
    (evidence / 'manifest.json').write_text(json.dumps(manifest))
    assert not change_acceptance(tmp_path, CHANGE)['ready']


def test_source_projection_preserves_current_input_binding(tmp_path):
    source = tmp_path / 'source'; source.mkdir()
    accepted(source, inputs=[DELTA, 'AGENTS.md'])
    projection = tmp_path / 'projection'
    shutil.copytree(source / 'openspec', projection / 'openspec')
    assert change_acceptance(projection, CHANGE, source_root=source)['ready']
    (source / 'AGENTS.md').write_text('source changed')
    assert not change_acceptance(projection, CHANGE, source_root=source)['ready']


def test_difference_api_uses_real_current_evidence(tmp_path):
    from app.governance.rule_change_api import describe
    accepted(tmp_path)
    for domain in ('requirements', 'bugs'):
        registry = tmp_path / 'issues' / domain / '_registry.yaml'
        registry.parent.mkdir(parents=True)
        registry.write_text('entries: []\n')
    project = SimpleNamespace(root=tmp_path, source_root=tmp_path, key='isolated')
    data = describe(None, project, {'id': 'isolated-user'}, CHANGE)
    assert data['state'] == 'ready'
    assert data['protected_changes'] == ['protected-rule']
    (tmp_path / DELTA).write_text((tmp_path / DELTA).read_text() + '\nchanged\n')
    assert describe(None, project, {'id': 'isolated-user'}, CHANGE)['state'] == 'blocked'


@pytest.mark.parametrize('fault', ['revoked', 'readonly', 'disabled', 'cross-space', 'binding'])
def test_passing_evidence_does_not_grant_write_permission(tmp_path, monkeypatch, fault):
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import Session
    from app.chat.service import ChatError
    from app.governance import scope
    from app.governance.replacement_permissions import authorize_write

    accepted(tmp_path)
    assert change_acceptance(tmp_path, CHANGE)['ready']
    binding = {'governance_root': str(tmp_path.resolve())}
    monkeypatch.setattr(scope, 'repository_binding', lambda repo, space: binding
                        if (repo, space) == ('repo', 'space') else None)
    engine = create_engine('sqlite://')
    with Session(engine) as db:
        for statement in [
            'CREATE TABLE admin_users (id TEXT, status TEXT, deleted_at TEXT)',
            'CREATE TABLE admin_spaces (id TEXT, owner_id TEXT, status TEXT, deleted_at TEXT, expires_at TEXT)',
            'CREATE TABLE admin_space_members (space_id TEXT, user_id TEXT, role TEXT)',
            "INSERT INTO admin_users VALUES ('editor','正常',NULL)",
            "INSERT INTO admin_spaces VALUES ('space','owner','ACTIVE',NULL,NULL)",
            "INSERT INTO admin_space_members VALUES ('space','editor','编辑者')",
        ]:
            db.execute(text(statement))
        db.commit()
        project = scope.authorize(db, 'editor', 'space', 'repo', write=True)
        assert authorize_write(db, project, 'editor') == project
        if fault == 'revoked':
            db.execute(text('DELETE FROM admin_space_members'))
        elif fault == 'readonly':
            db.execute(text("UPDATE admin_space_members SET role='查看者'"))
        elif fault == 'disabled':
            db.execute(text("UPDATE admin_users SET status='禁用'"))
        elif fault == 'binding':
            binding['revision_marker'] = 'changed'
        else:
            project = scope.ProjectScope('other-space', 'repo', project.root,
                                         project.binding_revision, False)
        db.commit()
        with pytest.raises((ValueError, ChatError)):
            authorize_write(db, project, 'editor')
    engine.dispose()
