"""Scoped HTTP regression with real sessions and an isolated synthetic project."""
import json
import yaml
from sqlalchemy import text
from app.db.session import get_session_factory


def test_context_resolves_only_space_members(api_client, tmp_path, monkeypatch):
    response = api_client.post('/api/v1/auth/login', json={
        'username': 'superadmin', 'password': 'example-test-password', 'remember_me': False})
    assert response.status_code == 200
    headers = {'Authorization': 'Bearer ' + response.json()['data']['access_token']}
    with get_session_factory()() as db:
        actor = db.execute(text("SELECT id FROM admin_users WHERE username='superadmin'")).scalar_one()
        db.execute(text("UPDATE admin_users SET nickname='可读负责人' WHERE id=:id"), {'id': actor})
        db.commit()
    response = api_client.post('/api/v1/admin/users', headers=headers, json={
        'username': 'outsideowner', 'nickname': '不可泄漏名称', 'role': '前台用户'})
    assert response.status_code == 201
    outsider = response.json()['data']['user']['id']
    temporary_password = response.json()['data']['temporary_password']
    response = api_client.post('/api/v1/admin/spaces', headers=headers, json={
        'name': '合成空间', 'code': 'owner-test', 'owner_id': actor, 'product_id': 'owner-test',
        'product_name': '合成项目', 'expiry_type': 'long_term'})
    assert response.status_code == 201
    space = response.json()['data']['id']
    root = tmp_path / 'governance'
    for kind, prefix, owner in [('requirements', 'REQ', actor), ('bugs', 'BUG', outsider)]:
        oid = f'{prefix}-9100-owner-test'
        relative = f'issues/{kind}/plan/{oid}'
        folder = root / relative
        folder.mkdir(parents=True)
        (folder / 'capture.md').write_text('# 合成归属样本\n')
        (folder / 'trace.md').write_text(f'---\nstatus: captured\nowner: {owner}\n---\n')
        (root / 'issues' / kind / '_registry.yaml').write_text(yaml.safe_dump({'entries': [{
            'id': oid, 'path': relative, 'title': '合成归属样本', 'owner': owner, 'status': 'captured'}]}))
    query = {'space_id': space, 'repository_id': 'owner-test'}
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORIES', json.dumps([{'id': 'owner-test', 'space_id': space}]))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS', json.dumps([
        {'id': 'owner-test', 'space_id': space, 'governance_root': str(root)}]))
    before = (root / 'issues/requirements/_registry.yaml').read_bytes()
    for _ in range(2):
        response = api_client.get('/api/v1/requirement-center/context', headers=headers, params=query)
        assert response.status_code == 200
        cards = {card['type']: card for card in response.json()['data']['issues']}
        assert cards['requirement']['owner_display_name'] == '可读负责人'
        assert cards['requirement']['owner_key'] == actor
        assert cards['bug']['owner'] == '未知用户'
        assert '不可泄漏名称' not in response.text
    response = api_client.post('/api/v1/auth/login', json={
        'username': 'outsideowner', 'password': temporary_password, 'remember_me': False})
    assert response.status_code == 200
    outsider_headers = {'Authorization': 'Bearer ' + response.json()['data']['access_token']}
    assert api_client.get('/api/v1/requirement-center/context', headers=outsider_headers, params=query).status_code == 403
    assert api_client.get('/api/v1/requirement-center/context', params=query).status_code == 401
    with get_session_factory()() as db:
        db.execute(text("""INSERT INTO admin_space_members(id,space_id,user_id,role,created_at,updated_at)
            VALUES('owner-viewer-test',:space,:actor,'查看者','2026-10-19','2026-10-19')"""),
            {'space': space, 'actor': outsider})
        db.commit()
    response = api_client.get('/api/v1/requirement-center/context', headers=outsider_headers, params=query)
    assert response.status_code == 200
    cards = {card['type']: card for card in response.json()['data']['issues']}
    assert cards['requirement']['owner_display_name'] == '可读负责人'
    assert cards['bug']['owner_display_name'] == '不可泄漏名称'  # Now explicitly within the authorized space.
    assert api_client.post('/api/v1/requirement-center/capture-drafts', headers=outsider_headers, params=query).status_code == 403
    assert before == (root / 'issues/requirements/_registry.yaml').read_bytes()


