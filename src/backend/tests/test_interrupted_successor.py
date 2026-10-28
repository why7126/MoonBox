"""An interrupted execution may have a startup baseline but no sync proof."""
import copy
import json
import pytest
from sqlalchemy import update, select
from test_chat import chat
from test_governance_writer import writing
from test_direct_completion import direct_scene, OID, CHANGE
from test_successor_completion import successor_scene


@pytest.fixture
def interrupted(successor_scene):
    from app.governance import store
    from app.chat.schema import turns
    factory, project, tid, rid, version = successor_scene
    record = store.read(rid, 'operation')
    record['steps'] = []
    record['terminal_status'] = 'stopped'
    store.write(rid, 'operation', record)
    with factory() as db:
        db.execute(update(turns).where(turns.c.id == tid).values(
            status='stopped', created_at='2026-10-20T00:00:00+00:00'))
        db.commit()
    return successor_scene


@pytest.mark.parametrize('failure', [None, 'baseline', 'identity', 'time', 'receipt', 'stale', 'running', 'version'])
def test_interrupted_successor_contract(interrupted, chat, failure):
    from app.governance import store
    from app.chat.schema import turns
    factory, project, tid, rid, version = interrupted
    client, _ = chat
    before = copy.deepcopy(store.read(rid, 'operation')['steps'])
    if failure in ('baseline', 'identity'):
        baseline = store.read(rid, 'baseline')
        if failure == 'baseline':
            baseline['files']['rules/security.md'] = 'tampered'
        else:
            baseline['object_id'] = 'BUG-9999-other'
        store.write(rid, 'baseline', baseline)
    if failure in ('running', 'time'):
        with factory() as db:
            values = dict(status='running') if failure == 'running' else dict(created_at='2099-01-01T00:00:00+00:00')
            db.execute(update(turns).where(turns.c.id == tid).values(**values)); db.commit()
    folder = project.root / 'openspec/changes' / CHANGE
    if failure == 'receipt':
        for f in (folder / '.workflow-receipts').glob('*.json'):
            f.unlink()
    if failure == 'stale':
        (folder / 'design.md').write_text('changed')
    url = f'/api/v1/chat/turns/{tid}/completion-verification'
    facts = client.get(url).json()['data']
    if failure in ('baseline', 'identity', 'running'):
        assert not facts['can_verify']
    elif failure != 'time':
        assert facts['can_verify']
    response = client.post(url, json={'expected_version': version + (failure == 'version')})
    assert response.status_code == (200 if failure is None else 409), response.text
    assert store.read(rid, 'operation')['steps'] == before
    with factory() as db:
        state = db.scalar(select(turns.c.status).where(turns.c.id == tid))
        assert state == ('running' if failure == 'running' else 'stopped')
    if failure is None:
        assert response.json()['data']['reason_code'] == 'direct_successor_verified'
        record = store.read(rid, 'operation')
        assert record['final_verification']['successor']['basis'] == 'startup_baseline'
        assert record['final_verification']['successor']['original_operation_id'] == tid
        assert client.post(url, json={'expected_version': version}).status_code == 200


def test_old_receipt_cannot_authorize_later_execution(interrupted, chat):
    _, project, tid, _, version = interrupted
    folder = project.root / 'openspec/changes' / CHANGE
    for f in (folder / '.workflow-receipts').glob('*.json'):
        value = json.loads(f.read_text()); value['created_at'] = '2026-10-19T00:00:00+00:00'
        f.write_text(json.dumps(value))
    response = chat[0].post(f'/api/v1/chat/turns/{tid}/completion-verification', json={'expected_version': version})
    assert response.status_code == 409


@pytest.mark.parametrize('mode', ['unrelated', 'source_race', 'guard_race', 'permission', 'interrupted'])
def test_independent_recovery_fences(interrupted, chat, monkeypatch, mode):
    from test_successor_completion import test_successor_recovery_fences
    test_successor_recovery_fences(interrupted, chat, monkeypatch, mode)


