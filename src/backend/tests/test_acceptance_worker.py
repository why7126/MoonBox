"""Missing deployment prerequisites produce durable refusals, not spinning queue rows."""
import pytest
from app.verification.acceptance_worker import run_one,root_directory
from app.verification.acceptance_state import Conflict
from test_acceptance_orchestration import state,create


def test_missing_template_is_durably_blocked_without_claim(state,tmp_path,monkeypatch):
    monkeypatch.setenv('MOONBOX_ACCEPTANCE_ROOT',str(tmp_path.resolve()/'private'))
    monkeypatch.delenv('MOONBOX_ACCEPTANCE_TEMPLATE',raising=False)
    item=create(state)
    result=run_one(state.factory,item['id'],'worker')
    assert result['status']=='blocked' and result['reason_code']=='acceptance_template_unavailable'
    assert result['lease_until']==0 and result['cleanup_state']=='not_created'


def test_untrusted_root_refuses_without_following_link(state,tmp_path,monkeypatch):
    destination=tmp_path/'outside';destination.mkdir()
    link=tmp_path/'link';link.symlink_to(destination,target_is_directory=True)
    monkeypatch.setenv('MOONBOX_ACCEPTANCE_ROOT',str(link))
    with pytest.raises(Conflict,match='acceptance_storage_untrusted'):root_directory()
    result=run_one(state.factory,create(state)['id'],'worker')
    assert result['status']=='blocked' and result['reason_code']=='acceptance_storage_untrusted'
    assert list(destination.iterdir())==[]
