"""Sprint closure keeps the same project operation across move/sync interruption."""
from pathlib import Path
import pytest
from sqlalchemy import select
from test_replacement_coordinator import orchestration
from app.governance import sprint_archive_coordinator as sprint,replacement_coordinator
from app.governance.replacement_schema import archive_operations
from app.chat.schema import governance_project_locks as locks


@pytest.fixture
def closing(orchestration,monkeypatch):
    c=orchestration
    folder=c.project.root/'iterations/change/sprint-001';folder.mkdir(parents=True)
    (folder/'sprint.yaml').write_text('sprint_id: sprint-001\nstatus: active\nchanges: []\n')
    for name in ('sprint.md','acceptance-report.md','release-note.md'):
        (folder/name).write_text('---\ntitle: 合成关闭验证\n---\n保留人工记录。\n')
    for name in ('project_lock','authorize_write','load'):
        monkeypatch.setattr(sprint,name,getattr(replacement_coordinator,name))
    monkeypatch.setattr(sprint,'require_final',lambda root,sid,**kwargs:sprint.resolve(root,sid))
    calls=[];fault={'sync':False}
    class Driver:
        def __init__(self,project):self.scripts=project.root/'scripts'
        def _run(self,args,root):
            calls.append(Path(args[1]).name)
            if fault['sync'] and Path(args[1]).name=='sync-workflow-status.py':raise OSError('injected sync failure')
    run=lambda:sprint.execute(c.db,actor='owner',space_id='space',repository_id='repo',sprint='sprint-001',operation_id='sprint-operation',driver_type=Driver)
    return c,run,calls,fault


def test_closure_and_replay(closing):
    c,run,calls,_=closing
    assert run()['stage']=='completed'
    assert not (c.project.root/'iterations/change/sprint-001').exists()
    assert run()['replayed']
    assert calls.count('sync-workflow-status.py')==1
    assert c.db.scalar(select(locks.c.operation_id)) is None


def test_original_closure_recovers_after_move(closing):
    c,run,calls,fault=closing;fault['sync']=True
    with pytest.raises(OSError):run()
    c.db.rollback()
    assert c.db.scalar(select(archive_operations.c.stage))=='move_verified'
    assert c.db.scalar(select(locks.c.operation_id))=='sprint-operation'
    fault['sync']=False
    assert run()['stage']=='completed'


def test_modified_signoff_after_interruption_stays_blocked(closing):
    c,run,_,fault=closing;fault['sync']=True
    with pytest.raises(OSError):run()
    c.db.rollback()
    report=c.project.root/'iterations/archive/sprint-001/acceptance-report.md'
    report.write_text(report.read_text()+'人工签署发生变化。\n')
    fault['sync']=False
    with pytest.raises(ValueError,match='sprint_inputs_changed'):run()
    assert c.db.scalar(select(locks.c.operation_id))=='sprint-operation'


def test_completed_replay_allows_later_unrelated_archives(closing):
    c,run,_,_=closing
    run()
    later=c.project.root/'openspec/archive/later-change';later.mkdir(parents=True)
    (later/'trace.md').write_text('合法的后续归档。')
    assert run()['replayed']


def test_completed_replay_rejects_changed_signoff(closing):
    c,run,_,_=closing
    run()
    report=c.project.root/'iterations/archive/sprint-001/acceptance-report.md'
    report.write_text(report.read_text()+'修改签署。')
    with pytest.raises(ValueError,match='sprint_inputs_changed'):run()


def test_generated_metadata_does_not_change_manual_fingerprint(tmp_path):
    folder=tmp_path/'iterations/change/sprint-001';folder.mkdir(parents=True)
    report=folder/'acceptance-report.md';report.write_text('# 验收\n\n人工签署: true\n')
    item={'path':'iterations/change/sprint-001'}
    before=sprint.fingerprint(tmp_path,item)
    report.write_text('---\ncreated_at: 2026-10-22 12:00:00\nupdated_at: 2026-10-22 12:00:00\nnote: 自动投影\n---\n\n# 验收\n\n人工签署: true\n')
    assert sprint.fingerprint(tmp_path,item)==before
    report.write_text(report.read_text().replace('人工签署: true','人工签署: false'))
    assert sprint.fingerprint(tmp_path,item)!=before


def test_workflow_note_preserves_existing_signoff():
    import sys
    from types import SimpleNamespace
    sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
    from workflow_sync.patch import sprint_summary_for_acceptance
    plan=SimpleNamespace(changes=['done-change'])
    changes={'done-change':SimpleNamespace(state='archived')}
    assert '待人工 sign-off' in sprint_summary_for_acceptance(plan,changes)
    assert '人工 sign-off 已完成' in sprint_summary_for_acceptance(plan,changes,signed_off=True)
