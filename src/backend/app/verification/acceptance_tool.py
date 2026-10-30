"""Fixed App Server tool: server-owned actor, turn, workspace and immutable checkpoint."""
import hashlib
import json
import re
from sqlalchemy import insert,select,update
from app.chat import service
from app.verification.acceptance_schema import tool_waits
from app.verification.acceptance_state import AcceptanceState,Conflict

SPEC={'type':'function','name':'moonbox_acceptance','description':
      'Run the current authorized Change acceptance in an isolated environment. Wait for the result; never send commands, paths or credentials.',
      'inputSchema':{'type':'object','properties':{},'additionalProperties':False}}


def begin(factory,token,workspace,call_id):
    from app.chat.execution import owned
    from app.moonbox_core.schema import delivery_sessions,execution_receipts
    from app.moonbox_core.sessions import execution_workspace
    from app.chat.snapshot_store import capture
    from app.moonbox_rollout import catalog
    from app.moonbox_worktree import Repository
    from app.moonbox_exec_server.scope import policy_id
    from app.verification.acceptance_service import create
    if not isinstance(call_id,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}',call_id):raise Conflict('tool_call_invalid')
    with factory() as db:
        turn,parent=owned(db,token)
        if turn['status']!='running':raise Conflict('source_execution_unconfirmed')
        from app.verification.acceptance_schema import deliveries
        if db.scalar(select(deliveries.c.id).where(deliveries.c.target_turn_id==turn['id'])):
            raise Conflict('resume_budget_exhausted')
        old=db.execute(select(tool_waits).where(tool_waits.c.source_turn_id==turn['id'])).mappings().first()
        if old:
            if old['call_id']!=call_id or old['generation']!=token['generation']:raise Conflict('tool_call_conflict')
            if not old['operation_id']:
                if not old['point_id'] or old['state']!='waiting':raise Conflict('tool_checkpoint_incomplete')
                linked=db.execute(select(delivery_sessions).where(delivery_sessions.c.conversation_id==parent['id'])).mappings().one()
                result=create(db,factory,parent['owner_id'],parent['id'],turn['id'],linked['change_id'],
                    'tool-'+hashlib.sha256(call_id.encode()).hexdigest(),source_point_id=old['point_id'])
                db.execute(update(tool_waits).where(tool_waits.c.id==old['id']).values(operation_id=result['id']))
                db.commit()
                return result['id']
            return old['operation_id']
        managed=execution_workspace(db,parent)
        linked=db.execute(select(delivery_sessions).where(delivery_sessions.c.conversation_id==parent['id'])).mappings().first()
        receipt=db.execute(select(execution_receipts).where(execution_receipts.c.turn_id==turn['id'])).mappings().first()
        if not managed or managed[1]!=workspace or not linked or not receipt:raise Conflict('source_workspace_unbound')
        allowed=json.loads(receipt['scope_json'] or '[]')
        if not allowed:raise Conflict('source_scope_not_isolated')
        db.execute(insert(tool_waits).values(**service.identity(),source_turn_id=turn['id'],call_id=call_id,
            generation=token['generation'],state='capturing'))
        db.commit()
    snapshot=capture(factory,parent['id'],turn['id'],workspace,'acceptance',
        fence=lambda db:owned(db,token),policy_roots=allowed)
    with factory() as db:
        owned(db,token)
        point=catalog.publish(db,managed[0]['id'],snapshot['version_id'],policy_version=policy_id(allowed),
            head_commit=Repository.open(workspace).head(),changed=True,scope=allowed)
        catalog.reference(db,managed[0]['id'],point['id'],'acceptance',turn['id'],'acceptance_evidence')
        db.execute(update(tool_waits).where(tool_waits.c.source_turn_id==turn['id']).values(point_id=point['id'],state='waiting'))
        db.commit()
        result=create(db,factory,parent['owner_id'],parent['id'],turn['id'],linked['change_id'],
            'tool-'+hashlib.sha256(call_id.encode()).hexdigest(),source_point_id=point['id'])
        db.execute(update(tool_waits).where(tool_waits.c.source_turn_id==turn['id']).values(operation_id=result['id']))
        db.commit()
        return result['id']


def poll(factory,token,server,request_id,operation_id):
    """Reserve the send once. A lost response remains unknown, never blindly replayed."""
    from app.chat.execution import owned
    from app.verification.acceptance_service import authorize,public
    state=AcceptanceState(factory);item=state.get(operation_id)
    if item['cancel_requested']:
        with factory() as db:
            turn,parent=owned(db,token)
            service.interrupt(db,parent['owner_id'],turn['id'])
        return False
    with factory.begin() as db:
        turn,parent=owned(db,token)
        wait=db.execute(select(tool_waits).where(tool_waits.c.source_turn_id==turn['id'],
            tool_waits.c.operation_id==operation_id)).mappings().one()
        if turn['status']=='stopping' and not item['cancel_requested']:
            db.rollback();state.cancel(operation_id,item['version']);return False
        if item['lease_until'] or item['status'] in {'queued','preparing','ready','running'}:return False
        current,_=authorize(db,parent['owner_id'],operation_id,write=True)
        if current['cancel_requested']:return False
        if current['version']!=item['version']:return False
        if wait['state']!='waiting':return False
        from app.verification.acceptance_delivery import validate_inputs
        validate_inputs(db,item)
        changed=db.execute(update(tool_waits).where(tool_waits.c.id==wait['id'],tool_waits.c.state=='waiting')
            .values(state='dispatching')).rowcount
        if not changed:return False
    # Persist the reservation before IPC: an uncertain send must never be replayed.
    with factory.begin() as db:
        turn,parent=owned(db,token)
        current,_=authorize(db,parent['owner_id'],operation_id,write=True)
        if current['cancel_requested'] or turn['status']!='running':return False
        if current['version']!=item['version']:raise Conflict('version_conflict')
        state._cas(db,current)
        # Stop serializes on the same operation row before this bounded pipe write.
        server.respond_tool(request_id,{'success':True,
            'contentItems':[{'type':'inputText','text':json.dumps(public(item),ensure_ascii=False)}]})
    return True


def acknowledge(factory,token,call_id):
    from app.chat.execution import owned
    with factory.begin() as db:
        owned(db,token)
        db.execute(update(tool_waits).where(tool_waits.c.source_turn_id==token['turn_id'],
            tool_waits.c.generation==token['generation'],tool_waits.c.call_id==call_id,
            tool_waits.c.state=='dispatching').values(state='delivered'))
