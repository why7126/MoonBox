"""Run in the separately mounted trusted writer service, without model credentials."""
import logging
import time
from sqlalchemy import select
from app.chat.schema import governance_applications
from app.chat.service import ChatError
from app.db.session import get_session_factory
from app.governance.writer import process
from app.governance import store

logger=logging.getLogger('moonbox.governance')


def tick(factory):
    with factory() as db:
        rows=db.execute(select(governance_applications.c.id).where(
            governance_applications.c.state.in_(('pending','applying','recovering')))
            .order_by(governance_applications.c.created_at,governance_applications.c.id)).all()
    for row in rows:
        try:
            with factory() as db:process(db,row.id)
        except BlockingIOError: continue
        except (OSError,ChatError):
            logger.warning('governance.controller.operation_unavailable',extra={'operation_id':row.id})


def main():
    store.root();factory=get_session_factory()
    while True:
        from app.governance.readiness import publish
        publish();tick(factory);time.sleep(.25)


if __name__=='__main__':main()
