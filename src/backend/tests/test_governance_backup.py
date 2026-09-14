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
    assert backup.create(factory,archive)['offline_only']
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
