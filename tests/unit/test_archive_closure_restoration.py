"""Synthetic binding/negative cases; real original recovery proof checked by CLI."""
import json
import pytest
from app.governance import archive_closure_restoration as m
from app.governance.archive_finalization import inspect_document, build_report


def put(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    return p


@pytest.fixture
def sample(tmp_path, monkeypatch):
    folder = tmp_path / 'openspec/archive/2026-10-31-fix-sample'
    issue = tmp_path / 'issues/requirements/archive/REQ-9001-sample'
    put(folder / 'trace.md', '---\nstatus: archived\nrequirement_id: REQ-9001-sample\n---\n')
    put(folder / 'proposal.md', '---\nstatus: proposed\n---\n# 原始提案\n')
    put(folder / 'verification.md', '# 验证\n通过\n')
    put(issue / 'trace.md', '---\nstatus: done\nlifecycle_stage: archive\nrelated_change: fix-sample\n---\n')
    put(issue / 'requirement.md', '---\nstatus: done\n---\n[验证](openspec/changes/fix-sample/verification.md)\n')
    put(issue / 'acceptance.md', '---\nacceptance_status: passed\n---\n')
    journal = put(m.journal_path(tmp_path, 'fix-sample'), '{"retained":true}\n')
    monkeypatch.setattr(m, 'archived_readiness', lambda *_: {'status': 'ready', 'run_id': 'one'})
    monkeypatch.setattr(m, 'latest_manifest', lambda *_: {'run_id': 'one', 'status': 'passed', 'scope': 'complete'})
    return tmp_path, folder, issue, journal


def test_explicit_readonly_restore_and_idempotent_shared_gate(sample):
    root, folder, issue, journal = sample
    before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
    assert build_report(root, 'fix-sample')['status'] == 'blocked'
    assert m.restore(root, 'fix-sample')['status'] == 'ready'
    assert before == {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
    assert m.restore(root, 'fix-sample', apply=True)['status'] == 'restored'
    receipt = m.receipt_path(root, 'fix-sample').read_bytes()
    assert build_report(root, 'fix-sample')['status'] == 'finalized'
    assert not inspect_document(root, issue / 'requirement.md', completed=True)
    assert m.restore(root, 'fix-sample', apply=True)['status'] == 'unchanged'
    assert m.receipt_path(root, 'fix-sample').read_bytes() == receipt
    assert all(p.read_bytes() == b for p, b in before.items())


@pytest.mark.parametrize('target', ['proposal', 'source', 'destination', 'journal', 'manifest', 'evidence', 'receipt'])
def test_changed_input_or_receipt_keeps_gate_closed(sample, monkeypatch, target):
    root, folder, issue, journal = sample
    m.restore(root, 'fix-sample', apply=True)
    paths = {'proposal': folder/'proposal.md', 'source': issue/'requirement.md', 'destination': folder/'verification.md', 'journal': journal}
    if target in paths:
        p=paths[target];p.write_text(p.read_text()+'\nchanged\n')
    elif target == 'manifest': monkeypatch.setattr(m, 'latest_manifest', lambda *_: {'run_id':'two'})
    elif target == 'evidence': monkeypatch.setattr(m, 'archived_readiness', lambda *_: {'status':'blocked'})
    else:
        p=m.receipt_path(root,'fix-sample');record=json.loads(p.read_text());record['proof']['projections'][0]['to']='done';p.write_text(json.dumps(record))
    with pytest.raises(ValueError): m.restore(root,'fix-sample',apply=True)
    assert build_report(root,'fix-sample')['status']=='blocked'


@pytest.mark.parametrize('case', ['active', 'duplicate', 'source-review', 'wrong-owner', 'partial', 'unfinished-sibling', 'missing-target', 'escape', 'symlink', 'failed-evidence', 'partial-manifest'])
def test_ineligible_or_unsafe_cases_cannot_publish(sample, monkeypatch, case):
    root,folder,issue,journal=sample
    if case=='active': (root/'openspec/changes/fix-sample').mkdir(parents=True)
    elif case=='duplicate': (root/'openspec/archive/2026-10-30-fix-sample').mkdir()
    elif case=='source-review':
        dst=root/'issues/requirements/review'/issue.name;dst.parent.mkdir();issue.rename(dst)
    elif case=='wrong-owner': (issue/'trace.md').write_text('---\nstatus: done\nlifecycle_stage: archive\nrelated_change: another\n---\n')
    elif case=='partial': (issue/'acceptance.md').write_text('---\nacceptance_status: partial\n---\n')
    elif case=='unfinished-sibling':
        (issue/'trace.md').write_text('---\nstatus: done\nlifecycle_stage: archive\nrelated_changes: [fix-sample, unfinished]\n---\n')
    elif case=='missing-target': (folder/'verification.md').unlink()
    elif case=='escape': (issue/'requirement.md').write_text('---\nstatus: done\n---\n[bad](openspec/changes/fix-sample/../secret.md)')
    elif case=='symlink':
        (folder/'verification.md').unlink();(folder/'verification.md').symlink_to(journal)
    elif case=='failed-evidence': monkeypatch.setattr(m,'archived_readiness',lambda *_:{'status':'blocked'})
    elif case=='partial-manifest': monkeypatch.setattr(m,'latest_manifest',lambda *_:{'status':'passed','run_id':'one','scope':'diagnostic'})
    with pytest.raises((ValueError, OSError)): m.restore(root,'fix-sample',apply=True)
    assert not m.receipt_path(root,'fix-sample').exists()


@pytest.mark.parametrize('state', ['failed','blocked','in_progress','applied'])
def test_noninitial_proposal_not_projected(sample,state):
    root,folder,issue,_=sample
    (folder/'proposal.md').write_text(f'---\nstatus: {state}\n---\n')
    m.restore(root,'fix-sample',apply=True)  # Only the unrelated valid link gets a projection.
    assert not any(row.get('field') for row in m.verified(root,'fix-sample')['projections'])
    assert m.document_projection(root,folder/'proposal.md') == []


def test_unrelated_source_and_current_prose_not_exempt(sample):
    root,folder,issue,_=sample
    (folder/'proposal.md').write_text('---\nstatus: proposed\n---\n当前交付状态：failed。\n')
    m.restore(root,'fix-sample',apply=True)
    assert 'current-state-conflict' in {x['kind'] for x in inspect_document(root,folder/'proposal.md',completed=True)}
    other=put(root/'issues/requirements/archive/REQ-9002-other/requirement.md','[bad](openspec/changes/fix-sample/verification.md)')
    put(other.parent/'trace.md','---\nrelated_change: fix-sample\n---\n')
    assert inspect_document(root,other)


def test_exclusive_publication_rejects_concurrent_writer(sample,monkeypatch):
    root,_,_,_=sample
    real_link=m.os.link
    def collision(source,destination):
        destination.write_text('{"foreign":true}')
        real_link(source,destination)
    monkeypatch.setattr(m.os,'link',collision)
    with pytest.raises(FileExistsError):m.restore(root,'fix-sample',apply=True)
    assert m.receipt_path(root,'fix-sample').read_text()=='{"foreign":true}'


def test_real_acceptance_and_recovery_proof_without_mocks(tmp_path):
    import sys
    from scripts.opsx_acceptance import run_acceptance
    from app.governance.archive_recovery import tree_hash, delivery_input_hash
    root=tmp_path;change='fix-real';folder=root/'openspec/changes'/change
    put(root/'input.txt','stable')
    put(folder/'trace.md','---\nstatus: archived\n---\n')
    put(folder/'proposal.md','---\nstatus: proposed\n---\n# Original\n')
    body='### Requirement: Sample\nSystem SHALL preserve evidence.\n\n#### Scenario: Closed\n- **WHEN** checked\n- **THEN** preserved\n'
    put(folder/'specs/sample/spec.md','## ADDED Requirements\n\n'+body)
    put(root/'openspec/specs/sample/spec.md',body)
    plan={'schema_version':1,'change_id':change,'checks':[{'id':'AC-1','kind':'command','inputs':['input.txt'],'argv':[sys.executable,'-c','pass']}]}
    put(folder/'acceptance-plan.json',json.dumps(plan))
    result=run_acceptance(root,change,None)
    assert result['status']=='passed'
    destination=root/'openspec/archive/2026-10-31-fix-real';destination.parent.mkdir(parents=True)
    folder.rename(destination)
    record={'schema_version':4,'change_id':change,'archive_date':'2026-10-31','input_projection':1,
            'delivery_input_hash':delivery_input_hash(destination),'delta_hash':tree_hash(destination/'specs'),
            'baseline_spec_hash':tree_hash(root/'openspec/specs'),'expected_spec_hash':tree_hash(root/'openspec/specs')}
    put(m.journal_path(root,change),json.dumps(record))
    assert m.restore(root,change,apply=True)['status']=='restored'
    assert build_report(root,change)['status']=='finalized'
    (destination/'proposal.md').write_text('tampered')
    assert build_report(root,change)['status']=='blocked'


def test_symlink_receipt_and_publish_input_race_rejected(sample,monkeypatch):
    root,folder,issue,journal=sample
    path=m.receipt_path(root,'fix-sample');path.parent.mkdir(parents=True)
    path.symlink_to(journal)
    with pytest.raises(ValueError):m.restore(root,'fix-sample',apply=True)
    path.unlink()
    real=m.proof;count=0
    def race(*args):
        nonlocal count
        count+=1
        if count==2:(folder/'verification.md').write_text('changed during publish')
        return real(*args)
    monkeypatch.setattr(m,'proof',race)
    with pytest.raises(ValueError):m.restore(root,'fix-sample',apply=True)
    assert not path.exists()


def test_unchanged_acceptance_replay_preserves_bytes_and_signoff(monkeypatch):
    from workflow_sync import issue_subdocuments as s
    args = dict(status='passed', source_change='fix-sample', source_sprint='sprint-018', event='opsx.archive', evidence='evidence/summary.md')
    monkeypatch.setattr(s, 'now_shanghai', lambda: '2026-10-31 19:42:19')
    original = '# 验收\n\n' + s.render_acceptance_block(**args) + '\n'
    monkeypatch.setattr(s, 'now_shanghai', lambda: '2026-10-31 20:01:34')
    assert s.upsert_acceptance_block(original, **args) == (original, False)
    changed, updated = s.upsert_acceptance_block(original, **{**args, 'status': 'failed'})
    assert updated and 'acceptance_status: failed' in changed
    assert 'accepted_at: 2026-10-31 20:01:34' in changed


def test_historical_closure_sentence_requires_receipt_and_preserves_bytes(sample):
    root, folder, _, _ = sample
    trace = folder / 'trace.md'
    trace.write_text(trace.read_text() + '\n## 验收结论\n8项AC通过。无正式归档授权，本次未归档。\n')
    original = trace.read_bytes()
    assert any(h['kind'] == 'current-state-conflict' for h in inspect_document(root, trace, completed=True))
    m.restore(root, 'fix-sample', apply=True)
    assert build_report(root, 'fix-sample')['status'] == 'finalized'
    assert trace.read_bytes() == original
    assert m.restore(root, 'fix-sample', apply=True)['status'] == 'unchanged'
    trace.write_text(trace.read_text() + '\nchanged\n')
    assert build_report(root, 'fix-sample')['status'] == 'blocked'


@pytest.mark.parametrize('text', [
    '无正式归档授权，本次未归档。当前交付状态：failed。',
    '无正式归档授权，本次未归档；当前状态：待验收。',
    '无正式归档授权，本次未归档，当前交付状态：failed。',
    '当前验收状态：未归档。',
])
def test_historical_projection_does_not_hide_neighbouring_or_unknown_claims(sample, text):
    root, folder, _, _ = sample
    trace = folder / 'trace.md'
    trace.write_text(trace.read_text() + '\n## 验收结论\n' + text + '\n')
    m.restore(root, 'fix-sample', apply=True)
    assert any(h['kind'] == 'current-state-conflict' for h in inspect_document(root, trace, completed=True))


@pytest.mark.parametrize('filename,heading', [('trace.md', '当前摘要'), ('proposal.md', '验收结论')])
def test_historical_projection_restricted_to_trace_acceptance_section(sample, filename, heading):
    root, folder, _, _ = sample
    path = folder / filename
    path.write_text(path.read_text() + f'\n## {heading}\n无正式归档授权，本次未归档。\n')
    m.restore(root, 'fix-sample', apply=True)
    assert any(h['kind'] in {'current-state-conflict', 'current-state-review'} for h in inspect_document(root, path, completed=True))
    assert not any('historical_sentence' in row for row in m.document_projection(root, path))


QUOTED_DIAGNOSIS = 'BUG-0073归档同步后，验收结论保留“无正式归档授权，本次未归档”，共享收尾校验误当当前状态'


def test_proposal_quote_requires_proof_and_preserves_original(sample):
    root, folder, _, _ = sample
    path = folder / 'proposal.md'
    path.write_text(path.read_text() + '\n## 背景\n' + QUOTED_DIAGNOSIS + '。\n')
    original = path.read_bytes()
    assert build_report(root, 'fix-sample')['status'] != 'finalized'
    assert m.restore(root, 'fix-sample')['status'] == 'ready'
    assert not m.receipt_path(root, 'fix-sample').exists()
    m.restore(root, 'fix-sample', apply=True)
    assert build_report(root, 'fix-sample')['status'] == 'finalized'
    assert path.read_bytes() == original
    assert m.restore(root, 'fix-sample', apply=True)['status'] == 'unchanged'
    path.write_text(path.read_text().replace('BUG-0073', 'BUG-0074'))
    assert build_report(root, 'fix-sample')['status'] == 'blocked'


@pytest.mark.parametrize('filename,heading,suffix', [
    ('proposal.md', '背景', '。当前交付状态：failed'),
    ('proposal.md', '背景', '；当前验收状态：待验收'),
    ('proposal.md', '背景', '，当前交付状态：failed'),
    ('proposal.md', '验收结论', ''),
    ('trace.md', '背景', ''),
])
def test_quoted_history_keeps_other_claims_and_wrong_locations_open(sample, filename, heading, suffix):
    root, folder, _, _ = sample
    path = folder / filename
    path.write_text(path.read_text() + f'\n## {heading}\n' + QUOTED_DIAGNOSIS + suffix + '。\n')
    m.restore(root, 'fix-sample', apply=True)
    assert build_report(root, 'fix-sample')['status'] != 'finalized'


def test_quote_restore_still_requires_complete_evidence(sample, monkeypatch):
    root, folder, _, _ = sample
    path = folder / 'proposal.md'
    path.write_text(path.read_text() + '\n## 背景\n' + QUOTED_DIAGNOSIS + '。\n')
    monkeypatch.setattr(m, 'archived_readiness', lambda *_: {'status': 'blocked'})
    with pytest.raises(ValueError):
        m.restore(root, 'fix-sample', apply=True)
    assert not m.receipt_path(root, 'fix-sample').exists()


def test_trace_supplement_preserves_original_and_rejects_tampering(sample):
    from app.governance import archive_trace_supplement as supplement
    root, folder, issue, _ = sample
    trace = issue / 'trace.md'
    trace.write_text(trace.read_text().replace('status: done', 'updated_at: 2026-10-31 19:42:17\nstatus: done'))
    original = trace.read_text()
    m.restore(root, 'fix-sample', apply=True)
    receipt = m.receipt_path(root, 'fix-sample').read_bytes()
    bug = root / 'issues/bugs/archive/BUG-9001-sample/trace.md'
    put(bug, '---\nstatus: done\nrelated_requirement: REQ-9001-sample\nrelated_change: fix-sample\n---\n')
    index = '\n## 关联缺陷\n\n| BUG | 严重等级 | 状态 | 关联 Change | 说明 |\n|---|---|---|---|---|\n| BUG-9001-sample | medium | done | fix-sample | 样本 |\n'
    current = original.replace('19:42:17', '20:42:17') + index
    trace.write_text(current)
    with pytest.raises((ValueError, OSError)): m.verified(root, 'fix-sample')
    assert supplement.create(root, 'fix-sample', original)['status'] == 'ready'
    assert supplement.create(root, 'fix-sample', original, True)['status'] == 'created'
    assert m.verified(root, 'fix-sample')
    assert receipt == m.receipt_path(root, 'fix-sample').read_bytes()
    assert current == trace.read_text()
    assert supplement.create(root, 'fix-sample', original, True)['status'] == 'unchanged'
    bug.write_text(bug.read_text().replace('REQ-9001', 'REQ-9002'))
    with pytest.raises(ValueError): m.verified(root, 'fix-sample')
    bug.write_text(bug.read_text().replace('REQ-9002', 'REQ-9001'))
    trace.write_text(current + 'unknown change\n')
    with pytest.raises(ValueError): m.verified(root, 'fix-sample')
    trace.write_text(current)
    path = supplement.location(root, 'fix-sample')
    record = json.loads(path.read_text()); record['original_text'] += 'tampered'
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError): m.verified(root, 'fix-sample')
