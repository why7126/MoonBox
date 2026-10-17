import copy

import pytest
import yaml

from app.chat.service import ChatError
from app.governance.candidates import frontmatter, validate
from app.governance.snapshot import stable
from app.governance.writer import process
from test_chat import chat
from test_governance_candidates import contents, bug_contents, front, OID, BASE, BUG_OID, BUG_BASE
from test_governance_writer import writing, queue


def review_files(bug=False, result='approved'):
    oid, base = (BUG_OID, BUG_BASE) if bug else (OID, BASE)
    field, primary, folder = ('bug_id', 'bug.md', 'bugs') if bug else ('requirement_id', 'requirement.md', 'requirements')
    before = (bug_contents() if bug else contents())[1]
    before[f'{base}/capture.md'] = front({field: oid})
    for name in (primary, 'trace.md'):
        meta, _ = frontmatter(before[f'{base}/{name}'])
        meta.update(status='pending_review', lifecycle_stage='plan')
        before[f'{base}/{name}'] = front(meta)
    if bug:
        before[f'{base}/root-cause.md'] = front({field: oid, 'status': 'confirmed'})
    registry, index = f'issues/{folder}/_registry.yaml', f'issues/{folder}/CHANGELOG.md'
    data = yaml.safe_load(before[registry])
    data['entries'][0].update(status='pending_review', lifecycle_stage='plan')
    before[registry] = yaml.safe_dump(data, allow_unicode=True).encode()
    before[index] = before[index].replace(b'draft', b'pending_review')
    target = base.replace('/plan/', '/review/') if result == 'approved' else base
    after = {p.replace(base, target): b.replace(base.encode(), target.encode()) for p, b in before.items()}
    for name in (primary, 'trace.md'):
        meta, _ = frontmatter(after[f'{target}/{name}'])
        meta.update(status=result, lifecycle_stage='review' if result == 'approved' else 'plan')
        if name == 'trace.md':
            meta.setdefault('lifecycle', {})['reviewed'] = '2026-09-30'
            if result == 'approved': meta['lifecycle']['approved'] = '2026-09-30'
        after[f'{target}/{name}'] = front(meta)
    after[f'{target}/review.md'] = front({field: oid, 'result': result})
    data = yaml.safe_load(after[registry])
    data['entries'][0].update(status=result, path=target, lifecycle_stage='review' if result == 'approved' else 'plan')
    after[registry] = yaml.safe_dump(data, allow_unicode=True).encode()
    after[index] = after[index].replace(b'pending_review', result.encode())
    return before, after, oid, base


@pytest.mark.parametrize('bug', [False, True])
@pytest.mark.parametrize('result', ['approved', 'rejected', 'deferred'])
def test_review_result_and_migration(bug, result):
    before, after, oid, base = review_files(bug, result)
    checked = validate(before, after, oid, base, 'bug-review' if bug else 'req-review')
    assert any(f['path'].endswith('/review.md') for f in checked['files'])
    assert any(f['after_sha256'] is None for f in checked['files']) == (result == 'approved')


@pytest.mark.parametrize('bug', [False, True])
@pytest.mark.parametrize('fields', [{'status': 'approved'}, {'result': 'approved'},
    {'status': 'approved', 'result': 'approved'}])
def test_review_accepts_compatible_outcome_fields(bug, fields):
    before, after, oid, base = review_files(bug)
    path = base.replace('/plan/', '/review/') + '/review.md'
    meta, _ = frontmatter(after[path]); meta.pop('result')
    after[path] = front({**meta, **fields})
    assert validate(before, after, oid, base, 'bug-review' if bug else 'req-review')['files']