def test_independent_commit_resume(interrupted, chat, monkeypatch):
    from test_successor_completion import test_resume_journal_after_guard_commit
    test_resume_journal_after_guard_commit(interrupted, chat, monkeypatch)


def test_independent_binding_fence(interrupted, chat, monkeypatch):
    from test_successor_completion import test_binding_change_after_signature_keeps_guard
    test_binding_change_after_signature_keeps_guard(interrupted, chat, monkeypatch)


@pytest.mark.parametrize('created', [None, 123, [], 'not-a-date', '2099-01-01T00:00:00+00:00'])
def test_malformed_receipt_keeps_protection(interrupted, chat, created):
    _, project, tid, _, version = interrupted
    for path in (project.root / 'openspec/changes' / CHANGE / '.workflow-receipts').glob('*.json'):
        value = json.loads(path.read_text()); value['created_at'] = created
        path.write_text(json.dumps(value))
    assert chat[0].post(f'/api/v1/chat/turns/{tid}/completion-verification',
                        json={'expected_version': version}).status_code == 409


def test_authorization_differences_are_not_display_truncated():
    from app.governance.direct_completion import differences
    old = {'files': {}}
    new = {'files': {str(i): str(i) for i in range(40)}}
    assert len(differences(old, new)) == 30
    assert len(differences(old, new, limit=None)) == 40


def test_uncovered_change_after_thirty_covered_changes_is_rejected(interrupted, chat):
    from app.governance.acceptance_evidence import fingerprint
    from app.governance.workflow_receipt import emit
    _, project, tid, _, version = interrupted
    folder = project.root/'openspec/changes'/CHANGE
    plan = json.loads((folder/'acceptance-plan.json').read_text())
    for n in range(35):
        path = folder/f'covered-{n:02}.md'; path.write_text('accepted input')
        plan['checks'][0]['inputs'].append(str(path.relative_to(project.root)))
    (folder/'zzz-uncovered.md').write_text('not accepted')
    (folder/'acceptance-plan.json').write_text(json.dumps(plan))
    report = json.loads((folder/'evidence/acceptance/run/manifest.json').read_text())
    report['checks'][0]['fingerprint'] = fingerprint(project.root, plan['checks'][0])
    (folder/'evidence/acceptance/run/manifest.json').write_text(json.dumps(report))
    emit(project.root, CHANGE, 'opsx.accept', OID)
    response = chat[0].post(f'/api/v1/chat/turns/{tid}/completion-verification',json={'expected_version':version})
    assert response.status_code == 409
    assert response.json()['data']['kind'] == 'direct_successor_input_uncovered'


