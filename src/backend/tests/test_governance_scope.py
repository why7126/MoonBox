import json
from pathlib import Path
import pytest
from sqlalchemy import text
from app.chat.service import ChatError
from app.governance.scope import authorize, visible
from app.governance.snapshot import stable
from test_chat import chat


def fixture_tree(root):
    for folder in ('requirements','bugs'):
        target=root/'issues'/folder
        target.mkdir(parents=True)
        (target/'_registry.yaml').write_text('entries: []\n')
    return root


def bind(monkeypatch, root):
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{'id':'repo','space_id':'space','governance_root':str(root)}]))


def test_scope_membership_and_frozen_read(chat,tmp_path,monkeypatch):
    _,factory=chat;bind(monkeypatch,fixture_tree(tmp_path/'repo'))
    with factory() as db:
        assert not authorize(db,'alice','space','repo').readonly
        with pytest.raises(ChatError): authorize(db,'bob','space','repo')
        db.execute(text("INSERT INTO admin_space_members(id,space_id,user_id,role) VALUES('viewer','space','bob','查看者')"));db.commit()
        assert authorize(db,'bob','space','repo').readonly
        with pytest.raises(ChatError): authorize(db,'bob','space','repo',write=True)
        db.execute(text("UPDATE admin_spaces SET status='FROZEN'"));db.commit()
        assert authorize(db,'alice','space','repo').readonly
        with pytest.raises(ChatError): authorize(db,'alice','space','repo',write=True)
        with pytest.raises(ChatError): authorize(db,'alice','space','other')


def test_snapshot_worktree_deletion_parse_and_links(tmp_path):
    root=fixture_tree(tmp_path/'repo'); first=stable(root)
    doc=root/'issues'/'requirements'/'notes.md';doc.write_text('uncommitted')
    second=stable(root);assert first.revision != second.revision
    doc.unlink();assert stable(root).revision==first.revision
    doc.symlink_to(tmp_path/'secret')
    with pytest.raises(ChatError): stable(root)
    doc.unlink(); (root/'issues/requirements/_registry.yaml').write_text('entries: [')
    with pytest.raises(ChatError): stable(root)


def test_all_http_routes_require_scope(chat):
    client,_=chat
    routes=['/context','/issues/REQ-0001/documents/capture.md',
      '/issues/REQ-0001/documents/prototype.html/preview',
      '/changes/change/documents/design.md']
    for route in routes: assert client.get('/api/v1/requirement-center'+route).status_code==422
    for route in routes[1:2]+routes[3:]+['/changes/change/documents/tasks.md/tasks']:
        response=client.put('/api/v1/requirement-center'+route,json={'content':'draft','expected_version':'a'*64})
        assert response.status_code==422


def test_scope_document_and_no_cross_project_leak(chat,tmp_path,monkeypatch):
    from sqlalchemy import insert
    from app.chat.schema import object_access
    client,factory=chat;root=fixture_tree(tmp_path/'repo');bind(monkeypatch,root)
    issue=root/'issues/requirements/plan/REQ-0099-test';issue.mkdir(parents=True)
    (issue/'capture.md').write_text('project one private document')
    (issue/'prototype/web').mkdir(parents=True)
    (issue/'prototype/web/prototype.html').write_text('<h1>private prototype</h1>')
    (root/'issues/requirements/_registry.yaml').write_text('entries:\n  - id: REQ-0099-test\n    path: issues/requirements/plan/REQ-0099-test\n    status: captured\n')
    route='/api/v1/requirement-center/issues/REQ-0099/documents/capture.md'
    query={'space_id':'space','repository_id':'repo'}
    response=client.get(route,params=query);assert response.status_code==200,response.text
    assert response.json()['data']['content']=='project one private document'
    assert len(response.json()['data']['version'])==64
    preview='/api/v1/requirement-center/issues/REQ-0099/documents/prototype/web/prototype.html/preview'
    response=client.get(preview,params=query)
    assert response.status_code==200 and '<h1>private prototype</h1>' in response.text
    with factory() as db:
        db.execute(insert(object_access).values(space_id='space',repository_id='repo',object_id='REQ-0099-test',user_id='bob',can_read=1));db.commit()
    assert client.get(route,params=query).status_code==403
    assert client.get(preview,params=query).status_code==403
    query['repository_id']='other'
    assert client.get(route,params=query).status_code==503


