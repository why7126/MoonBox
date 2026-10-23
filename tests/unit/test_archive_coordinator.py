"""Ordinary and controlled archives must share the project fence."""
import json
import pytest
from sqlalchemy import select,delete,update
from test_replacement_coordinator import orchestration
from app.governance import archive_coordinator as ordinary
from app.governance import replacement_coordinator,controlled_successor
from app.governance.replacement_schema import proposals,archive_operations
from app.chat.schema import governance_project_locks as locks


@pytest.fixture
def normal(orchestration,monkeypatch):
    c=orchestration
    c.db.execute(delete(proposals));c.db.commit()
    for name in ('project_lock','authorize_write','change_acceptance','load'):
        monkeypatch.setattr(ordinary,name,getattr(replacement_coordinator,name))
    monkeypatch.setattr(ordinary,'evidence_digest',lambda *args:c.value['acceptance_sha256'])
    c.execute_normal=lambda:ordinary.execute(c.db,actor='owner',space_id='space',repository_id='repo',
        change='fix-sample',operation_id='normal-operation',driver_type=c.driver)
    return c


@pytest.mark.parametrize('point',[None,'merge','move','sync'])
def test_normal_archive_resumes_once_and_releases_shared_fence(normal,point):
    c=normal;c.fault['at']=point
    if point:
        with pytest.raises(OSError):c.execute_normal()
        c.db.rollback()
        assert c.db.scalar(select(locks.c.operation_id))=='normal-operation'
        c.fault['at']=None
    assert c.execute_normal()['stage']=='completed'
    assert c.calls.count('merge')==1 and c.calls.count('move')==1 and c.calls.count('sync')==1
    assert c.db.scalar(select(archive_operations.c.stage))=='completed'
    assert c.db.scalar(select(locks.c.operation_id)) is None


def test_normal_resume_rejects_external_spec_changes(normal):
    c=normal;c.fault['at']='move'
    with pytest.raises(OSError):c.execute_normal()
    c.db.rollback();c.spec.write_text('unrelated writer changed the tree')
    with pytest.raises(ValueError,match='archive_result_unknown'):c.execute_normal()
    assert c.db.scalar(select(locks.c.operation_id))=='normal-operation'


def test_normal_path_cannot_consume_controlled_approval(orchestration,monkeypatch):
    c=orchestration
    c.db.execute(update(proposals).values(state='claimed'));c.db.commit()
    monkeypatch.setattr(ordinary,'load',replacement_coordinator.load)
    monkeypatch.setattr(ordinary,'project_lock',replacement_coordinator.project_lock)
    with pytest.raises(ValueError,match='controlled_proposal_required'):
        ordinary.execute(c.db,actor='owner',space_id='space',repository_id='repo',change='fix-sample',
            operation_id='normal-operation',driver_type=c.driver)
    assert not c.db.execute(select(archive_operations)).first() and not c.calls
