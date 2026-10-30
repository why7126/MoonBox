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


def test_document_gate_blocks_completion_and_resume_does_not_repeat_writes(normal,monkeypatch):
    c=normal
    original=ordinary.require_finalized
    checks=[]
    def check(root,change):
        checks.append(change)
        return original(root,change)
    monkeypatch.setattr(ordinary,'require_finalized',check)
    issue=c.project.root/'issues/bugs/archive/BUG-0001-sample'
    issue.mkdir(parents=True)
    (issue/'bug.md').write_text('---\nstatus: done\n---\nfix-sample\n')
    doc=issue/'acceptance.md';doc.write_text('[证据](missing.md)')
    with pytest.raises(ValueError,match='archive_finalization_blocked'):c.execute_normal()
    assert c.db.scalar(select(archive_operations.c.stage))=='synced'
    c.db.rollback()
    doc.write_text('验收已通过。')
    assert c.execute_normal()['stage']=='completed'
    assert c.calls.count('merge')==c.calls.count('move')==c.calls.count('sync')==1
    assert len(checks)==2


def test_completed_replay_rechecks_documents(normal,monkeypatch):
    c=normal
    assert c.execute_normal()['stage']=='completed'
    # Replay has separate history authorization; keep that independent gate isolated.
    monkeypatch.setattr(ordinary,'recovery_admission',lambda *a,**kw:{'ready':True})
    issue=c.project.root/'issues/bugs/archive/BUG-0001-sample'
    issue.mkdir(parents=True)
    (issue/'bug.md').write_text('---\nstatus: done\n---\nfix-sample\n当前交付状态：尚未实施。')
    with pytest.raises(ValueError,match='archive_finalization_blocked'):c.execute_normal()
    assert c.calls.count('merge')==c.calls.count('sync')==1