@pytest.mark.parametrize('fields,reason', [
    ({'status': 'approved', 'result': 'rejected'}, 'outcome_conflict'),
    ({'status': None, 'result': 'approved'}, 'outcome_conflict'),
    ({}, 'outcome'), ({'status': 'unknown'}, 'outcome'),
])
def test_review_outcome_failures_are_specific(fields, reason):
    before, after, oid, base = review_files(True)
    path = base.replace('/plan/', '/review/') + '/review.md'
    meta, _ = frontmatter(after[path]); meta.pop('result')
    after[path] = front({**meta, **fields})
    with pytest.raises(ChatError) as error:
        validate(before, after, oid, base, 'bug-review')
    assert error.value.details == {'reason': reason}


@pytest.mark.parametrize('event', ['bug.complete', 'bug.review', 'unrelated'])
def test_review_acceptance_can_preserve_or_sync_event(event):
    before, after, oid, base = review_files(True)
    original = front({'bug_id': oid}) + b'\nsource_event: bug.complete\n'
    before[base + '/acceptance.md'] = original
    after[base.replace('/plan/', '/review/') + '/acceptance.md'] = original.replace(b'bug.complete', event.encode())
    if event == 'unrelated':
        with pytest.raises(ChatError) as error: validate(before, after, oid, base, 'bug-review')
        assert error.value.details == {'reason': 'acceptance_scope'}
    else:
        assert validate(before, after, oid, base, 'bug-review')['files']


@pytest.mark.parametrize('failure', ['outside', 'missing', 'old_path', 'state', 'other_doc', 'lifecycle'])
def test_review_rejects_partial_or_expanded_results(failure):
    before, after, oid, base = review_files()
    target = base.replace('/plan/', '/review/')
    if failure == 'outside': after['src/unsafe.py'] = b'bad'
    elif failure == 'missing': del after[f'{target}/capture.md']
    elif failure == 'old_path': after[f'{base}/trace.md'] = before[f'{base}/trace.md']
    elif failure == 'state': after[f'{target}/requirement.md'] = before[f'{base}/requirement.md']
    elif failure == 'other_doc': after[f'{target}/capture.md'] += b'changed'
    else: after[f'{target}/trace.md'] = after[f'{target}/trace.md'].replace(b'captured: ', b'overwritten: ')
    with pytest.raises(ChatError): validate(before, after, oid, base, 'req-review')


def test_review_controller_migrates_and_replays(writing):
    factory, project, _, _, permit = writing
    before, after, oid, base = review_files()
    for p in stable(project.root).files:
        (project.root/p).unlink()
    for p,b in before.items():
        path=project.root/p;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b)
    operation=queue((factory,project,before,after,permit),candidate_action='req-review',object_id=oid,base_path=base)
    with factory() as db:
        assert process(db,operation)['state']=='applied'
        assert process(db,operation)['state']=='applied'
    assert stable(project.root).files==after
    assert not (project.root/base).exists()


@pytest.mark.parametrize('crash_after', [0, 5, 7])
def test_review_restart_replays_tombstones(writing, crash_after):
    factory, project, _, _, permit = writing
    before, after, oid, base = review_files()
    for p in stable(project.root).files: (project.root/p).unlink()
    for p,b in before.items():
        path=project.root/p;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b)
    operation=queue((factory,project,before,after,permit),candidate_action='req-review',object_id=oid,base_path=base)
    def crash(index, path):
        if index == crash_after: raise RuntimeError('simulated controller restart')
    with factory() as db:
        with pytest.raises(RuntimeError): process(db, operation, after_write=crash)
    with factory() as db:
        assert process(db, operation)['state'] == 'applied'
    assert stable(project.root).files == after
    assert not (project.root/base).exists()


@pytest.mark.parametrize('rejected,conflict', [(False, False), (False, True), (True, False),
    (True, True), (True, 'later'), (True, 'outside')])
