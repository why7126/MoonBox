"""Historical proof bridges EOF-LF only; altered content and anchors fail closed."""
import copy
import hashlib
import json
from pathlib import Path

import pytest
from app.governance import archive_recovery as recovery
from app.governance import spec_normalization as normalization


def put(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)


def inventory(path):
    return {p.relative_to(path).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in path.rglob('*') if p.is_file()}


def archive(root, cid):
    specs = root / 'openspec/specs'
    baseline = recovery.tree_hash(specs)
    text = f'### Requirement: {cid}\n系统 SHALL 核对。\n\n#### Scenario: 检查\n- **WHEN** 读取\n- **THEN** 核对\n\n'
    folder = root / f'openspec/archive/2026-10-26-{cid}'
    put(folder / f'specs/{cid}/spec.md', '## ADDED Requirements\n\n' + text)
    put(folder / 'trace.md', f'---\nstatus: archived\nchange_id: {cid}\n---\n')
    put(specs / f'{cid}/spec.md', '## Requirements\n\n' + text)
    record = dict(schema_version=4, input_projection=1, change_id=cid,
                  baseline_spec_hash=baseline, expected_spec_hash=recovery.tree_hash(specs),
                  delta_hash=recovery.tree_hash(folder/'specs'),
                  delivery_input_hash=recovery.delivery_input_hash(folder))
    put(recovery.journal_path(root, cid), json.dumps(record))
    return folder


@pytest.fixture
def scene(tmp_path):
    archive(tmp_path, 'source')
    specs = tmp_path/'openspec/specs'
    before = inventory(specs)
    p = specs/'source/spec.md'
    old = p.read_text(); new = old[:-1]; p.write_text(new)
    after = inventory(specs)
    archive(tmp_path, 'successor')
    data = dict(schema_version=1, source_change='source', successor_change='successor',
                before=before, after=after, texts={'source/spec.md': {'before': old, 'after': new}})
    proof = tmp_path/'openspec/archive/.spec-normalizations/proof.json'
    put(proof, json.dumps(data))
    return tmp_path, proof, data


def test_valid_complete_chain_is_read_only(scene):
    root, path, _ = scene
    before = recovery.tree_hash(root)
    result = recovery.recovery_admission(root, 'source')
    assert result['ready']
    assert len(result['chain']) == 2
    assert 'normalization' in result['chain'][0]
    assert recovery.tree_hash(root) == before


@pytest.mark.parametrize('mutation', ['body', 'missing-file', 'hash', 'anchor', 'delta',
                                     'delivery', 'duplicate', 'symlink', 'unsafe-path', 'unknown-schema'])
def test_bad_proof_blocks(scene, mutation):
    root, path, data = scene
    if mutation == 'body': data['texts']['source/spec.md']['after'] += 'changed\n'
    if mutation == 'missing-file': data['after'].pop('source/spec.md')
    if mutation == 'hash': data['before']['source/spec.md'] = '0'*64
    if mutation == 'anchor': data['source_change'] = 'missing'
    if mutation == 'delta': put(root/'openspec/archive/2026-10-26-successor/specs/successor/spec.md', 'tampered')
    if mutation == 'delivery': put(root/'openspec/archive/2026-10-26-successor/tasks.md', 'tampered')
    if mutation == 'duplicate': (root/'openspec/archive/2026-10-25-successor').mkdir()
    if mutation == 'unsafe-path': data['before']['../escape'] = '0'*64; data['after']['../escape'] = '0'*64
    if mutation == 'unknown-schema': data['schema_version'] = 99
    path.write_text(json.dumps(data))
    if mutation == 'symlink':
        saved = path.with_suffix('.saved'); path.rename(saved); path.symlink_to(saved)
    assert not recovery.recovery_admission(root, 'source')['ready']


def test_missing_proof_cannot_bridge(scene):
    root, path, _ = scene; path.unlink()
    assert not recovery.recovery_admission(root, 'source')['ready']


def test_concurrent_proof_change_rejected(scene, monkeypatch):
    root, path, data = scene
    original = recovery._recovery_state
    def race(*args):
        result = original(*args)
        data['schema_version'] = 2; path.write_text(json.dumps(data))
        return result
    monkeypatch.setattr(recovery, '_recovery_state', race)
    assert not recovery.recovery_admission(root, 'source')['ready']


def test_inventory_matches_path_component_order(tmp_path):
    for name in ['a/spec.md', 'a-b/spec.md', '.gitkeep']:
        put(tmp_path/name, name)
    assert normalization.inventory_hash(inventory(tmp_path)) == recovery.tree_hash(tmp_path)

@pytest.mark.parametrize('value', [[], None, {'schema_version': 1},
                                    {'schema_version': 1, 'unexpected': True}])
def test_malformed_document_fails_closed(scene, value):
    root, path, _ = scene
    path.write_text(json.dumps(value))
    assert not recovery.recovery_admission(root, 'source')['ready']
