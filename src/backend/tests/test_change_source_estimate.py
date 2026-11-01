"""BUG-0073: estimate ownership is checked before visibility projection."""
import pytest
import yaml
from app.governance.card_metadata import estimate_metadata
from test_change_visibility import cards, change, issue, context_database
from test_chat import chat
from test_governance_scope import fixture_tree, bind
from test_governance_board import write

SOURCE = 'BUG-0070-standalone-change-updated-time-missing'
TARGET = 'fix-standalone-change-updated-time'


def setup(root, value=3):
    source = issue(root, SOURCE)
    change(root, TARGET, bug=SOURCE, iteration='sprint-001')
    plan = dict(sprint_id='sprint-001', status='planning', bugs=[SOURCE], changes=[TARGET],
                capacity_person_days=30, scope_estimates=[dict(id=SOURCE, bug=SOURCE, change=TARGET, estimated_person_days=value)])
    write(root / 'iterations/change/sprint-001/sprint.yaml', yaml.safe_dump(plan))
    return source, plan


@pytest.mark.parametrize('number', [0, 0.5, 3])
def test_unique_source_is_read_only_and_survives_archive(tmp_path, number):
    root = fixture_tree(tmp_path); setup(root, number)
    before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
    for _ in range(2):
        row = next(r for r in cards(root).issues if r.id == TARGET)
        assert row.estimated_person_days == number
        assert row.estimate_source_issue_id == SOURCE
    assert all(p.read_bytes() == data for p, data in before.items())
    archive = root / 'openspec/archive' / ('2026-10-31-' + TARGET)
    archive.parent.mkdir(parents=True, exist_ok=True)
    (root / 'openspec/changes' / TARGET).rename(archive)
    row = next(r for r in cards(root).issues if r.id == TARGET)
    assert row.stage == 'done' and row.estimated_person_days == number


@pytest.mark.parametrize('value,status', [('3','invalid'), (True,'invalid'), (-1,'invalid'), (float('inf'),'invalid'), (float('nan'),'invalid')])
def test_invalid_source_values(value, status):
    row = dict(id=SOURCE, change=TARGET, estimated_person_days=value)
    result = estimate_metadata([row], TARGET, [], source_issue_id=SOURCE)
    assert result['estimate_status'] == status and result['estimated_person_days'] is None


def test_own_values_and_errors_take_priority():
    source = dict(id=SOURCE, change=TARGET, estimated_person_days=3)
    for number, status in [(2.5, 'available'), (-1, 'invalid')]:
        result = estimate_metadata([source, dict(id=TARGET, estimated_person_days=number)], TARGET, [], source_issue_id=SOURCE)
        assert result['estimate_status'] == status
        assert 'estimate_source_issue_id' not in result
        assert result['estimated_person_days'] == (number if status == 'available' else None)
    assert estimate_metadata([source, dict(id=TARGET, estimated_person_days=1), dict(id=TARGET, estimated_person_days=2)], TARGET, [], source_issue_id=SOURCE)['estimate_status'] == 'conflict'


def test_duplicate_and_conflicting_source_rows():
    row = dict(id=SOURCE, bug=SOURCE, change=TARGET, estimated_person_days=3)
    assert estimate_metadata([row,row],TARGET,[],source_issue_id=SOURCE)['estimated_person_days'] == 3
    for other in [dict(row,estimated_person_days=4), dict(row,change='other'), dict(row,bug='BUG-0099-other')]:
        assert estimate_metadata([row,other],TARGET,[],source_issue_id=SOURCE)['estimate_status'] == 'conflict'
    assert estimate_metadata([row],TARGET,[])['estimate_status'] == 'missing'


@pytest.mark.parametrize('sibling', ['active', 'archive', 'missing', 'hidden'])
def test_full_index_prevents_false_unique_source(tmp_path, sibling):
    root = fixture_tree(tmp_path); source, _ = setup(root)
    if sibling == 'missing':
        write(root / source['path'] / 'trace.md', '---\nopenspec_changes:\n- change_id: other\n---\n')
    else:
        change(root, '2026-10-01-other' if sibling == 'archive' else 'other',
               location='archive' if sibling == 'archive' else 'changes', bug=SOURCE)
    row = next(r for r in cards(root, lambda oid: oid != 'other').issues if r.id == TARGET)
    assert row.estimated_person_days is None and row.estimate_source_issue_id is None


def test_multiple_or_hidden_sources_never_leak(tmp_path):
    root = fixture_tree(tmp_path); setup(root)
    other = issue(root, 'REQ-0099-other')
    change(root, TARGET, bug=SOURCE, requirement=other['id'], iteration='sprint-001')
    row = next(r for r in cards(root).issues if r.id == TARGET)
    assert row.estimate_status == 'missing'
    result = cards(root, lambda oid: oid != SOURCE)
    assert SOURCE not in result.model_dump_json()
    assert TARGET not in [r.id for r in result.issues]


def test_summary_and_full_http_share_estimate_and_log_request(context_database, tmp_path, monkeypatch):
    client, factory = context_database
    root = fixture_tree(tmp_path / 'repo'); setup(root); bind(monkeypatch, root)
    before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
    for query in [{}, {'view':'summary'}]:
        response = client.get('/api/v1/requirement-center/context', params=dict(space_id='space',repository_id='repo', **query))
        assert response.status_code == 200
        row = next(r for r in response.json()['data']['issues'] if r['id'] == TARGET)
        assert row['estimated_person_days'] == 3 and row['estimate_source_issue_id'] == SOURCE
        assert response.headers['X-Request-ID']
    assert all(p.read_bytes() == data for p, data in before.items())

@pytest.mark.parametrize('state,stage', [('proposed','ready-dev'),('in_progress','development'),('applied','acceptance')])
def test_stage_changes_preserve_source_estimate(tmp_path, state, stage):
    root=fixture_tree(tmp_path); setup(root)
    write(root/'openspec/changes'/TARGET/'trace.md', '---\n'+yaml.safe_dump(dict(bug=SOURCE,iteration='sprint-001',status=state))+'---\n')
    row=next(r for r in cards(root).issues if r.id==TARGET)
    assert row.stage==stage and row.estimated_person_days==3


def test_missing_membership_or_explicit_target_is_not_inferred(tmp_path):
    root=fixture_tree(tmp_path); _,plan=setup(root)
    plan['bugs']=[]
    write(root/'iterations/change/sprint-001/sprint.yaml',yaml.safe_dump(plan))
    assert next(r for r in cards(root).issues if r.id==TARGET).estimate_status=='missing'
    row=dict(id=SOURCE,estimated_person_days=3)
    assert estimate_metadata([row],TARGET,[],source_issue_id=SOURCE)['estimated_person_days'] is None