@pytest.mark.parametrize('action', ['opsx-apply', 'opsx-modify'])
def test_requirement_independent_successor(interrupted, chat, action):
    from app.governance import store, execution_guard as guards
    from app.governance.snapshot import digest
    from app.governance.acceptance_evidence import fingerprint
    from app.governance.workflow_receipt import emit
    factory, project, tid, rid, version = interrupted
    req = 'REQ-9001-sample'
    def translate(value):
        return value.replace(OID, req).replace('issues/bugs/', 'issues/requirements/').replace('bug_id:', 'requirement:').replace('/bug.md', '/requirement.md')
    current = {translate(str(p.relative_to(project.root))): translate(p.read_text())
               for p in project.root.rglob('*') if p.is_file() and '.workflow-receipts' not in p.parts}
    for p in project.root.rglob('*'):
        if p.is_file(): p.unlink()
    # The empty original requirements registry must not overwrite the translated one.
    current['issues/requirements/_registry.yaml'] = f'entries: [{{id: {req}, path: issues/requirements/review/{req}, status: in_sprint}}]'
    current['issues/bugs/_registry.yaml'] = 'entries: []'
    sprint = 'iterations/change/sprint-012/sprint.yaml'
    current[sprint] = current[sprint].replace('bugs:', 'sample_bugs:').replace('requirements: []', f'requirements: [{req}]')
    for name, content in current.items():
        path = project.root / name; path.parent.mkdir(exist_ok=True, parents=True); path.write_text(content)
    baseline = store.read(rid, 'baseline')
    baseline['files'] = {translate(k): translate(v) for k, v in baseline['files'].items()}
    baseline['files']['issues/requirements/_registry.yaml'] = current['issues/requirements/_registry.yaml']
    baseline['files']['issues/bugs/_registry.yaml'] = 'entries: []'
    baseline['files'][sprint] = current[sprint]
    baseline.update(object_id=req, action=action, revision=digest({k:v.encode() for k,v in baseline['files'].items()}))
    store.write(rid, 'baseline', baseline)
    record = store.read(rid, 'operation'); record.update(object_id=req, action=action, baseline_revision=baseline['revision'])
    store.write(rid, 'operation', record)
    with factory() as db:
        db.execute(update(guards.execution_guards).where(guards.execution_guards.c.operation_id == tid).values(
            object_id=req, action=action, baseline_revision=baseline['revision'])); db.commit()
    folder = project.root / 'openspec/changes' / CHANGE
    plan = json.loads((folder/'acceptance-plan.json').read_text())
    report = json.loads((folder/'evidence/acceptance/run/manifest.json').read_text())
    report['checks'][0]['fingerprint'] = fingerprint(project.root, plan['checks'][0])
    (folder/'evidence/acceptance/run/manifest.json').write_text(json.dumps(report))
    emit(project.root, CHANGE, 'opsx.accept', req)
    response = chat[0].post(f'/api/v1/chat/turns/{tid}/completion-verification', json={'expected_version':version})
    assert response.status_code == 200, response.text
    assert response.json()['data']['successor_evidence'] == {CHANGE:'run'}


@pytest.mark.parametrize('failure', [None, 'missing', 'operation', 'baseline', 'before', 'after', 'tasks', 'identity', 'coverage', 'sections', 'receipt', 'tamper', 'time', 'race'])
def test_receipt_bound_rule_transition(interrupted, chat, monkeypatch, failure):
    from app.governance import store
    from app.governance.direct_completion import manifest
    from app.governance.snapshot import stable
    from app.governance.acceptance_evidence import fingerprint
    from app.governance.workflow_receipt import emit
    from test_direct_completion import md
    _, project, tid, rid, version = interrupted
    folder = project.root/'openspec/changes'/CHANGE
    baseline = store.read(rid, 'baseline')
    old = manifest({k:v.encode() for k,v in baseline['files'].items()}, OID, 'opsx-apply')
    path = 'rules/security.md'
    (project.root/path).write_text('explicitly accepted rule transition')
    prefix = 'openspec/archive/2026-10-22-fix-rule-transition'
    source = project.root/prefix; source.mkdir(parents=True)
    for name in ['proposal','design']: (source/(name+'.md')).write_text('approved scope')
    (source/'tasks.md').write_text('- [ ] pending' if failure == 'tasks' else '- [x] done')
    (source/'trace.md').write_bytes(md(change_id='wrong' if failure == 'identity' else 'fix-rule-transition',status='applied',execution=dict(schema_version=1,started_at='2026-10-21 14:00:00',completed_at='2099-01-01' if failure == 'time' else '2026-10-22 14:00:00',last_event='opsx.apply')))
    current=manifest(stable(project.root).files, OID, 'opsx-apply')
    proof=dict(schema_version=1,path=path,source_change='fix-rule-transition',operation_id=tid,
               baseline_revision=baseline['revision'],before_sha256=old['files'][path],after_sha256=current['files'][path],check_ids=['AC-001'])
    field={'operation':'operation_id','baseline':'baseline_revision','before':'before_sha256','after':'after_sha256'}.get(failure)
    if field:proof[field]='wrong'
    plan=json.loads((folder/'acceptance-plan.json').read_text());check=plan['checks'][0]
    check['inputs'] += [path]+[prefix+'/'+name+'.md' for name in ['proposal','design','tasks','trace']]
    if failure == 'coverage':check['inputs'].remove(prefix+'/design.md')
    if failure == 'sections':check['input_sections']={path:['explicitly accepted rule transition']}
    if failure != 'missing':plan['successor_dependency_proofs']=[proof]
    (folder/'acceptance-plan.json').write_text(json.dumps(plan))
    report=folder/'evidence/acceptance/run/manifest.json';value=json.loads(report.read_text())
    value['checks'][0]['fingerprint']=fingerprint(project.root,check);report.write_text(json.dumps(value))
    emit(project.root,CHANGE,'opsx.accept',OID)
    if failure == 'receipt':
        for f in (folder/'.workflow-receipts').glob('*'):f.unlink()
    if failure == 'tamper':
        proof['source_change']='changed';(folder/'acceptance-plan.json').write_text(json.dumps(plan))
    if failure == 'race':
        original=store.write
        def write(record_id,name,value):
            original(record_id,name,value)
            if name=='operation' and value.get('final_verification'):(project.root/path).write_text('new rule race')
        monkeypatch.setattr(store,'write',write)
    before=copy.deepcopy(store.read(rid,'operation')['steps'])
    response=chat[0].post(f'/api/v1/chat/turns/{tid}/completion-verification',json={'expected_version':version})
    assert response.status_code==(200 if failure is None else 409),response.text
    assert store.read(rid,'operation')['steps']==before
    if failure is None:
        assert path in store.read(rid,'operation')['final_verification']['successor']['dependency_proofs']


