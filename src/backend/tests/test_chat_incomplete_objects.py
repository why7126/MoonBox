import pytest
from sqlalchemy import insert
from test_chat import chat, governance, create, queued
from app.chat import relations, service
from app.chat.schema import object_access


def linked_history(client, factory, object_id):
    cid = create(client)
    url = f'/api/v1/chat/conversations/{cid}'
    assert client.put(url + '/relations', json={'primary': object_id}).status_code == 200
    tid = queued(factory, cid)
    with factory() as db:
        relations.capture_for_turn(db, 'alice', service.conversation(db, 'alice', cid), tid)
        db.commit()
    return url, tid


def test_incomplete_change_does_not_poison_original_history(chat, governance):
    client, factory = chat
    root, entries = governance
    url, tid = linked_history(client, factory, entries[0]['id'])
    pending = root / 'openspec/changes/new-pending-change'
    pending.mkdir(parents=True)
    marker = pending / '.openspec.yaml'; marker.write_text('schema: spec-driven\n')
    valid = root / 'openspec/changes/valid-change'; valid.mkdir()
    (valid / 'proposal.md').write_text('# Valid change\n')
    for path in [url, url + '/messages', url + '/relations', url + '/objects', f'/api/v1/chat/turns/{tid}/context']:
        assert client.get(path).status_code == 200, path
    assert client.get(url + '/relations').json()['data']['primary']['id'] == entries[0]['id']
    ids = [item['id'] for item in client.get(url + '/objects').json()['data']['items']]
    assert 'valid-change' in ids and 'new-pending-change' not in ids
    assert marker.read_text() == 'schema: spec-driven\n'
    assert list(pending.iterdir()) == [marker]
    assert client.put(url + '/relations', json={'primary': 'new-pending-change'}).status_code == 409  # active turn
    with factory() as db, pytest.raises(service.ChatError) as caught:
        relations.resolve_object(db, 'alice', 'space', 'repo', 'new-pending-change')
    assert caught.value.status == 503
    with factory() as db:
        db.execute(insert(object_access).values(space_id='space', repository_id='repo', object_id='new-pending-change', user_id='alice', can_read=0))
        db.commit()
        with pytest.raises(service.ChatError) as denied:
            relations.resolve_object(db, 'alice', 'space', 'repo', 'new-pending-change')
        assert denied.value.status == 403


def test_missing_document_is_not_a_space_permission_error(chat, governance):
    client, factory = chat
    root, entries = governance
    url, _ = linked_history(client, factory, entries[0]['id'])
    document = root / entries[0]['path'] / 'requirement.md'
    original = document.read_text(); document.unlink()
    for path in [url, url + '/messages', url + '/relations']:
        response = client.get(path)
        assert response.status_code == 503
        assert '尚未就绪' in response.json()['message']
    document.write_text(original)
    assert client.get(url + '/relations').status_code == 200


def test_review_promotion_keeps_authorized_history_readable_before_registry_update(chat, governance):
    client, factory = chat
    root, entries = governance
    oid = entries[0]['id']
    review = root / entries[0]['path']
    plan = root / f'issues/requirements/plan/{oid}'
    plan.parent.mkdir(parents=True, exist_ok=True)
    review.rename(plan)
    entries[0]['path'] = f'issues/requirements/plan/{oid}'
    (root / 'issues/requirements/_registry.yaml').write_text(__import__('json').dumps({'entries': entries}))
    url, _ = linked_history(client, factory, oid)
    plan.rename(review)
    assert client.get(url + '/relations').status_code == 200
    assert client.get(url + '/messages').status_code == 200
    with factory() as db:
        db.execute(insert(object_access).values(space_id='space', repository_id='repo',
            object_id=oid, user_id='alice', can_read=0))
        db.commit()
    assert client.get(url + '/relations').status_code == 403


@pytest.mark.parametrize('denied', ['acl', 'symlink'])
def test_real_object_permission_denial_still_blocks_history(chat, governance, tmp_path, denied):
    client, factory = chat
    root, entries = governance
    oid = entries[0]['id']
    url, _ = linked_history(client, factory, oid)
    if denied == 'acl':
        with factory() as db:
            db.execute(insert(object_access).values(space_id='space', repository_id='repo', object_id=oid, user_id='alice', can_read=0))
            db.commit()
    else:
        target = root / entries[0]['path'] / 'requirement.md'; target.unlink()
        outside = tmp_path / 'outside.md'; outside.write_text('private')
        target.symlink_to(outside)
        (target.parent / 'capture.md').write_text('fallback must not bypass denial')
    for path in [url, url + '/messages', url + '/relations']:
        assert client.get(path).status_code == 403
