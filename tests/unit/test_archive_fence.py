"""Shared archive fence and additive operation table on SQLite and MySQL."""
from datetime import datetime,timedelta,timezone
from sqlalchemy import select
import pytest
from test_replacement_authorization import context
from app.chat.schema import governance_project_locks as locks
from app.governance.archive_coordinator import acquire,assert_fence,checkpoint
from app.governance.replacement_schema import archive_operations


def test_ordinary_fence_persists_blocks_other_operation_and_releases(context):
    db,project,*_=context;locks.create(db.get_bind(),checkfirst=True)
    fence=acquire(db,project,'owner','sample','ordinary',{'expected':'a'*64},None)
    assert assert_fence(db,project,'ordinary',fence)['stage']=='claimed'
    with pytest.raises(ValueError,match='project_archive_busy'):
        acquire(db,project,'owner','other','another',{},None)
    db.rollback()
    with pytest.raises(ValueError,match='stale_archive_executor'):
        assert_fence(db,project,'ordinary',fence,now=datetime.now(timezone.utc)+timedelta(minutes=6))
    row=db.execute(select(archive_operations)).mappings().one()
    next_fence=acquire(db,project,'owner','sample','ordinary',{'expected':'a'*64},row)
    assert next_fence>fence
    with pytest.raises(ValueError):assert_fence(db,project,'ordinary',fence)
    for stage in ('merge_verified','move_verified','synced','completed'):
        checkpoint(db,project,'ordinary',next_fence,stage)
    assert db.scalar(select(locks.c.operation_id)) is None
