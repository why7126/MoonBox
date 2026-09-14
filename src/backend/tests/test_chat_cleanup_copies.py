from pathlib import Path
import pytest
from sqlalchemy import insert,select,update,text
from test_chat import chat,create
from app.chat import service
from app.chat.cleanup import process_copies
from app.chat.schema import conversations,cleanup_jobs


def test_copy_cleanup_retries_and_never_removes_code(chat,tmp_path):
    client,factory=chat;cid=create(client)
    code=tmp_path/'code';code.write_text('preserve')
    history=tmp_path/'history';history.write_text('synthetic conversation')
    backup=tmp_path/'backup';backup.write_text('synthetic backup')
    with factory() as db:
        db.execute(update(conversations).where(conversations.c.id==cid).values(deleted_at=service.now()))
        db.execute(insert(cleanup_jobs).values(**service.identity(),conversation_id=cid,owner_id='alice',executor_thread_id='thread',main_status='purged',executor_status='pending',backup_status='pending'));db.commit()
        def failed(_):raise OSError('unavailable')
        def purge(_):history.unlink(missing_ok=True);return not history.exists()
        assert not process_copies(db,cid,failed,lambda _:False)
        assert db.scalar(select(cleanup_jobs.c.executor_status))=='retry'
        assert not process_copies(db,cid,purge,lambda _:False)
        assert db.scalar(select(cleanup_jobs.c.executor_status))=='purged'
        def purge_backup(_):backup.unlink(missing_ok=True);return not backup.exists()
        assert process_copies(db,cid,failed,purge_backup)  # Already purged executor not called again.
        assert process_copies(db,cid,failed,failed)
        assert db.scalar(select(conversations.c.cleanup_status).where(conversations.c.id==cid))=='complete'
    assert code.read_text()=='preserve'


def test_cleanup_status_requires_current_owner_and_space_access(chat):
    from app.chat.cleanup import status
    client,factory=chat;cid=create(client)
    with factory() as db:
        db.execute(update(conversations).where(conversations.c.id==cid).values(deleted_at=service.now()))
        db.execute(insert(cleanup_jobs).values(**service.identity(),conversation_id=cid,owner_id='alice',main_status='purged',executor_status='pending',backup_status='pending'))
        db.commit()
        assert status(db,'alice',cid)['executor_status']=='pending'
        with pytest.raises(service.ChatError):status(db,'bob',cid)
        db.execute(text("UPDATE admin_spaces SET status='FROZEN'"));db.commit()
        with pytest.raises(service.ChatError):status(db,'alice',cid)
