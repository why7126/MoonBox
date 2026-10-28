"""Archive proof rejects incomplete merges and unrelated execution identities."""
from types import SimpleNamespace
from unittest.mock import patch
import pytest
from app.governance.archive_proof import validate_merge, verify, ArchiveProofError

CID = 'fix-example'
PREFIX = f'openspec/changes/{CID}/'
ARCHIVE = f'openspec/archive/2026-10-19-{CID}'
OLD = '### Requirement: 原能力\n系统 SHALL 保留。\n\n#### Scenario: 原场景\n- **WHEN** 读取\n- **THEN** 保留\n'
NEW = '### Requirement: 新能力\n系统 SHALL 核验。\n\n#### Scenario: 新场景\n- **WHEN** 归档\n- **THEN** 核验\n'


def fixture():
    before = {PREFIX+'trace.md': b'original', 'openspec/specs/test/spec.md': OLD.encode(),
              PREFIX+'specs/test/spec.md': ('## ADDED Requirements\n\n'+NEW).encode()}
    for name in ('proposal.md', 'design.md', 'tasks.md'):
        before[PREFIX+name] = b'approved artifact'
    current = {n.replace(PREFIX, ARCHIVE+'/'): b for n,b in before.items()}
    current['openspec/specs/test/spec.md'] = (OLD+'\n'+NEW).encode()
    return before, current


def test_wrapped_archive_merge_proof_allows_unrelated_new_issue():
    before,current=fixture()
    current['issues/bugs/plan/BUG-9999/capture.md']=b'unrelated'
    validate_merge(before,current,CID,ARCHIVE)


@pytest.mark.parametrize('mutation', ['missing', 'edited', 'extra', 'delta', 'tasks'])
def test_archive_merge_rejects_missing_or_conflicting_results(mutation):
    before,current=fixture()
    if mutation=='missing': current['openspec/specs/test/spec.md']=OLD.encode()
    if mutation=='edited': current['openspec/specs/test/spec.md']=(OLD.replace('保留','改变')+NEW).encode()
    if mutation=='extra': current['openspec/specs/test/spec.md']+=(NEW.replace('新能力','额外能力')).encode()
    if mutation=='delta': current[ARCHIVE+'/specs/test/spec.md']=b'changed'
    if mutation=='tasks': current[ARCHIVE+'/tasks.md']=b'changed'
    with pytest.raises(ArchiveProofError): validate_merge(before,current,CID,ARCHIVE)


@pytest.mark.parametrize('operation', ['MODIFIED','REMOVED'])
def test_modified_and_removed_requirements(operation):
    before,current=fixture()
    replacement=OLD.replace('保留','核验')
    before[PREFIX+'specs/test/spec.md']=(f'## {operation} Requirements\n\n'+replacement).encode()
    current[ARCHIVE+'/specs/test/spec.md']=before[PREFIX+'specs/test/spec.md']
    current['openspec/specs/test/spec.md']=replacement.encode() if operation=='MODIFIED' else b''
    validate_merge(before,current,CID,ARCHIVE)


def test_unknown_and_failed_terminal_do_not_run_checker():
    for terminal in ('unknown','failed','stopped','running'):
        with patch('app.governance.archive_proof.subprocess.run') as run:
            with pytest.raises(ArchiveProofError,match='terminal'):
                verify(None,{'action':'opsx-archive'},{'status':terminal},{},None)
            run.assert_not_called()


def test_wrong_execution_is_rejected_before_record_access():
    with pytest.raises(ArchiveProofError,match='execution'):
        verify(None,{'action':'opsx-archive','operation_id':'old','conversation_id':'c'},
               {'status':'completed','id':'new','conversation_id':'c'}, {},None)

@pytest.fixture
def verifier(tmp_path, monkeypatch):
    from contextlib import nullcontext
    from app.governance.snapshot import Snapshot, digest
    from app.governance import archive_proof as module
    before,current=fixture()
    source=tmp_path/'source';(source/'scripts').mkdir(parents=True)
    (source/'scripts'/'sync-workflow-status.py').write_text('# trusted checker')
    project=SimpleNamespace(root=source,source_root=source,key='scope',binding_revision='binding')
    guard=dict(action='opsx-archive',operation_id='turn',conversation_id='c',object_id=CID,
               baseline_revision=digest(before),scope_key='scope')
    turn=dict(id='turn',status='completed',conversation_id='c',client_request_id='request')
    operation=dict(phase='terminal',terminal_status='completed',steps=[{'sync_succeeded':False}])
    baseline=dict(binding_revision='binding',files={n:b.decode() for n,b in before.items()})
    def checked_records(*args, **kwargs):
        kwargs['records']['baseline'] = baseline
        return None
    monkeypatch.setattr(module,'record_block_reason',checked_records)
    monkeypatch.setattr(module.store,'read',lambda *a:baseline)
    monkeypatch.setattr(module,'_archive',lambda *a:(CID,ARCHIVE))
    monkeypatch.setattr(module,'validate_result',lambda *a:True)
    monkeypatch.setattr(module,'project_lock',lambda *a:nullcontext())
    monkeypatch.setattr(module,'read_once',lambda *a:current)
    writes=[];monkeypatch.setattr(module.store,'write',lambda *a:writes.append(a))
    commands=[]
    def run(args,**kwargs):
        commands.append(args)
        assert kwargs['env']['PYTHONPATH'].endswith(('src/backend', '/app'))
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(module.subprocess,'run',run)
    return module,project,guard,turn,operation,Snapshot(current,digest(current)),writes,commands


