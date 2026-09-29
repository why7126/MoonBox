"""Organization runs on the model worker, separate from the formal file writer."""
import logging
import time
from sqlalchemy import select,update
from app.governance.capture_schema import organize_tasks
from app.governance.capture_organizer import run
from app.governance.capture_executor import execute
from app.chat.service import now


_last_cleanup=0.0

def tick(factory):
    global _last_cleanup
    if time.monotonic()-_last_cleanup>60:
        _last_cleanup=time.monotonic()
        try:
            from app.governance.capture_cleanup import cleanup
            from app.core.object_storage import get_object_storage
            with factory() as db:cleanup(db,get_object_storage())
        except Exception:logging.getLogger("moonbox.capture").warning("capture.cleanup_unavailable")
    with factory() as db:
        tid=db.scalar(select(organize_tasks.c.id).where(organize_tasks.c.state=='pending')
            .order_by(organize_tasks.c.created_at,organize_tasks.c.id).limit(1))
    if tid:
        try:run(factory,tid,execute)
        except Exception:
            logging.getLogger('moonbox.capture').warning('capture.organization_unavailable')
            with factory() as db:
                db.execute(update(organize_tasks).where(organize_tasks.c.id==tid)
                    .values(state='failed',error_code='organization_unavailable',updated_at=now()))
                db.commit()


def recover_interrupted(factory):
    with factory() as db:
        db.execute(update(organize_tasks).where(organize_tasks.c.state=='running')
            .values(state='failed',error_code='worker_interrupted',updated_at=now()))
        db.commit()