@pytest.mark.parametrize('stale_projection', [False, True])
def test_retained_review_recovery_uses_original_turn(chat, tmp_path, monkeypatch, conflict, rejected, stale_projection):
    import json
    from sqlalchemy import insert, select
    from app.chat import service
    from app.chat.schema import turns, governance_applications, governance_candidates
    from app.chat.workspace import git, prepare_workspace, snapshot
    from app.governance import store
    from app.governance.preparation import prepare_object_session, _command_baseline_id
    from app.governance.review_recovery import recover
    from app.governance.readiness import publish
    _, factory = chat
    root=tmp_path/'repo';root.mkdir()
    private=tmp_path/'private';private.mkdir(mode=0o700)
    workspaces=tmp_path/'workspaces';workspaces.mkdir()
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{
        'id':'repo','space_id':'space','governance_root':str(root),'workspace_root':str(workspaces)}]))
    before,after,oid,base=review_files()
    for p,b in before.items():
        target=root/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
    git(root,'init');git(root,'add','.')
    git(root,'-c','user.name=Test','-c','user.email=test@invalid','commit','-m','baseline')
    publish()
    with factory() as db:
        parent=prepare_object_session(db,'alice','space','repo',oid,action='req-review')
        workspace=prepare_workspace(root,workspaces,parent['conversation_id'])['path']
        # A previous complete application must not stand in for this review turn.
        from app.governance import scope
        project=scope.authorize(db,'alice','space','repo',write=True)
        previous=service.identity()
        previous['created_at'] = previous['updated_at'] = '2026-01-01T00:00:00+00:00'
        db.execute(insert(governance_candidates).values(**previous,actor_id='alice',space_id='space',
            repository_id='repo',scope_key=project.key,conversation_id=parent['conversation_id'],
            object_id=oid,action='req-complete',binding_revision=project.binding_revision,
            baseline_hash=stable(root).revision,state='applied',revision=1))
        manifest={p:{k:v for k,v in item.items() if k in ('kind','sha256','executable')}
            for p,item in snapshot(workspace)['files'].items()}
        store.write(previous['id'],'baseline',{'workspace_manifest':manifest})
        store.write(previous['id'],'result',{'after':{}})
        turn=service.identity()
        db.execute(insert(turns).values(**turn,conversation_id=parent['conversation_id'],client_request_id='review',
            prompt=f'/req-review {oid}',status='completed',executor_turn_id='executed'))
        store.write(_command_baseline_id(parent['conversation_id'],'review'),'baseline',{
            'object_id':oid,'files':{p:b.decode() for p,b in before.items()}})
        db.commit()
        for p in before.keys()-after.keys(): (workspace/p).unlink()
        for p,b in after.items():
            target=workspace/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b)
        if stale_projection:
            for name in ('_registry.yaml', 'CHANGELOG.md'):
                path = f'issues/requirements/{name}'
                (workspace/path).write_bytes(before[path])
        preserved=snapshot(workspace)['hash']
        if rejected:
            from app.governance.preparation import _candidate_id
            identity = _candidate_id('alice',project.key,oid,'req-review','review')
            db.execute(insert(governance_candidates).values(**identity,actor_id='alice',space_id='space',
                repository_id='repo',scope_key=project.key,conversation_id=parent['conversation_id'],
                object_id=oid,action='req-review',binding_revision=project.binding_revision,
                baseline_hash=stable(root).revision,state='rejected',revision=1,
                prepared_turn_id=turn['id'],turn_id=turn['id'],error_code='governance_validation_failed'))
            store.write(identity['id'],'baseline',{'files':{p:b.decode() for p,b in before.items()},
                'base_path':base,'workspace_manifest':manifest})
            db.commit()
            from sqlalchemy import update
            from app.governance.preparation import collect, list_candidates
            review_path = base.replace('/plan/', '/review/') + '/review.md'
            meta, _ = frontmatter(after[review_path])
            (workspace/review_path).write_bytes(front({**meta, 'status': 'rejected'}))
            db.execute(update(governance_candidates).where(governance_candidates.c.id==identity['id']).values(state='running'))
            full_parent = service.conversation(db,'alice',parent['conversation_id'])
            collect(db,full_parent,turn['id'],workspace,'completed')
            public = list_candidates(db,'alice',parent['conversation_id'])['items'][0]
            assert public['error_code']=='review_outcome_conflict'
            assert public['state']=='rejected'
            assert not db.scalar(select(governance_applications.c.id))
            (workspace/review_path).write_bytes(after[review_path])
        if conflict:
            if conflict == 'later':
                db.execute(insert(turns).values(**service.identity(),conversation_id=parent['conversation_id'],
                    client_request_id='later',prompt='later',status='completed'))
                db.commit()
            elif conflict == 'outside':
                (workspace/'unauthorized.txt').write_text('unexpected change')
                preserved=snapshot(workspace)['hash']
            else:
                (root/f'{base}/trace.md').write_bytes(before[f'{base}/trace.md']+b'\nexternal edit')
            with pytest.raises(ChatError): recover(db,'alice',turn['id'])
            assert snapshot(workspace)['hash']==preserved
            return
        recovered=recover(db,'alice',turn['id'])
        assert recovered['state']=='pending'
        candidate=db.execute(select(governance_candidates).where(governance_candidates.c.id==recovered['candidate_id'])).mappings().one()
        assert candidate['turn_id']==turn['id']
        assert candidate['id']!=previous['id'] and candidate['action']=='req-review'
        operation=db.execute(select(governance_applications)).mappings().one()
        assert process(db,operation['id'])['state']=='applied'
        assert recover(db,'alice',turn['id'])['state']=='applied'
        from app.governance.review_finalization import finalize_review
        retained = dict(after)
        if stale_projection:
            for name in ('_registry.yaml', 'CHANGELOG.md'):
                path = f'issues/requirements/{name}'
                retained[path] = before[path]
        assert stable(root).files==finalize_review(before,retained,oid,base,'req-review')
        if stale_projection:
            assert stable(workspace).files == stable(root).files
            from app.governance.preparation import _checkpoint_applied_workspace
            _checkpoint_applied_workspace(db, service.conversation(db,'alice',parent['conversation_id']), workspace)
            assert not git(workspace,'status','--porcelain').strip()
        else:
            assert snapshot(workspace)['hash']==preserved