@pytest.mark.parametrize('failure', [None, 'missing', 'operation', 'baseline', 'before', 'after', 'identity', 'extra', 'coverage', 'receipt'])
def test_receipt_bound_task_adjustment(interrupted, chat, failure):
    import hashlib,re
    from app.governance import store
    from app.governance.direct_completion import encoded
    from app.governance.acceptance_evidence import fingerprint
    from app.governance.workflow_receipt import emit
    _,project,tid,rid,version=interrupted
    prefix=f'openspec/changes/{CHANGE}/';folder=project.root/prefix
    baseline=store.read(rid,'baseline')
    before=re.findall(r'^\s*- \[[ xX]\]\s+(.+)$',baseline['files'][prefix+'tasks.md'],re.M)
    after=['task adjusted']
    if failure=='identity':after=['other task']
    if failure=='extra':after.append('extra task')
    (folder/'tasks.md').write_text('\n'.join('- [x] '+row for row in after))
    plan=json.loads((folder/'acceptance-plan.json').read_text());check=plan['checks'][0]
    check['inputs']+= [prefix+'tasks.md',prefix+'proposal.md']+[str(path.relative_to(project.root)) for path in (folder/'specs').glob('*/spec.md')]
    if failure=='coverage':check['inputs'].remove(prefix+'proposal.md')
    proof=dict(schema_version=1,change_id=CHANGE,operation_id=tid,baseline_revision=baseline['revision'],before_sha256=hashlib.sha256(encoded(before)).hexdigest(),after_sha256=hashlib.sha256(encoded(after)).hexdigest(),check_ids=['AC-001'])
    field={'operation':'operation_id','baseline':'baseline_revision','before':'before_sha256','after':'after_sha256'}.get(failure)
    if field:proof[field]='wrong'
    if failure!='missing':plan['successor_task_proofs']=[proof]
    (folder/'acceptance-plan.json').write_text(json.dumps(plan))
    report=folder/'evidence/acceptance/run/manifest.json';value=json.loads(report.read_text());value['checks'][0]['fingerprint']=fingerprint(project.root,check);report.write_text(json.dumps(value));emit(project.root,CHANGE,'opsx.accept',OID)
    if failure=='receipt':
        for f in (folder/'.workflow-receipts').glob('*'):f.unlink()
    original=copy.deepcopy(store.read(rid,'operation')['steps'])
    response=chat[0].post(f'/api/v1/chat/turns/{tid}/completion-verification',json={'expected_version':version})
    assert response.status_code==(200 if failure is None else 409),response.text
    assert store.read(rid,'operation')['steps']==original
