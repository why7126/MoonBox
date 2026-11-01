"""BUG-0070: factual time sources, not file/query timestamps."""
import pytest
from app.governance.change_time import card_time, valid_time
from test_change_visibility import change, cards, issue
from test_governance_scope import fixture_tree

@pytest.mark.parametrize('raw', [None, '', '2026-02-30 12:00:00', '2026-10-31', 123, {}, '2026-10-31 25:00:00'])
def test_invalid_time(raw):
    assert valid_time(raw) is None

@pytest.mark.parametrize('trace,source', [
    ({'updated_at':'2026-10-31 12:00:00','created_at':'2026-09-01 12:00:00'},'updated'),
    ({'updated_at':'bad','created_at':'2026-09-01 12:00:00'},'created'),
    ({'execution':{'completed_at':'2026-10-31T04:00:00Z'}},'execution_completed'),
    ({'execution':{'completed_at':'bad','started_at':'2026-10-31 12:00:00'}},'execution_started'),
    ({'execution':'invalid'},'missing'),
])
def test_sources(trace,source):
    result=card_time(trace)
    assert result['card_time_source']==source
    if source!='missing': assert result['card_time'].endswith('+08:00')

@pytest.mark.parametrize('location,cid', [('changes','sample-change'),('archive','2026-10-31-sample-change')])
def test_card_projection_readonly(tmp_path,location,cid):
    root=fixture_tree(tmp_path)
    directory=change(root,cid,location=location,execution={'schema_version':1,'started_at':'2026-10-30 12:00:00','completed_at':'2026-10-31T04:00:00Z','last_event':'opsx.apply'})
    original=(directory/'trace.md').read_bytes()
    for _ in range(2):
        row=cards(root).issues[0]
        assert row.card_time=='2026-10-31T12:00:00+08:00'
        assert row.card_time_source=='execution_completed'
        assert row.updated_at == "更新时间未知"
    assert (directory/'trace.md').read_bytes()==original

def test_issue_linked_cards_keep_legacy_time(tmp_path):
    root=fixture_tree(tmp_path);issue(root,related_change='sample-change');change(root,updated_at='2026-10-31 12:00:00')
    row=cards(root).issues[0]
    assert row.card_time_source is None
    assert row.updated_at

from test_chat import chat
from test_governance_scope import bind


def test_api_summary_and_full_share_time_projection(chat, tmp_path, monkeypatch):
    from app.services import requirement_center
    monkeypatch.setattr(requirement_center, '_load_workspaces', lambda *args: [])
    root=fixture_tree(tmp_path/'repo')
    change(root, execution={'schema_version':1,'started_at':'2026-10-30 12:00:00','completed_at':'2026-10-31T04:00:00Z','last_event':'opsx.apply'})
    bind(monkeypatch,root)
    client,_=chat
    for view in ('summary','full'):
        response=client.get('/api/v1/requirement-center/context',params={'space_id':'space','repository_id':'repo','view':view})
        assert response.status_code==200, response.text
        row=next(r for r in response.json()['data']['issues'] if r['id']=='sample-change')
        assert row['card_time_source']=='execution_completed'
        assert row['card_time']=='2026-10-31T12:00:00+08:00'