@pytest.mark.parametrize('bug', [False, True])
@pytest.mark.parametrize('outcome', ['approved', 'rejected', 'deferred'])
def test_review_finalization_repairs_only_stale_projections(bug, outcome):
    from app.governance.review_finalization import finalize_review
    before, after, oid, base = review_files(bug, outcome)
    action = 'bug-review' if bug else 'req-review'
    folder = 'bugs' if bug else 'requirements'
    stale = dict(after)
    for name in ('_registry.yaml', 'CHANGELOG.md'):
        path = f'issues/{folder}/{name}'
        stale[path] = before[path]
    fixed = finalize_review(before, stale, oid, base, action)
    assert validate(before, fixed, oid, base, action)['files']
    assert finalize_review(before, fixed, oid, base, action) == fixed
    assert {p for p in fixed if fixed[p] != stale.get(p)} <= {
        f'issues/{folder}/_registry.yaml', f'issues/{folder}/CHANGELOG.md'}


@pytest.mark.parametrize('bug', [False, True])
def test_review_finalization_updates_full_index_stage_and_next_action(bug):
    from app.governance.review_finalization import finalize_review
    before, after, oid, base = review_files(bug)
    folder = 'bugs' if bug else 'requirements'
    index = f'issues/{folder}/CHANGELOG.md'
    kind = 'bug' if bug else 'req'
    if bug:
        row = f'| {oid} | 本地缺陷业务主题 | medium | pending_review | plan | 无 | 无 | 2026-09-30 12:00:00 | `/bug-review {oid}` | `{base}/trace.md` |\n'
    else:
        row = f'| {oid} | 本地需求业务主题 | pending_review | plan | P2 | 无 | 无 | 2026-09-30 12:00:00 | `/req-review {oid}` | `{base}/trace.md` |\n'
    before[index] = front({'purpose': 'index', 'updated_at': '2026-09-30'}, row)
    after[index] = before[index]
    after[f'issues/{folder}/_registry.yaml'] = before[f'issues/{folder}/_registry.yaml']
    fixed = finalize_review(before, after, oid, base, f'{kind}-review')
    cells = [cell.strip() for cell in fixed[index].decode().splitlines()[-1].strip('|').split('|')]
    assert cells[4 if bug else 3] == 'review'
    assert cells[8] == f'`/sprint-propose --{kind} {oid}`'
    assert validate(before, fixed, oid, base, f'{kind}-review')['files']