def test_success_records_new_proof_without_forging_original_steps(verifier):
    m,p,g,t,o,s,w,cmd=verifier
    proof=verify(p,g,t,o,s)
    assert proof['operation_id']=='turn' and proof['source_hash']==s.revision
    assert w[0][2]['steps']==[{'sync_succeeded':False}]
    assert cmd[0][1:3]==['-m','app.governance.archive_workflow_check']
    assert cmd[0][-1]==CID
    assert 'archive-change.sh' not in ' '.join(cmd[0])
    assert verify(p,g,t,o,s)==proof


def test_missing_baseline_rejects_before_digest_without_reopening_records(verifier, monkeypatch):
    m,p,g,t,o,s,w,cmd=verifier
    def checked_records(*args, **kwargs):
        kwargs['records']['baseline'] = {'binding_revision': 'binding', 'files': {}}
    monkeypatch.setattr(m, 'record_block_reason', checked_records)
    def unexpected(*args, **kwargs):
        pytest.fail('missing baseline must reject before duplicate read or digest')
    monkeypatch.setattr(m.store, 'read', unexpected)
    monkeypatch.setattr(m, 'digest', unexpected)
    with pytest.raises(ArchiveProofError, match='archive_baseline_missing'):
        verify(p,g,t,o,s)
    assert not w and not cmd


def test_record_handoff_is_fresh_and_only_populated_after_validation(tmp_path, monkeypatch):
    from app.governance import direct_command_journal as journal
    rid = journal.record_id('conversation', 'request')
    (tmp_path / rid).mkdir()
    monkeypatch.setattr(journal.store, 'root', lambda: tmp_path)
    operation = dict(schema_version=1, action='opsx-archive', object_id=CID,
                     baseline_revision='revision', steps=[], phase='terminal')
    baseline = dict(action='opsx-archive', object_id=CID, revision='revision', files={})
    reads = []
    def read(record, name):
        reads.append(name)
        return dict(operation if name == 'operation' else baseline)
    monkeypatch.setattr(journal.store, 'read', read)
    records = {}
    assert journal.record_block_reason('conversation', 'request', action='opsx-archive', records=records) is None
    assert reads == ['operation', 'baseline'] and records['baseline'] == baseline
    baseline['revision'] = 'changed'
    rejected = {}
    assert journal.record_block_reason('conversation', 'request', action='opsx-archive', records=rejected) == 'direct_command_identity_mismatch'
    assert reads == ['operation', 'baseline'] * 2 and not rejected


@pytest.mark.parametrize('failure', ['sync','changed','business','binding','baseline','scope'])
def test_untrusted_or_incomplete_result_never_writes_proof(verifier,monkeypatch,failure):
    m,p,g,t,o,s,w,cmd=verifier
    if failure=='sync': monkeypatch.setattr(m.subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=1))
    if failure=='changed': monkeypatch.setattr(m,'read_once',lambda *a:{})
    if failure=='business': monkeypatch.setattr(m,'validate_result',lambda *a:False)
    if failure=='binding': p.binding_revision='changed'
    if failure=='baseline': g['baseline_revision']='changed'
    if failure=='scope': p.key='other'
    with pytest.raises(ArchiveProofError): verify(p,g,t,o,s)
    assert not w


def test_change_during_readonly_sync_is_rejected(verifier,monkeypatch):
    m,p,g,t,o,s,w,cmd=verifier
    reads=iter([s.files,s.files,{}])
    monkeypatch.setattr(m,'read_once',lambda *a:next(reads))
    with pytest.raises(ArchiveProofError,match='source_changed'): verify(p,g,t,o,s)
    assert not w


def test_issue_not_migrated_is_rejected():
    from app.governance.archive_proof import _archive
    import yaml
    oid='BUG-9001-example'
    files={'issues/bugs/_registry.yaml':yaml.safe_dump({'entries':[{'id':oid,'path':f'issues/bugs/review/{oid}/'}]}).encode()}
    with pytest.raises(ArchiveProofError,match='not_promoted'): _archive(files,oid)

# Real guard persistence exercises the reconciliation hook separately from proof parsing.
from test_chat import chat, create, queued


