"""No-op projection batching and immutable pure-parser reuse under live reads."""
from types import SimpleNamespace

import pytest
from sqlalchemy import update
from test_chat import chat
from test_governance_writer import writing
from test_direct_completion import direct_scene, OID
from app.governance import execution_context as context, execution_guard as guards
from app.governance import read_memo, snapshot
from app.services import requirement_center as legacy


def test_parser_clone_preserves_cycles_aliases_and_custom_types():
    from datetime import date
    shared = {'nested': [1, 'value', date(2026, 10, 28)]}
    original = [shared, shared]
    original.append(original)
    custom = SimpleNamespace(owner=original)
    original.append(custom)
    copied = read_memo.clone(original)
    assert copied is not original and copied[0] is copied[1]
    assert copied[0] is not shared and copied[2] is copied
    assert copied[3] is not custom and copied[3].owner is copied
    copied[0]['nested'].append('changed')
    assert len(shared['nested']) == 3


@pytest.mark.parametrize('locations,expected', [([], False),
    (['openspec/archive/2026-10-27-example-fix'], True),
    (['openspec/changes/example-fix'], False),
    (['openspec/archive/2026-10-27-example-fix', 'openspec/archive/2026-10-26-example-fix'], False),
    (['openspec/archive/2026-10-27-example-fix-extra'], False)])
def test_external_archive_pattern_built_once_without_changing_identity(monkeypatch, locations, expected):
    from app.governance import execution_validation as validation
    files = {f'docs/unrelated-{n}.md': b'other' for n in range(1000)}
    for base in locations:
        files.update({base + '/' + name: b'---\nstatus: applied\n---\ncontent'
                      for name in ('trace.md', 'proposal.md', 'design.md', 'tasks.md')})
    escaped, original = [], validation.re.escape
    monkeypatch.setattr(validation.re, 'escape', lambda value: escaped.append(value) or original(value))
    assert validation._change(files, 'example-fix', 'opsx-archive', external=True) is expected
    assert escaped == ['example-fix']


def test_external_batch_has_bounded_commits_and_rechecks_invalid_facts(direct_scene, monkeypatch):
    from sqlalchemy import event
    from app.governance import execution_validation
    factory, project, *_ = direct_scene
    snap = SimpleNamespace(revision='batch', files={})
    monkeypatch.setattr(context, 'stable', lambda root: snap)
    validated = []
    monkeypatch.setattr(execution_validation, 'validate_external',
                        lambda files, oid, stage: validated.append(oid) or False)
    items = [(f'synthetic-{n}', 'unknown') for n in range(65)]
    with factory() as db:
        commits = []
        event.listen(db, 'after_commit', lambda session: commits.append(1))
        context.reconcile_external_batch(db, project, items, snap, actor='alice')
        assert len(commits) == 3  # Entry boundary plus two bounded write batches.
        before = [dict(guards.read(db, project.key, oid)) for oid, _ in items]
        assert all(row['state'] == 'needs_review' for row in before)
        context.reconcile_external_batch(db, project, items, snap, actor='alice')
        assert len(validated) == 130  # Rejected evidence is never an admission cache.
        assert [dict(guards.read(db, project.key, oid)) for oid, _ in items] == before
        assert len(commits) == 4  # No repeated identical DML or version churn.


@pytest.mark.parametrize('failure', ['permission', 'binding', 'source', 'concurrent_guard'])
def test_external_batch_keeps_all_guards_unchanged_on_fence_failure(direct_scene, monkeypatch, failure):
    from sqlalchemy import insert
    from app.chat.service import ChatError
    from app.governance import execution_validation, scope
    from app.governance.verification_transaction import VerificationPlan
    factory, project, *_ = direct_scene
    snap = SimpleNamespace(revision='batch', files={})
    monkeypatch.setattr(context, 'stable', lambda root: SimpleNamespace(
        revision='changed' if failure == 'source' else 'batch'))
    monkeypatch.setattr(execution_validation, 'validate_external', lambda *args: True)
    items = [('synthetic-a', 'capture'), ('synthetic-b', 'capture')]
    original = VerificationPlan.apply
    def raced(plan, **kwargs):
        if failure == 'permission':
            monkeypatch.setattr(scope, 'visible', lambda db, actor, project, oid: oid != 'synthetic-b')
        elif failure == 'binding':
            monkeypatch.setattr(scope, 'authorize', lambda *a, **kw: SimpleNamespace(binding_revision='changed'))
        elif failure == 'concurrent_guard':
            with factory() as other:
                other.execute(insert(guards.execution_guards).values(scope_key=project.key,
                    object_id='synthetic-b', version=9, state='running', action='opsx-apply',
                    confirmed_stage='development', updated_at='concurrent'))
                other.commit()
        return original(plan, **kwargs)
    monkeypatch.setattr(VerificationPlan, 'apply', raced)
    with factory() as db:
        if failure == 'source':
            with pytest.raises(ChatError) as error:
                context.reconcile_external_batch(db, project, items, snap, actor='alice')
            assert error.value.status == 503
        else:
            context.reconcile_external_batch(db, project, items, snap, actor='alice')
        assert guards.read(db, project.key, 'synthetic-a') is None
        other = guards.read(db, project.key, 'synthetic-b')
        if failure == 'concurrent_guard':
            assert other['version'] == 9 and other['state'] == 'running'
        else:
            assert other is None