@pytest.mark.parametrize('failure', ['conclusion', 'root', 'missing', 'outside', 'registry'])
def test_review_finalization_does_not_bypass_gates(failure):
    from app.governance.review_finalization import finalize_review
    before, after, oid, base = review_files(True)
    target = base.replace('/plan/', '/review/')
    after['issues/bugs/_registry.yaml'] = before['issues/bugs/_registry.yaml']
    if failure == 'conclusion':
        after[target+'/review.md'] = front({'bug_id': oid, 'status': 'rejected', 'result': 'approved'})
    elif failure == 'root':
        after[target+'/root-cause.md'] = front({'bug_id': oid, 'status': 'hypothesis'})
    elif failure == 'missing':
        del after[target+'/capture.md']
    elif failure == 'outside':
        after['src/unauthorized.py'] = b'changed'
    else:
        after['issues/bugs/_registry.yaml'] = after['issues/bugs/_registry.yaml'].replace(b'pending_review', b'in_sprint')
    original = dict(after)
    with pytest.raises(ChatError): finalize_review(before, after, oid, base, 'bug-review')
    assert after == original


@pytest.mark.parametrize('bug', [False, True])
@pytest.mark.parametrize('interrupt', [False, True])
def test_source_review_collect_and_interrupted_finalization_recovery(chat, tmp_path, monkeypatch, bug, interrupt):
    import json
    from sqlalchemy import insert, select
    from app.chat import service
    from app.chat.schema import turns, governance_candidates, governance_applications
    from app.chat.workspace import snapshot
    from app.governance import scope, store, writer
    from app.governance.preparation import prepare_object_session, _candidate_id, collect
    from app.governance.review_recovery import recover
    _, factory = chat
    root = tmp_path/'source'; root.mkdir()
    private = tmp_path/'private'; private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(private))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS', json.dumps([{
        'id': 'repo', 'space_id': 'space', 'governance_root': str(root),
        'source_root': str(root), 'workspace_mode': 'source'}]))
    before, after, oid, base = review_files(bug)
    action = 'bug-review' if bug else 'req-review'
    folder = 'bugs' if bug else 'requirements'
    for p, body in before.items():
        path=root/p; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(body)
    sync_script=root/'scripts/sync-workflow-status.py'
    sync_script.parent.mkdir(parents=True, exist_ok=True)
    sync_script.write_text('import sys\nsys.exit(0)\n')
    with factory() as db:
        info=prepare_object_session(db,'alice','space','repo',oid,action=action)
        parent=service.conversation(db,'alice',info['conversation_id'])
        project=scope.authorize(db,'alice','space','repo',write=True)
        turn=service.identity()
        db.execute(insert(turns).values(**turn, conversation_id=parent['id'], client_request_id='review',
            prompt=f'/{action} {oid}', status='completed', executor_turn_id='executed'))
        candidate=_candidate_id('alice',project.key,oid,action,'review')
        db.execute(insert(governance_candidates).values(**candidate, actor_id='alice', space_id='space',
            repository_id='repo', scope_key=project.key, conversation_id=parent['id'], object_id=oid,
            action=action, binding_revision=project.binding_revision, baseline_hash=stable(root).revision,
            state='running', revision=1, prepared_turn_id=turn['id']))
        manifest={p:{k:v for k,v in item.items() if k in ('kind','sha256','executable')}
                  for p,item in snapshot(root)['files'].items()}
        store.write(candidate['id'],'baseline',{'workspace_mode':'source','base_path':base,
            'files':{p:b.decode() for p,b in before.items()},'workspace_manifest':manifest})
        db.commit()
        for p in before.keys()-after.keys(): (root/p).unlink()
        for p, body in after.items():
            path=root/p; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(body)
        for name in ('_registry.yaml','CHANGELOG.md'):
            p=f'issues/{folder}/{name}'; (root/p).write_bytes(before[p])
        original_replace=writer.replace_file
        def fail_second(*args, **kwargs):
            if args[1].endswith('_registry.yaml'):
                raise OSError('simulated interruption')
            return original_replace(*args, **kwargs)
        if interrupt: monkeypatch.setattr(writer,'replace_file',fail_second)
        collect(db,parent,turn['id'],root,'completed')
        if interrupt:
            assert db.scalar(select(governance_candidates.c.state)) == 'rejected'
            assert not db.scalar(select(governance_applications.c.id))
            monkeypatch.setattr(writer,'replace_file',original_replace)
            assert recover(db,'alice',turn['id'])['state'] == 'applied'
        assert db.scalar(select(governance_candidates.c.state)) == 'applied'
        assert db.execute(select(governance_applications)).mappings().one()['phase'] == 'verified'
        assert validate(before,stable(root).files,oid,base,action)['files']
        assert recover(db,'alice',turn['id'])['state'] == 'applied'


