"""Fail-closed delivery identity tests; filesystem documents are parsed for real."""
from types import SimpleNamespace
import pytest
import yaml
from app.chat.service import ChatError
from app.moonbox_core import authority


@pytest.fixture
def facts(monkeypatch, tmp_path):
    change = {'iteration': 'sprint-015', 'requirement_id': 'REQ-0042-example', 'status': 'in_progress'}
    issue = {'iteration': 'sprint-015', 'status': 'in_sprint', 'openspec_changes': [{'change_id': 'example-change'}]}
    sprint = {'id': 'sprint-015', 'status': 'planning', 'plan': {'requirements': ['REQ-0042-example'], 'changes': ['example-change']}}
    access = {'write': True, 'visible': True}
    def authorize(*args, **kwargs):
        assert kwargs['write'] is True
        if not access['write']:
            raise ChatError(2601, '禁止操作', 403)
        return SimpleNamespace(root=tmp_path)
    monkeypatch.setattr(authority, 'authorize', authorize)
    monkeypatch.setattr(authority, 'visible', lambda *args: access['visible'])
    monkeypatch.setattr(authority, 'resolve', lambda *args: sprint)
    monkeypatch.setattr(authority, 'resolve_object', lambda *args: {'path': 'openspec/changes/example-change' if args[-1] == 'example-change' else 'issues/requirements/review/REQ-0042-example'})
    def write():
        for path, data in [('openspec/changes/example-change', change), ('issues/requirements/review/REQ-0042-example', issue)]:
            directory = tmp_path / path
            directory.mkdir(parents=True, exist_ok=True)
            (directory / 'trace.md').write_text('---\n' + yaml.safe_dump(data) + '---\n')
    def check():
        write()
        return authority.delivery(None, 'actor', 'space', 'repository', 'example-change')[1]
    return change, issue, sprint, access, check


def test_delivery_uses_requirement_chain_and_current_permissions(facts):
    change, issue, sprint, access, check = facts
    assert check()['delivery_root'] == 'REQ-0042-example'
    access['write'] = False
    with pytest.raises(ChatError) as error:
        check()
    assert error.value.status == 403


@pytest.mark.parametrize('mutation', [
    lambda c, i, s, a: c.update(sprint='sprint-016'),
    lambda c, i, s, a: c.update(sprint=['sprint-015']),
    lambda c, i, s, a: c.update(requirement_id=['REQ-0042-example']),
    lambda c, i, s, a: i.update(openspec_changes=[{'change_id': []}]),
    lambda c, i, s, a: i.update(iteration='sprint-016'),
    lambda c, i, s, a: s.update(status='closed'),
    lambda c, i, s, a: s['plan'].update(changes=[]),
    lambda c, i, s, a: s['plan'].update(requirements='REQ-0042-example'),
    lambda c, i, s, a: a.update(visible=False),
])
def test_changed_or_malformed_facts_deny_delivery(facts, mutation):
    change, issue, sprint, access, check = facts
    mutation(change, issue, sprint, access)
    with pytest.raises(ChatError):
        check()


def test_independent_change_owns_its_chain(facts):
    change, issue, sprint, access, check = facts
    del change['requirement_id']
    assert check()['delivery_root'] == 'example-change'
