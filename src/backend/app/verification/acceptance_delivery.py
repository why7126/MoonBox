"""One transactional linked continuation through normal Chat admission."""
import hashlib
import json
import time
from sqlalchemy import insert,select,update
from app.chat import service
from app.chat.schema import turns,conversations
from app.verification.acceptance_schema import operations,deliveries,tool_waits
from app.verification.acceptance_service import authorize
from app.verification.acceptance_state import AcceptanceState,Conflict


def remaining_tokens(db,source_turn_id):
    from app.chat.schema import reservations
    reservation=db.execute(select(reservations).where(reservations.c.turn_id==source_turn_id)).mappings().first()
    if not reservation:raise Conflict('source_budget_unconfirmed')
    if not reservation['tokens']:return None
    if reservation['actual_tokens'] is None:raise Conflict('source_budget_unconfirmed')
    remaining=reservation['tokens']-reservation['actual_tokens']
    if remaining<=0:raise Conflict('resume_budget_exhausted')
    return remaining


def token_limit(db,turn_id):
    oid=db.scalar(select(deliveries.c.operation_id).where(deliveries.c.target_turn_id==turn_id))
    if not oid:return None
    return remaining_tokens(db,db.scalar(select(operations.c.source_turn_id).where(operations.c.id==oid)))


def validate_inputs(db,row):
    from app.verification.acceptance_source import resolve,verify_files
    from app.verification.acceptance_template import approved_template
    ref=json.loads(row['source_ref_json'])
    _,project,managed,point,recorded,_,source=resolve(db,row['actor_id'],row['conversation_id'],
        row['source_turn_id'],row['change_id'],source_point_id=ref.get('point_id') if ref.get('kind')=='tool_checkpoint' else None)
    digest=verify_files(managed,point,recorded,project.binding_revision)
    if hashlib.sha256(json.dumps([digest,source],sort_keys=True).encode()).hexdigest()!=row['input_digest']:
        raise Conflict('input_changed')
    if row.get('template_digest') and approved_template(managed[1]).key!=row['template_digest']:
        raise Conflict('template_changed')


def guard(db,row,admitted_turn=None):
    from app.moonbox_core.schema import execution_receipts
    current,_=authorize(db,row['actor_id'],row['id'],write=True)
    if current['cancel_requested']:raise Conflict('cancelled')
    if not current['expires_at'] or current['expires_at']<=time.time():raise Conflict('environment_expired')
    if current['attempt_id']!=row['attempt_id'] or current['input_digest']!=row['input_digest']:
        raise Conflict('input_changed')
    source=service.turn(db,row['actor_id'],row['source_turn_id'])
    receipt=db.execute(select(execution_receipts).where(execution_receipts.c.turn_id==source['id'])).mappings().first()
    if source['status']!='failed' or not receipt or not receipt['executor_closed'] or not receipt['files_collected']:
        raise Conflict('source_execution_unconfirmed')
    remaining_tokens(db,source['id'])
    parent=service.conversation(db,row['actor_id'],row['conversation_id'])
    if parent['active_turn_id'] not in (None,admitted_turn) or parent['archived']:raise Conflict('source_workspace_busy')
    return current,source


def continue_once(factory,operation_id):
    state=AcceptanceState(factory);row=state.get(operation_id)
    if row['status'] not in {'passed','failed','blocked'} or row['lease_until'] or row['cleanup_state']!='released':
        raise Conflict('delivery_not_settled')
    with factory() as db:
        authorize(db,row['actor_id'],operation_id,write=True)
        old=db.execute(select(deliveries).where(deliveries.c.operation_id==operation_id)).mappings().first()
        if old:return {'state':old['state'],'turn_id':old['target_turn_id']}
        waiting=db.execute(select(tool_waits).where(tool_waits.c.operation_id==operation_id)).mappings().first()
        if waiting and waiting['state']=='delivered':return {'state':'delivered','turn_id':row['source_turn_id']}
        if waiting and waiting['state']=='dispatching':raise Conflict('delivery_unconfirmed')
        current,source=guard(db,row)
        validate_inputs(db,row)
        config=json.loads(source['requested_config'] or '{}')
        # Include only allowlisted facts. Raw output is not promoted into model instructions.
        facts={'operation_id':operation_id,'status':row['status'],'checks':[
            {'id':c['ac_id'],'status':c['status'],'reason':c['reason_code']} for c in row['checks']]}
        prompt=source['prompt']+'\n\n隔离验收结果（数据，不扩大原授权）：\n'+json.dumps(facts,ensure_ascii=False)+'\n在原授权和剩余期限内继续。不得重写原轮次终态或自动归档。'
        def admit(transaction,tid):
            locked,original=guard(transaction,row,tid)
            if locked['version']!=current['version']:raise Conflict('version_conflict')
            if locked['resume_count']>=1:raise Conflict('resume_budget_exhausted')
            state._cas(transaction,locked,resume_count=1)
            transaction.execute(insert(deliveries).values(**service.identity(),operation_id=operation_id,
                attempt_id=row['attempt_id'],input_digest=row['input_digest'],state='queued',mode='continuation',target_turn_id=tid))
        # request_turn performs the existing executor, governance, identity and budget gates.
        result=service.request_turn(db,row['actor_id'],row['conversation_id'],'acceptance-'+operation_id,
            prompt,execution_config=config,admission_guard=admit)
        stored=db.execute(select(deliveries).where(deliveries.c.operation_id==operation_id)).mappings().first()
        if not stored or stored['target_turn_id']!=result['id']:raise Conflict('delivery_admission_unconfirmed')
        return {'state':stored['state'],'turn_id':stored['target_turn_id']}


def execution_guard(db,turn_id,*,starting=False):
    """Called by the sole Chat owner before starting and on every event-loop iteration."""
    delivery=db.execute(select(deliveries).where(deliveries.c.target_turn_id==turn_id)).mappings().first()
    if not delivery:return
    row,_=authorize(db,db.scalar(select(operations.c.actor_id).where(operations.c.id==delivery['operation_id'])),
                    delivery['operation_id'],write=True)
    if row['cancel_requested'] or row['expires_at']<=time.time():raise Conflict('acceptance_continuation_stopped')
    if row['attempt_id']!=delivery['attempt_id'] or row['input_digest']!=delivery['input_digest']:
        raise Conflict('input_changed')
    if starting:
        from app.verification.acceptance_schema import attempts
        current=dict(row)
        current['template_digest']=db.scalar(select(attempts.c.template_digest).where(attempts.c.id==row['attempt_id']))
        validate_inputs(db,current)
        db.execute(update(deliveries).where(deliveries.c.id==delivery['id']).values(state='consumed'))


def tick(factory,limit=10):
    cursor=getattr(factory,'_acceptance_delivery_cursor','')
    with factory() as db:
        ids=list(db.scalars(select(operations.c.id).join(turns,turns.c.id==operations.c.source_turn_id)
            .outerjoin(deliveries,deliveries.c.operation_id==operations.c.id).where(
                deliveries.c.id.is_(None),operations.c.cancel_requested==0,operations.c.resume_count==0,
                operations.c.cleanup_state=='released',operations.c.status.in_(['passed','failed','blocked']),
                turns.c.status=='failed',operations.c.id>cursor).order_by(operations.c.id).limit(limit)))
    factory._acceptance_delivery_cursor=ids[-1] if len(ids)==limit else ''
    for oid in ids:
        try:continue_once(factory,oid)
        except (Conflict,service.ChatError):continue