@pytest.mark.parametrize('reject', [False, True])
def test_reconcile_wrapper_proof_confirms_once_or_keeps_failure(chat, monkeypatch, reject):
    from app.governance import execution_context as context, execution_guard as guards
    from app.governance.snapshot import Snapshot
    client, factory = chat
    cid = create(client)
    tid = queued(factory, cid, 'completed')
    project = SimpleNamespace(key='project', root=None, space_id='space', repository_id='repo',
                              readonly=False, binding_revision='test')
    monkeypatch.setattr(context.scope, 'authorize', lambda *a, **kw: project)
    monkeypatch.setattr(context.scope, 'visible', lambda *a, **kw: True)
    snapshot = Snapshot({}, 'after')
    monkeypatch.setattr(context, 'stable', lambda *a: snapshot)
    monkeypatch.setattr(context, 'stage_map', lambda *a: {CID: 'done'})
    monkeypatch.setattr(context.store, 'read', lambda *a: {'phase': 'terminal', 'steps': []})
    monkeypatch.setattr('app.governance.execution_validation.validate_result', lambda *a: True)
    calls = []
    def proof(*args):
        calls.append(args)
        if reject:
            raise ArchiveProofError('archive_spec_merge_mismatch')
        return {'verification_source': 'archive_source_revalidation'}
    monkeypatch.setattr('app.governance.archive_proof.verify', proof)
    with factory() as db:
        guards.acquire(db, scope_key='project', object_id=CID, operation_id=tid,
                       conversation_id=cid, owner_id='alice', action='opsx-archive',
                       confirmed_stage='acceptance', baseline_revision='before')
        db.commit()
        context.reconcile(db, 'alice', project)
        db.commit()
    with factory() as db:
        row = guards.read(db, 'project', CID)
        if reject:
            assert row['state'] == 'needs_review'
            assert row['reason_code'] == 'archive_spec_merge_mismatch'
            assert row['confirmed_stage'] == 'acceptance'
        else:
            assert row['state'] == 'validated'
            assert row['confirmed_stage'] == 'done'
            context.reconcile(db, 'alice', project)
            assert len(calls) == 1


def test_archive_display_time_compatibility_is_target_and_file_scoped(tmp_path):
    from app.governance.archive_workflow_check import timestamp_only_projection as compatible
    path=tmp_path/'iterations/change/sprint-010/sprint.md'
    before='| BUG | done | archived `fix-example`（2026-10-19 23:45:09） |'
    after=before.replace('23:45:09','23:53:43')
    assert compatible(path,tmp_path,CID,before,after)
    assert not compatible(path,tmp_path,CID,before,after.replace('done','in_sprint'))
    assert not compatible(path,tmp_path,CID,before,after+' extra')
    assert not compatible(path,tmp_path,'other-change',before,after)
    assert not compatible(tmp_path/'issues/bugs/trace.md',tmp_path,CID,before,after)
    assert not compatible(path,tmp_path,CID,before,after.replace('fix-example','other-change'))
    assert not compatible(path,tmp_path,CID,before,after.replace('archived','applied'))


def test_archive_workflow_check_forces_readonly_and_restores_hook(tmp_path, monkeypatch):
    import sys
    from app.governance.archive_workflow_check import main
    original = lambda *args: True
    patch_module = SimpleNamespace(persist_markdown=original)
    monkeypatch.setitem(sys.modules, 'workflow_sync', SimpleNamespace(patch=patch_module))
    def engine(argv):
        assert argv == ['--event','opsx.archive','--change',CID,'--sprint','auto','--check']
        with pytest.raises(ValueError, match='write_forbidden'):
            patch_module.persist_markdown(tmp_path/'file.md','new','old',True)
        assert patch_module.persist_markdown(tmp_path/'file.md','new','old',False)
        return 0
    monkeypatch.setitem(sys.modules, 'workflow_sync.engine', SimpleNamespace(main=engine))
    assert main([str(tmp_path),CID]) == 0
    assert patch_module.persist_markdown is original


def test_openspec_blank_separator_normalization_is_not_a_merge_failure():
    before, current = fixture()
    before[PREFIX+'specs/test/spec.md'] = ('## ADDED Requirements\n\n'+NEW.replace('\n\n', '\n\n\n')).encode()
    current[ARCHIVE+'/specs/test/spec.md'] = before[PREFIX+'specs/test/spec.md']
    validate_merge(before, current, CID, ARCHIVE)


def test_fenced_example_blank_lines_and_duplicate_requirements_remain_protected():
    before, current = fixture()
    original = NEW + '\n```text\na\n\n\nb\n```\n'
    before[PREFIX+'specs/test/spec.md'] = ('## ADDED Requirements\n\n'+original).encode()
    current[ARCHIVE+'/specs/test/spec.md'] = before[PREFIX+'specs/test/spec.md']
    current['openspec/specs/test/spec.md'] = (OLD + original.replace('a\n\n\nb', 'a\n\nb')).encode()
    with pytest.raises(ArchiveProofError): validate_merge(before, current, CID, ARCHIVE)
    before, current = fixture()
    current['openspec/specs/test/spec.md'] += NEW.encode()
    with pytest.raises(ArchiveProofError, match='duplicate'): validate_merge(before, current, CID, ARCHIVE)
