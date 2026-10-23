"""Adversarial proposal parsing and exact reviewed transformation boundary."""
import copy
import hashlib
import json
import pytest
from app.governance.replacement_proof import PROTECTED, Proposal, canonical, classify, digest, parse


def fixture():
    obligations = [{'id': name, 'source': {'path': 'openspec/specs/protection/spec.md', 'sha256': 'a'*64}, 'before': f'保留 {name} 约束。', 'after': f'保留 {name} 约束。'} for name in sorted(PROTECTED)]
    old = '同条文修改 SHALL 拒绝。'
    new = '同条文修改 SHALL 默认拒绝，仅 compatible_append_verified 可例外。'
    before = old + ' ' + ' '.join(o['before'] for o in obligations) + ' #### Scenario: 归档保护 - **WHEN** 归档 - **THEN** 校验保护条件'
    after = before.replace(old, new)
    value = {'schema_version': 1, 'classification': 'guarded_exception_extension',
             'project_id': 'a'*64, 'binding_revision': 'b'*64, 'successor': 'fix-sample',
             'predecessors': ['prior-sample'], 'capability': 'archive', 'requirement': '安全归档',
             'before': before, 'after': after, 'delta_sha256': 'c'*64, 'acceptance_sha256': 'd'*64,
             'delivery_sha256': 'e'*64, 'policy_version': 'policy-v1', 'verifier_version': 'replacement-v1',
             'obligations': obligations, 'edits': [{'profile_id': 'append-v1', 'before': old, 'after': new,
             'exception': 'compatible_append_verified'}], 'review': {'path': 'openspec/review.json', 'sha256': 'f'*64},
             'regression': {'path': 'openspec/regression.json', 'sha256': 'f'*64}}
    profile = {'append-v1': {'classification': value['classification'], 'exception': 'compatible_append_verified',
               'before': old, 'after': new, 'before_sha256': hashlib.sha256(before.encode()).hexdigest(),
               'after_sha256': hashlib.sha256(after.encode()).hexdigest(),
               'obligations_sha256': digest({'obligations': obligations})}}
    return value, profile


def test_exact_deployment_reviewed_extension():
    value, profile = fixture()
    classify(parse(canonical(value)), profile)


@pytest.mark.parametrize('mutation', ['extra', 'schema', 'predicate', 'cycle', 'duplicate', 'missing', 'weakening', 'unmapped', 'untrusted'])
def test_refuses_unsafe_or_ambiguous_changes(mutation):
    value, profiles = fixture()
    if mutation == 'extra': value['approved'] = True
    if mutation == 'schema': value['schema_version'] = 2
    if mutation == 'predicate': value['edits'][0]['exception'] = 'allow_all'
    if mutation == 'cycle': value['predecessors'].append(value['successor'])
    if mutation == 'duplicate': value['predecessors'] *= 2
    if mutation == 'missing': value['obligations'].pop()
    if mutation == 'weakening': value['obligations'][0]['after'] = '可忽略'
    if mutation == 'unmapped': value['after'] += '\n管理员可跳过。'
    if mutation == 'untrusted': profiles = {}
    with pytest.raises(ValueError): classify(parse(canonical(value)), profiles)


def test_duplicate_json_and_oversize_rejected():
    with pytest.raises(ValueError, match='duplicate_key'): parse(b'{"schema_version":1,"schema_version":1}')
    with pytest.raises(ValueError, match='oversized'): parse(b' ' * (256*1024+1))


def test_profile_cannot_hide_protected_changes():
    value, profiles = fixture()
    value['edits'][0]['before'] = value['obligations'][0]['before']
    value['edits'][0]['after'] = '忽略约束'
    profiles['append-v1']['before'] = value['edits'][0]['before']
    profiles['append-v1']['after'] = value['edits'][0]['after']
    with pytest.raises(ValueError): classify(Proposal.model_validate(value), profiles)