def test_concurrent_projects_never_share_parser_root(chat,tmp_path,monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    client,_=chat;bindings=[]
    for identifier in ('one','two'):
        root=fixture_tree(tmp_path/identifier);issue=root/'issues/requirements/plan/REQ-0099-test';issue.mkdir(parents=True)
        (issue/'capture.md').write_text(identifier)
        (root/'issues/requirements/_registry.yaml').write_text('entries:\n  - id: REQ-0099-test\n    path: issues/requirements/plan/REQ-0099-test\n')
        bindings.append({'id':identifier,'space_id':'space','governance_root':str(root)})
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORIES',json.dumps([{'id':row['id'],'space_id':'space'} for row in bindings]))
    monkeypatch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps(bindings))
    def request(identifier):
        response=client.get('/api/v1/requirement-center/issues/REQ-0099/documents/capture.md',params={'space_id':'space','repository_id':identifier})
        assert response.status_code==200,response.text
        return response.json()['data']['content']
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert list(pool.map(request,['one','two','one','two']))==['one','two','one','two']


@pytest.mark.parametrize('location',['change','archive'])
def test_sprint_document_http_uses_authorized_issue_association(chat,tmp_path,monkeypatch,location):
    client,_=chat;root=fixture_tree(tmp_path/'repo');bind(monkeypatch,root)
    issue=root/'issues/requirements/review/REQ-0099-test';issue.mkdir(parents=True)
    (issue/'trace.md').write_text('---\nstatus: in_sprint\n---\n')
    (root/'issues/requirements/_registry.yaml').write_text('entries:\n  - id: REQ-0099-test\n    path: issues/requirements/review/REQ-0099-test\n    status: in_sprint\n    iteration: sprint-005\n')
    sprint=root/f'iterations/{location}/sprint-005';sprint.mkdir(parents=True)
    (sprint/'sprint.yaml').write_text('requirements: [REQ-0099-test]\n')
    (sprint/'sprint.md').write_text('# Associated Sprint')
    route='/api/v1/requirement-center/issues/REQ-0099/documents/sprint.md';query={'space_id':'space','repository_id':'repo'}
    response=client.get(route,params=query)
    assert response.status_code==200,response.text
    assert response.json()['data']['content']=='# Associated Sprint'
    assert client.get(route).status_code==422
    assert client.get(route.replace('REQ-0099','REQ-0098'),params=query).status_code==403
    (sprint/'sprint.md').unlink()
    assert client.get(route,params=query).status_code==404


def test_change_read_materializes_once_and_logs_safe_timings(chat, tmp_path, monkeypatch, caplog):
    from contextlib import contextmanager
    from app.governance import reader
    client, _ = chat
    root = fixture_tree(tmp_path / 'repo'); bind(monkeypatch, root)
    issue = root / 'issues/requirements/plan/REQ-0099-test'; issue.mkdir(parents=True)
    (issue / 'trace.md').write_text('---\nopenspec_changes: [{change_id: sample-change}]\n---\n')
    (root / 'issues/requirements/_registry.yaml').write_text('entries:\n  - id: REQ-0099-test\n    path: issues/requirements/plan/REQ-0099-test\n')
    change = root / 'openspec/changes/sample-change'; change.mkdir(parents=True)
    (change / 'tasks.md').write_text('# private-body')
    calls = []
    original = reader.cached_materialize
    @contextmanager
    def counted(snapshot, namespace):
        calls.append(snapshot.revision)
        with original(snapshot, namespace) as path: yield path
    monkeypatch.setattr(reader, 'cached_materialize', counted)
    with caplog.at_level('INFO', logger='moonbox.requirement_center'):
        response = client.get('/api/v1/requirement-center/changes/sample-change/documents/tasks.md', params={'space_id':'space','repository_id':'repo'})
    assert response.status_code == 200, response.text
    assert response.json()['data']['content'] == '# private-body'
    assert 'snapshot_and_fences;dur=' in response.headers['server-timing']
    assert 'parse;dur=' in response.headers['server-timing']
    assert 'private-body' not in response.headers['server-timing']
    assert len(calls) == 1
    log = next(r.message for r in caplog.records if 'read_timing' in r.message)
    assert 'snapshot_and_fences_ms' in log and 'object_authorization_ms' in log
    assert 'private-body' not in log and str(root) not in log