def test_rejected_source_review_restores_moved_plan_directory(chat, tmp_path, monkeypatch):
    import json
    from sqlalchemy import insert, select
    from app.chat import service
    from app.chat.schema import turns, governance_candidates, governance_applications
    from app.chat.workspace import snapshot
    from app.governance import scope, store
    from app.governance.preparation import prepare_object_session, _candidate_id, collect
    _, factory = chat
    root = tmp_path / 'source'; root.mkdir()
    private = tmp_path / 'private'; private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(private))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS', json.dumps([{
        'id': 'repo', 'space_id': 'space', 'governance_root': str(root),
        'source_root': str(root), 'workspace_mode': 'source'}]))
    before, after, oid, base = review_files()
    for name, body in before.items():
        path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(body)
    with factory() as db:
        info = prepare_object_session(db, 'alice', 'space', 'repo', oid, action='req-review')
        parent = service.conversation(db, 'alice', info['conversation_id'])
        project = scope.authorize(db, 'alice', 'space', 'repo', write=True)
        turn = service.identity()
        db.execute(insert(turns).values(**turn, conversation_id=parent['id'], client_request_id='review',
            prompt=f'/req-review {oid}', status='completed', executor_turn_id='executed'))
        candidate = _candidate_id('alice', project.key, oid, 'req-review', 'review')
        db.execute(insert(governance_candidates).values(**candidate, actor_id='alice', space_id='space',
            repository_id='repo', scope_key=project.key, conversation_id=parent['id'], object_id=oid,
            action='req-review', binding_revision=project.binding_revision,
            baseline_hash=snapshot(root)['hash'], state='running', revision=1,
            prepared_turn_id=turn['id']))
        manifest = {name: {key: value for key, value in item.items() if key in ('kind', 'sha256', 'executable')}
                    for name, item in snapshot(root)['files'].items()}
        store.write(candidate['id'], 'baseline', {'workspace_mode': 'source', 'base_path': base,
            'files': {name: body.decode() for name, body in before.items()}, 'workspace_manifest': manifest})
        db.commit()
        for name in before.keys() - after.keys():
            (root / name).unlink()
        (root / base).rmdir()
        for name, body in after.items():
            path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(body)
        altered = base.replace('/plan/', '/review/') + '/capture.md'
        (root / altered).write_bytes((root / altered).read_bytes() + b'forbidden edit')
        collect(db, parent, turn['id'], root, 'completed')
        row = db.execute(select(governance_candidates)).mappings().one()
        assert row['state'] == 'rejected'
        assert row['error_code'] == 'review_unrelated_document_edit'
        assert not db.scalar(select(governance_applications.c.id))
        assert snapshot(root)['files'].keys() == manifest.keys()
        assert {name: (root / name).read_bytes() for name in before} == before
