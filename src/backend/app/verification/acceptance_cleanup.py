"""Three bounded cleanup attempts; restart retains count and scheduled retry time."""
import json
from sqlalchemy import insert, select, update
from app.chat.service import identity
from app.verification.acceptance_schema import steps


def record(state,operation_id,clean):
    with state.factory.begin() as db:
        row=state._row(db,operation_id)
        old=db.execute(select(steps).where(steps.c.attempt_id==row['attempt_id'],steps.c.step_key=='cleanup-policy')).mappings().first()
        previous=json.loads(old['facts_json']) if old else {'count':0}
        count=previous['count']+1
        next_at=None if clean or count>=3 else int(state.clock())+(30 if count==1 else 120)
        values={'status':'complete' if clean else 'pending' if next_at else 'failed',
                'facts_json':json.dumps({'count':count,'next_at':next_at})}
        state._cas(db,row,cleanup_state='released' if clean else 'cleanup_failed')
        if old:db.execute(update(steps).where(steps.c.id==old['id']).values(**values))
        else:db.execute(insert(steps).values(**identity(),attempt_id=row['attempt_id'],step_key='cleanup-policy',epoch=0,**values))


def due(state,item):
    if item['cleanup_state']=='releasing':return True
    with state.factory() as db:
        raw=db.scalar(select(steps.c.facts_json).where(steps.c.attempt_id==item['attempt_id'],steps.c.step_key=='cleanup-policy'))
    if not raw:return False
    data=json.loads(raw)
    return data['count']<3 and data['next_at'] is not None and data['next_at']<=state.clock()
