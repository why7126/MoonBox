"""后台自动快照的最小 Task Trace；只存计数与固定阶段。"""

import json
import logging
from uuid import uuid4

from sqlalchemy import insert, select, update

from app.chat import service
from app.chat.schema import task_traces, task_trace_spans

STAGES = {'started', 'created', 'rotated', 'skipped', 'failed'}


def record(factory, operation_id, stage, *, expired=0, protected=0, error_code=None):
    if stage not in STAGES:
        return
    metadata = {'expired': expired, 'protected': protected}
    if error_code in {'snapshot_operation_failed', 'snapshot_inventory_failed'}:
        metadata['error_code'] = error_code
    try:
        with factory() as db:
            key = 'local-snapshot:' + operation_id
            row = db.execute(select(task_traces).where(task_traces.c.turn_id == key)).mappings().first()
            if row is None:
                trace_id = str(uuid4())
                db.execute(insert(task_traces).values(**service.identity(), task_trace_id=trace_id,
                    turn_id=key, parent_request_id=None, task_type='local_snapshot', task_name='chat.local_snapshot',
                    status=stage, metadata=json.dumps(metadata)))
            else:
                trace_id = row['task_trace_id']
                db.execute(update(task_traces).where(task_traces.c.id == row['id']).values(
                    status=stage, updated_at=service.now(),
                    finished_at=service.now() if stage in {'rotated', 'skipped', 'failed'} else None))
            db.execute(insert(task_trace_spans).values(**service.identity(), task_trace_id=trace_id,
                span_name='local_snapshot.' + stage, status=stage, metadata=json.dumps(metadata)))
            db.commit()
    except Exception:
        logging.getLogger('moonbox.chat').warning('local_snapshot.trace_unavailable')
