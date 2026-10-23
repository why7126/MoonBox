"""Completion evidence rejects partial output and inconsistent object references."""
import pytest
import yaml
from app.governance.execution_validation import validate_result, validate_external


def doc(**metadata):
    return ('---\n' + yaml.safe_dump(metadata) + '---\n# 验证样本\n').encode()


@pytest.mark.parametrize('prefix,folder,primary', [('REQ','requirements','requirement.md'),('BUG','bugs','bug.md')])
@pytest.mark.parametrize('suffix,status', [('generate','draft'),('complete','pending_review'),('review','approved'),('opsx','in_sprint')])
def test_completion_requires_consistent_documents(prefix, folder, primary, suffix, status):
    oid=f'{prefix}-9001-completion';base=f'issues/{folder}/review/{oid}';cid='completion-test'
    files={f'issues/{folder}/_registry.yaml':yaml.safe_dump({'entries':[dict(id=oid,path=base,status=status)]}).encode(),
           f'{base}/trace.md':doc(status=status,iteration='sprint-999',openspec_changes=[dict(change_id=cid)]),
           f'{base}/{primary}':doc(title='完成验证样本',status=status),
           'iterations/change/sprint-999/sprint.yaml':yaml.safe_dump({folder if prefix=='REQ' else 'bugs':[oid],'changes':[cid]}).encode()}
    for name in ['business-flow.md','user-stories.md','root-cause.md','workaround.md','acceptance.md','review.md']:
        files[f'{base}/{name}']=doc(title='验证材料')
    for name in ['proposal.md','design.md','tasks.md']:
        files[f'openspec/changes/{cid}/{name}']=b'# Test\n'
    files[f'openspec/changes/{cid}/trace.md']=doc(status='proposed')
    action=f'{prefix.lower()}-{suffix}'
    assert validate_result(files,oid,action)
    files[f'{base}/{primary}']=doc(title='完成验证样本',status='captured')
    assert not validate_result(files,oid,action)


def test_apply_does_not_trust_checked_tasks_without_completion_fact():
    cid='completion-test';base=f'openspec/changes/{cid}'
    files={f'{base}/{name}':b'# Test\n' for name in ['proposal.md','design.md']}
    files[f'{base}/tasks.md']=b'- [x] implementation\n'
    files[f'{base}/trace.md']=doc(status='in_progress',execution={'completed_at':None})
    assert not validate_result(files,cid,'opsx-apply')
    files[f'{base}/trace.md']=doc(status='applied',execution={'completed_at':'2026-10-19 12:00:00'})
    assert validate_result(files,cid,'opsx-apply')
    files[f'{base}/tasks.md']+=b'- [ ] validation\n'
    assert not validate_result(files,cid,'opsx-apply')
    assert not validate_external(files,cid,'acceptance')


@pytest.mark.parametrize('key',['requirement','requirement_id','req_id','source_requirement'])
def test_change_source_aliases_remain_compatible_and_conflicts_fail_closed(key):
    from app.governance.preparation import _matches_change_source
    oid='REQ-9001-completion'
    assert _matches_change_source({key:oid},oid)
    other_key = 'requirement_id' if key == 'source_requirement' else 'source_requirement'
    assert not _matches_change_source({key:oid,other_key:'REQ-9002-other'},oid)
    assert not _matches_change_source({key:[oid]},oid)


@pytest.mark.parametrize('status',['applied','archived'])
def test_archive_accepts_preserved_apply_trace_only_in_archive_location(status):
    cid='archive-test';base=f'openspec/archive/2026-10-19-{cid}'
    files={f'{base}/{name}':b'# Test\n' for name in ['proposal.md','design.md','tasks.md']}
    files[f'{base}/trace.md']=doc(status=status)
    assert validate_result(files,cid,'opsx-archive')
    active={path.replace(base,f'openspec/changes/{cid}'):body for path,body in files.items()}
    assert not validate_result(active,cid,'opsx-archive')


def test_external_enriching_preserves_planning_without_claiming_completion():
    oid='BUG-9001-completion';base=f'issues/bugs/plan/{oid}'
    files={'issues/bugs/_registry.yaml':yaml.safe_dump({'entries':[dict(id=oid,path=base,status='enriching')]}).encode(),
        f'{base}/trace.md':doc(status='enriching'), f'{base}/bug.md':doc(title='处理中',status='enriching')}
    assert validate_external(files,oid,'planning')
    assert not validate_result(files,oid,'bug-generate')
    assert not validate_result(files,oid,'bug-complete')


def test_legacy_archive_uses_existing_folder_fact_without_inventing_execution():
    cid='legacy-test';base=f'openspec/archive/2026-07-29-{cid}'
    files={f'{base}/{name}':b'# Historical evidence\n' for name in ['proposal.md','tasks.md','trace.md']}
    assert validate_external(files,cid,'done')
    assert not validate_result(files,cid,'opsx-archive')  # new commands require current artifacts
    assert not validate_external({**files,f'openspec/changes/{cid}/trace.md':doc(status='proposed')},cid,'done')
