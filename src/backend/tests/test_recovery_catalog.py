import pytest
from sqlalchemy import create_engine, insert, select, update
from sqlalchemy.orm import sessionmaker
from app.chat.schema import metadata, conversations, turns
from app.chat.content_schema import versions, objects, entries
from app.moonbox_core.schema import TABLES, session_bindings
from app.moonbox_core.workspaces import register_main, stamp
from app.moonbox_rollout.schema import TABLES as RECOVERY_TABLES, points
from app.moonbox_rollout.catalog import publish, reference, rotate, unprotect_manual
from test_managed_worktree_git import repo


@pytest.fixture
def data(tmp_path, repo):
    engine = create_engine('sqlite:///' + str(tmp_path / 'catalog.db'))
    metadata.create_all(engine, tables=[conversations, turns, objects, versions, entries, *TABLES, *RECOVERY_TABLES])
    factory = sessionmaker(engine)
    with factory.begin() as db:
        main = register_main(db, 'space', 'repo', repo[0].root)
        db.execute(insert(conversations).values(id='c', created_at=stamp(), updated_at=stamp(), owner_id='a', space_id='space', repository_id='repo', title='test'))
        db.execute(insert(turns).values(id='t', created_at=stamp(), updated_at=stamp(), conversation_id='c', client_request_id='r', status='completed', prompt='test'))
        db.execute(insert(session_bindings).values(conversation_id='c', workspace_id=main['id']))
        for n in range(15):
            db.execute(insert(versions).values(id=str(n), created_at=stamp(), updated_at=stamp(), conversation_id='c', turn_id='t', phase='after', status='complete', manifest_hash=str(n).zfill(64)))
    yield factory, main['id']
    engine.dispose()


def test_reuse_pin_rotation_and_expired_reference_rejection(data):
    factory, wid = data
    with factory.begin() as db:
        first = publish(db, wid, '0', policy_version='p', head_commit='h', changed=True)
        assert publish(db, wid, '0', policy_version='p', head_commit='h', changed=True)['id'] == first['id']
        reference(db, wid, first['id'], 'initial', 'initial', 'initial_baseline')
        reference(db, wid, first['id'], 'manual', 'actor', 'manual')
        assert unprotect_manual(db, wid, first['id'], 'actor') == 1
        reference(db, wid, first['id'], 'initial', 'initial', 'initial_baseline')
        for n in range(1, 15):
            publish(db, wid, str(n), policy_version='p', head_commit='h', changed=True)
        expired = rotate(db, wid)
        assert len(expired) == 4
        assert first['id'] not in expired
        assert len(db.execute(select(points).where(points.c.state == 'complete')).all()) == 11
        with pytest.raises(ValueError, match='unavailable'):
            reference(db, wid, expired[0], 'manual', 'actor', 'manual')


def test_incomplete_content_and_wrong_workspace_rejected(data):
    factory, wid = data
    with factory.begin() as db:
        db.execute(update(versions).where(versions.c.id == '0').values(status='building'))
        with pytest.raises(ValueError, match='snapshot_unavailable'):
            publish(db, wid, '0', policy_version='p', head_commit='h', changed=True)
        with pytest.raises(ValueError, match='workspace_unavailable'):
            publish(db, 'foreign', '1', policy_version='p', head_commit='h', changed=True)


def test_exact_twelve_ordinary_and_three_protected_points(data):
    factory, wid = data
    with factory.begin() as db:
        protected = set()
        for n in range(15):
            point = publish(db,wid,str(n),policy_version='p',head_commit='h',changed=True)
            if n < 3:
                reference(db,wid,point['id'],'manual',str(n),'manual')
                protected.add(point['id'])
        expired = rotate(db,wid)
        alive = set(db.scalars(select(points.c.id).where(points.c.state=='complete')))
        assert len(expired) == 2 and len(alive) == 13
        assert protected <= alive and not protected.intersection(expired)
