import pytest
from sqlalchemy import create_engine,select
from sqlalchemy.orm import sessionmaker
from app.chat.schema import governance_applications
from app.governance import backup,store
from test_chat import chat
from test_governance_writer import writing,queue

@pytest.fixture(autouse=True)
def history_backup_store(writing,tmp_path,monkeypatch):
    from app.chat.backup import LocalBackupStore
    path=tmp_path/"history-backups";path.mkdir(mode=0o700)
    LocalBackupStore(path,initialize=True)
    monkeypatch.setenv("MOONBOX_CHAT_BACKUP_ROOT",str(path))


def test_database_and_private_images_restore_together(writing,tmp_path):
    oid=queue(writing);factory,project,_,_,_=writing
    archive=tmp_path/'offline-backup';target=tmp_path/'offline-restored'
    from app.governance.recovery_capabilities import publish
    publish('worker');publish('controller')
    assert backup.create(factory,archive)['offline_only']
    assert len(list((archive/'records').iterdir())) == 1
    assert backup.restore(archive,target)['maintenance_registration_required']
    engine=create_engine('sqlite:///'+str(target/'database.sqlite'))
    with sessionmaker(engine)() as db:
        assert db.scalar(select(governance_applications.c.id))==oid
    assert (target/'records'/oid/'operation.json').exists()
    assert not (target/'records/maintenance.json').exists()
    engine.dispose()


def test_backup_tampering_is_rejected_before_restore(writing,tmp_path):
    oid=queue(writing);factory,*_=writing;archive=tmp_path/'offline-backup'
    backup.create(factory,archive)
    (archive/'records'/oid/'operation.json').write_text('{}')
    with pytest.raises(ValueError):backup.restore(archive,tmp_path/'rejected-restore')
    assert not (tmp_path/'rejected-restore').exists()


def test_durable_recovery_restores_original_command_record(writing,tmp_path):
    from app.chat.schema import conversations, governance_candidates as candidates
    from app.governance import durable_recovery as policy
    from app.governance.direct_command_journal import record_id
    from app.governance.recovery_schema import operations
    aid=queue(writing);factory,project,_,_,_=writing
    with factory() as db:
        app=db.execute(select(governance_applications).where(governance_applications.c.id==aid)).mappings().one()
        candidate=db.execute(select(candidates).where(candidates.c.id==app['candidate_id'])).mappings().one()
        parent=db.execute(select(conversations).where(conversations.c.id==candidate['conversation_id'])).mappings().one()
        oid=policy.create(db,actor='alice',project=project,parent=parent,action='req-review',object_id=candidate['object_id'],request_key='original',request_hash='hash',source_hash='source',candidate_id=candidate['id'])
        db.commit()
    rid=record_id(parent['id'],'original');store.write(rid,'operation',{'schema_version':1,'phase':'terminal'})
    store.write(rid,'baseline',{'revision':'source'})
    archive=tmp_path/'durable-backup';target=tmp_path/'durable-restored'
    backup.create(factory,archive);backup.restore(archive,target)
    assert (target/'records'/rid/'operation.json').exists()
    assert (target/'records'/rid/'baseline.json').exists()
    engine=create_engine('sqlite:///'+str(target/'database.sqlite'))
    with sessionmaker(engine)() as db:assert db.scalar(select(operations.c.id))==oid
    engine.dispose()