def test_request_snapshot_change_rejects_pending_guard_update(direct_scene, monkeypatch):
    from app.chat.service import ChatError
    factory, project, tid, _, _ = direct_scene
    def planned(plan, *args, **kwargs):
        plan.execute(update(guards.execution_guards).where(
            guards.execution_guards.c.operation_id == tid).values(state='validated'))
    monkeypatch.setattr(context, '_reconcile_plan', planned)
    monkeypatch.setattr(context, 'stable', lambda root: SimpleNamespace(revision='changed'))
    with factory() as db:
        before = dict(guards.read(db, project.key, OID))
        with pytest.raises(ChatError) as error:
            context.reconcile(db, 'alice', project, snapshot=SimpleNamespace(revision='old'))
        assert error.value.status == 503
        assert dict(guards.read(db, project.key, OID)) == before


def test_pure_memo_reuses_only_immutable_revision_and_copies_values(tmp_path, monkeypatch):
    read_memo.clear()
    source = snapshot.Snapshot({'issues/item.md': b'---\ntitle: first\n---\n'}, 'one')
    calls = []
    # Count underlying disk reads without replacing the memo wrapper.
    from pathlib import Path
    read_text = Path.read_text
    def reading(path, *a, **kw):
        if path.name == 'item.md': calls.append(1)
        return read_text(path, *a, **kw)
    monkeypatch.setattr(Path, 'read_text', reading)
    for _ in range(2):
        with snapshot.cached_materialize(source, 'repair') as root:
            with legacy.using_governance_root(root, immutable=True, shared_memo=True):
                value = legacy._frontmatter(root / 'issues/item.md')
                assert value['title'] == 'first'
                value['title'] = 'must not leak'
    assert len(calls) == 1
    changed = snapshot.Snapshot({'issues/item.md': b'---\ntitle: other\n---\n'}, 'two')
    with snapshot.cached_materialize(changed, 'repair') as root:
        with legacy.using_governance_root(root, immutable=True, shared_memo=True):
            assert legacy._frontmatter(root / 'issues/item.md')['title'] == 'other'
    assert len(calls) == 2
    # Mutable callers never receive the cross-request parser cache.
    doc = tmp_path / 'item.md'; doc.write_text('---\ntitle: mutable\n---\n')
    with legacy.using_governance_root(tmp_path, shared_memo=True):
        assert legacy._frontmatter(doc)['title'] == 'mutable'
        doc.write_text('---\ntitle: changed\n---\n')
        assert legacy._frontmatter(doc)['title'] == 'changed'


def test_memo_budget_evicts_and_does_not_retain_oversized_values(monkeypatch):
    read_memo.clear()
    monkeypatch.setattr(read_memo, 'MAX_BYTES', 2048)
    for n in range(4):
        with read_memo.lease(str(n)) as memo: memo['value'] = str(n)
    assert len(read_memo._versions) <= 2
    with read_memo.lease('large') as memo: memo['value'] = 'x' * 4096
    assert 'large' not in read_memo._versions
    assert sum(x[1] for x in read_memo._versions.values()) <= 2048
    read_memo.clear()


def test_batch_noop_reads_current_admission_and_changed_revision_uses_fences(direct_scene, monkeypatch):
    factory, project, tid, _, _ = direct_scene
    snap = SimpleNamespace(revision='same')
    with factory() as db:
        db.execute(update(guards.execution_guards).where(guards.execution_guards.c.operation_id == tid)
                   .values(state='idle', result_revision='same', action='external-sync'))
        db.commit()
        seen = []
        monkeypatch.setattr(context, 'reconcile_external', lambda *a, **kw: seen.append(a[2]))
        context.reconcile_external_batch(db, project, [(OID, 'acceptance')], snap, actor='alice')
        assert seen == []
        # This is not an admission cache: a concurrent acquisition remains busy.
        with factory() as other:
            other.execute(update(guards.execution_guards).where(guards.execution_guards.c.operation_id == tid)
                          .values(state='running', result_revision=None))
            other.commit()
        assert context.visible_state(db, 'alice', project, OID)['can_send'] is False
        db.rollback()
        with factory() as other:
            other.execute(update(guards.execution_guards).where(guards.execution_guards.c.operation_id == tid)
                          .values(state='idle', result_revision='different'))
            other.commit()
        context.reconcile_external_batch(db, project, [(OID, 'acceptance')], snap, actor='alice')
        assert seen == [OID]