def test_capture_confirmation_keeps_identity_and_resolves_first_read(api_client, tmp_path, monkeypatch):
    """Real HTTP draft/confirmation and writer, using disposable project data."""
    import time
    from sqlalchemy import select
    from app.governance import readiness, scope, writer
    from app.governance.capture_schema import confirmations

    login = api_client.post('/api/v1/auth/login', json={
        'username': 'superadmin', 'password': 'example-test-password', 'remember_me': False})
    headers = {'Authorization': 'Bearer ' + login.json()['data']['access_token']}
    with get_session_factory()() as db:
        actor = db.execute(text("SELECT id FROM admin_users WHERE username='superadmin'")).scalar_one()
        db.execute(text("UPDATE admin_users SET nickname='采集测试负责人' WHERE id=:id"), {'id': actor})
        db.commit()
    response = api_client.post('/api/v1/admin/spaces', headers=headers, json={
        'name': '采集验收空间', 'code': 'owner-capture', 'owner_id': actor,
        'product_id': 'owner-capture', 'product_name': '采集验收项目', 'expiry_type': 'long_term'})
    assert response.status_code == 201
    space = response.json()['data']['id']
    root = tmp_path / 'capture-project'
    for kind in ('requirements', 'bugs'):
        folder = root / 'issues' / kind
        folder.mkdir(parents=True)
        (folder / '_registry.yaml').write_text('next_id: 1\nentries: []\n')
    private = tmp_path / 'private'
    private.mkdir(mode=0o700)
    monkeypatch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(private))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORIES', json.dumps([{'id': 'owner-capture', 'space_id': space}]))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS', json.dumps([
        {'id': 'owner-capture', 'space_id': space, 'governance_root': str(root)}]))
    with get_session_factory()() as db:
        project = scope.authorize(db, actor, space, 'owner-capture', write=True)
    permit = private / 'maintenance.json'
    permit.write_text(json.dumps({'scope_key': project.key, 'binding_revision': project.binding_revision,
        'registered_writers': ['governance-controller'], 'external_writers_paused': True,
        'expires_at': time.time() + 120}))
    permit.chmod(0o600)
    readiness.publish()
    query = {'space_id': space, 'repository_id': 'owner-capture'}
    response = api_client.post('/api/v1/requirement-center/capture-drafts', headers=headers, params=query)
    assert response.status_code == 200
    draft = response.json()['data']
    url = '/api/v1/requirement-center/capture-drafts/' + draft['id']
    response = api_client.patch(url, headers=headers, params=query, json={
        'expected_revision': 1, 'text': '合成采集验收材料', 'media_ids': [], 'candidates': [
            {'type': 'requirement', 'title': '负责人名称采集验收需求', 'description': '合成需求验证首次名称解析',
             'priority': 'P2', 'source_refs': ['text']},
            {'type': 'bug', 'title': '负责人名称采集验收缺陷', 'description': '合成缺陷验证刷新名称一致',
             'severity': 'low', 'source_refs': ['text']}]})
    assert response.status_code == 200
    response = api_client.post(url + '/confirmations', headers=headers, params=query,
        json={'expected_revision': 2, 'idempotency_key': 'owner-capture-regression'})
    assert response.status_code == 202
    task_id = response.json()['data']['id']
    with get_session_factory()() as db:
        operation = db.scalar(select(confirmations.c.operation_id).where(confirmations.c.id == task_id))
        assert writer.process(db, operation)['state'] == 'applied'
    for _ in range(2):
        response = api_client.get('/api/v1/requirement-center/context', headers=headers, params=query)
        assert response.status_code == 200
        cards = response.json()['data']['issues']
        assert {card['type'] for card in cards} == {'requirement', 'bug'}
        assert all(card['owner_key'] == actor and card['owner'] == card['owner_display_name'] == '采集测试负责人'
                   for card in cards)
    for kind in ('requirements', 'bugs'):
        registry = yaml.safe_load((root / 'issues' / kind / '_registry.yaml').read_text())
        assert registry['entries'][0]['owner'] == actor