def test_review_guards_never_bypass_successor_verification(direct_scene, monkeypatch):
    factory, project, tid, _, _ = direct_scene
    with factory() as db:
        db.execute(update(guards.execution_guards).where(guards.execution_guards.c.operation_id == tid)
                   .values(state='needs_review', action='bug-review', result_revision='same'))
        db.commit()
        seen = []
        monkeypatch.setattr(context, 'reconcile_external', lambda *a, **kw: seen.append(a[2]))
        context.reconcile_external_batch(db, project, [(OID, 'acceptance')], SimpleNamespace(revision='same'), actor='alice')
        assert seen == [OID]


def test_registry_parsing_reused_only_for_same_immutable_root(tmp_path, monkeypatch):
    from test_governance_scope import fixture_tree
    root = fixture_tree(tmp_path / 'repo')
    snap = snapshot.stable(root)
    snap = snapshot.Snapshot(snap.files, snap.revision)  # Warm validation omits parsed registries.
    calls, original = [], context.safe_load
    monkeypatch.setattr(context, 'safe_load', lambda value: calls.append(1) or original(value))
    read_memo.clear()
    with snapshot.cached_materialize(snap, ('registry-test',)) as private:
        for _ in range(2):
            index = context.IdentityIndex(snap)
            with legacy.using_governance_root(private, immutable=True, registry_index=index, shared_memo=True):
                result = legacy._read_yaml(private / 'issues/bugs/_registry.yaml')
                result['entries'].append({'id': 'poison'})
                assert not index.registry('bugs')['entries']
    assert len(calls) == 2
    with snapshot.cached_materialize(snap, ('other-project',)) as private:
        with legacy.using_governance_root(private, immutable=True,
                registry_index=context.IdentityIndex(snap), shared_memo=True):
            pass
    assert len(calls) == 4
    read_memo.clear()


@pytest.mark.parametrize('actor', ['alice', 'bob'])
@pytest.mark.parametrize('guard_state', ['idle', 'running', 'needs_review', 'validated'])
def test_batched_display_matches_point_reads_and_reloads_current_state(direct_scene, actor, guard_state):
    from sqlalchemy import insert
    from app.chat import service
    from app.chat.schema import conversations, relations, governance_candidates
    factory, project, tid, *_ = direct_scene
    with factory() as db:
        guard = guards.read(db, project.key, OID)
        cid = guard['conversation_id']
        db.execute(update(guards.execution_guards).where(guards.execution_guards.c.object_id == OID).values(state=guard_state))
        db.execute(update(conversations).where(conversations.c.id == cid).values(active_turn_id=tid))
        db.execute(insert(relations).values(conversation_id=cid, object_id='legacy', role='primary', title='legacy'))
        db.execute(insert(governance_candidates).values(**service.identity(), actor_id='alice',
            space_id=project.space_id, repository_id=project.repository_id, scope_key=project.key,
            conversation_id=cid, object_id='pending', action='bug-review', binding_revision=project.binding_revision,
            baseline_hash='baseline', state='pending'))
        db.commit()
        ids = [OID, 'legacy', 'pending', 'empty']
        expected = {oid: context.visible_state(db, actor, project, oid) for oid in ids}
        actual = context.visible_states(db, actor, project, ids)
        assert {oid: row[1] for oid, row in actual.items()} == expected
        # A later request must see changed guards and conversation visibility.
        db.execute(update(guards.execution_guards).where(guards.execution_guards.c.object_id == OID).values(state='needs_review'))
        db.execute(update(conversations).where(conversations.c.id == cid).values(archived=1))
        db.commit()
        fresh = context.visible_states(db, actor, project, ids)
        assert fresh[OID][1]['can_send'] is False
        assert fresh['legacy'][1]['view_conversation_id'] is None
        assert {oid: row[1] for oid, row in fresh.items()} == {oid: context.visible_state(db, actor, project, oid) for oid in ids}


def test_display_batch_bounds_queries_and_project_scope(direct_scene):
    from sqlalchemy import insert, event
    factory, project, *_ = direct_scene
    with factory() as db:
        db.execute(insert(guards.execution_guards).values(scope_key='other', object_id='empty-0',
            state='running', version=1, updated_at='now'))
        db.commit()
        calls = []
        engine = db.get_bind()
        def query(*args): calls.append(1)
        event.listen(engine, 'before_cursor_execute', query)
        try:
            actual = context.visible_states(db, 'alice', project, [f'empty-{n}' for n in range(600)])
        finally:
            event.remove(engine, 'before_cursor_execute', query)
        assert len(calls) == 9
        assert all(state['can_send'] for _, state in actual.values())


def test_immutable_metadata_memo_is_version_scoped_and_live_reads_stay_fresh(tmp_path, monkeypatch):
    from pathlib import Path
    read_memo.clear()
    original = Path.is_file
    calls = []
    def is_file(path):
        calls.append(str(path)); return original(path)
    monkeypatch.setattr(Path, 'is_file', is_file)
    for revision, files in [('one', {'issues/item.md': b'one'}), ('two', {'issues/other.md': b'two'})]:
        with snapshot.cached_materialize(snapshot.Snapshot(files, revision), 'metadata-test') as root:
            for _ in range(2):
                with legacy.using_governance_root(root, immutable=True, shared_memo=True):
                    before = len(calls)
                    exists = legacy._snapshot_is_file(root / 'issues/item.md')
                    assert exists is (revision == 'one')
                    assert legacy._snapshot_resolve(root / 'issues/../issues') == root / 'issues'
                    assert legacy._safe_issue_dir('../outside') is None
                    legacy._snapshot_is_file(root / 'issues/item.md')
                    assert len(calls) - before <= 1
    live = tmp_path / 'live'; live.mkdir()
    with legacy.using_governance_root(live):
        assert not legacy._snapshot_is_file(live / 'new.md')
        (live / 'new.md').write_text('new')
        assert legacy._snapshot_is_file(live / 'new.md')
    assert sum(row[1] for row in read_memo._versions.values()) <= read_memo.MAX_BYTES


def test_sprint_association_memo_tracks_snapshot_versions_and_mutable_reads(tmp_path):
    read_memo.clear()

    oid, sid = 'BUG-0001-test', 'sprint-001'
    entry = {'id': oid, 'iteration': sid}
    for member in (True, False):
        files = {'iterations/change/sprint-001/sprint.md': b'# Sprint',
                 'iterations/change/sprint-001/sprint.yaml':
                     (f'bugs: [{oid}]\n' if member else 'bugs: []\n').encode()}
        snap = snapshot.Snapshot(files, snapshot.digest(files))
        with snapshot.cached_materialize(snap, 'sprint-association') as root:
            for _ in range(2):
                with legacy.using_governance_root(root, immutable=True, shared_memo=True):
                    assert legacy._sprint_contains(sid, oid) is member
                    assert (legacy._sprint_document(entry, {}) is not None) is member
    live = tmp_path / 'live'
    sprint = live / 'iterations/change/sprint-001'
    sprint.mkdir(parents=True)
    (sprint / 'sprint.md').write_text('# Sprint')
    yaml = sprint / 'sprint.yaml'
    yaml.write_text(f'bugs: [{oid}]\n')
    with legacy.using_governance_root(live):
        assert legacy._sprint_contains(sid, oid)
        assert legacy._sprint_document(entry, {}) is not None
        yaml.write_text('bugs: []\n')
        assert not legacy._sprint_contains(sid, oid)
        assert legacy._sprint_document(entry, {}) is None
    read_memo.clear()


def test_root_cause_facts_are_revision_scoped_and_defensively_copied(tmp_path):
    from app.governance.change_index import _root_cause_fields
    read_memo.clear()
    for state in ('confirmed', 'hypothesis'):
        body = f'---\nroot_cause_status: {state}\n---\n# 根因分析\n已观察到重复读取造成额外耗时。\n'.encode()
        files = {'issues/bugs/review/BUG-0001-test/root-cause.md': body}
        snap = snapshot.Snapshot(files, snapshot.digest(files))
        with snapshot.cached_materialize(snap, 'root-cause-facts') as root:
            for _ in range(2):
                with legacy.using_governance_root(root, immutable=True, shared_memo=True):
                    facts = _root_cause_fields(root / 'issues/bugs/review/BUG-0001-test')
                    assert facts['root_cause_state'] == ('confirmed' if state == 'confirmed' else 'pending')
                    facts['root_cause_state'] = 'poison'
    issue = tmp_path / 'issue'; issue.mkdir()
    doc = issue / 'root-cause.md'
    with legacy.using_governance_root(tmp_path):
        assert _root_cause_fields(issue) == {}
        doc.write_bytes(body)
        assert _root_cause_fields(issue)['root_cause_state'] == 'pending'
        doc.unlink()
        outside = tmp_path / 'outside.md'; outside.write_bytes(body)
        doc.symlink_to(outside)
        assert _root_cause_fields(issue) == {}
    read_memo.clear()
