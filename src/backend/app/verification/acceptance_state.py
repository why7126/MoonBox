"""Transactional acceptance state. No network or model side effects inside transactions."""
import hashlib
import json
import re
import time
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from app.chat.service import identity, now
from app.verification.acceptance_schema import operations, attempts, results, steps

class Conflict(ValueError):
    """Stable, non-secret refusal reason."""


def online(check):
    stamp=datetime.fromisoformat(check['updated_at'].replace('Z','+00:00'))
    if stamp.tzinfo is None:stamp=stamp.replace(tzinfo=timezone.utc)
    return timedelta(0)<=datetime.now(timezone.utc)-stamp<=timedelta(days=7)


def dependencies(check):
    if 'dependencies' in check and 'depends_on' in check and check['dependencies'] != check['depends_on']:
        raise Conflict('plan_invalid')
    return check.get('depends_on',check.get('dependencies',[]))


def validate_plan(plan):
    checks=plan.get('checks') if isinstance(plan,dict) else None
    if not isinstance(checks,list) or not 1<=len(checks)<=200:
        raise Conflict('plan_invalid')
    ids=[x.get('id') for x in checks if isinstance(x,dict)]
    if len(ids)!=len(checks) or any(not isinstance(x,str) or not x.startswith('AC-') or len(x)>64 for x in ids) or len(set(ids))!=len(ids):
        raise Conflict('plan_invalid')
    graph={x['id']:dependencies(x) for x in checks}
    for x in checks:
        if not isinstance(x.get('inputs'),list) or not x['inputs'] or any(not isinstance(p,str) for p in x['inputs']):
            raise Conflict('plan_invalid')
        if not isinstance(graph[x['id']],list) or any(not isinstance(d,str) or d not in graph for d in graph[x['id']]):
            raise Conflict('plan_invalid')
    pending=set(ids);done=set()
    while pending:
        ready={i for i in pending if set(graph[i])<=done}
        if not ready:raise Conflict('plan_invalid')
        done.update(ready);pending-=ready
    return checks


class AcceptanceState:
    def __init__(self,factory,clock=time.time):
        self.factory,self.clock=factory,clock

    def create(self,*,actor,space,repository,conversation,turn,change,request_key,binding,input_digest,plan,source_ref=None,request_id=None):
        checks=validate_plan(plan)
        request_hash=hashlib.sha256(request_key.encode()).hexdigest()
        condition=(operations.c.actor_id==actor,operations.c.space_id==space,
            operations.c.repository_id==repository,operations.c.source_turn_id==turn,
            operations.c.request_hash==request_hash)
        def previous(db):
            row=db.execute(select(operations).where(*condition)).mappings().first()
            if row and (row['input_digest']!=input_digest or row['binding_revision']!=binding or
                        row['change_id']!=change or json.loads(row['plan_json'])!=plan or
                        json.loads(row['source_ref_json']) != (source_ref or {})):
                raise Conflict('input_conflict')
            return row
        with self.factory() as db:
            old=previous(db)
            if old:return self.get(old['id'])
        attempt_id=str(uuid4())
        row=dict(**identity(),actor_id=actor,space_id=space,repository_id=repository,
            conversation_id=conversation,source_turn_id=turn,change_id=change,request_hash=request_hash,
            binding_revision=binding,input_digest=input_digest,plan_json=json.dumps(plan,sort_keys=True),
            source_ref_json=json.dumps(source_ref or {},sort_keys=True),
            status='queued',version=1,cancel_requested=0,resume_count=0,attempt_id=attempt_id,
            queued_at=int(self.clock()),expires_at=None,checks_deadline=None,cleanup_state='not_created',reason_code=None)
        try:
            with self.factory.begin() as db:
                db.execute(insert(operations).values(**row))
                db.execute(insert(attempts).values(**{**identity(),'id':attempt_id},operation_id=row['id'],
                    sequence=1,epoch=0,worker_id=None,lease_until=0,input_digest=input_digest,state='queued'))
                for check in checks:
                    db.execute(insert(results).values(**identity(),attempt_id=attempt_id,ac_id=check['id'],
                        input_digest=input_digest,status='pending',evidence_json='{}'))
                from app.verification.acceptance_observability import transition
                transition(db,row,'queued',request_id)
        except IntegrityError:
            with self.factory() as db:
                old=previous(db)
                if not old:raise Conflict('request_conflict')
                return self.get(old['id'])
        return self.get(row['id'])

    def _row(self,db,oid):
        row=db.execute(select(operations).where(operations.c.id==oid)).mappings().first()
        if not row:raise Conflict('operation_not_found')
        return dict(row)

    def get(self,oid):
        with self.factory() as db:
            row=self._row(db,oid)
            row['checks']=[dict(x) for x in db.execute(select(results).where(results.c.attempt_id==row['attempt_id'])).mappings()]
            attempt=dict(db.execute(select(attempts).where(attempts.c.id==row['attempt_id'])).mappings().one())
            row['epoch']=attempt['epoch'];row['lease_until']=attempt['lease_until']
            row['template_digest']=attempt['template_digest']
            row['ready']=row['status']=='passed' and not row['cancel_requested'] and row['cleanup_state']=='released' and bool(row['checks']) and all(
                c['status']=='passed' and c['input_digest']==row['input_digest'] and
                bool(json.loads(c['evidence_json'])) and online(c) for c in row['checks'])
            return row

    def _cas(self,db,row,**values):
        changed=db.execute(update(operations).where(operations.c.id==row['id'],operations.c.version==row['version']).values(
            **values,version=row['version']+1,updated_at=now())).rowcount
        if changed!=1:raise Conflict('version_conflict')
        if 'status' in values or 'cleanup_state' in values:
            from app.verification.acceptance_observability import transition
            transition(db,{**row,**values},values.get('status',row['status']))

    def claim(self,oid,worker):
        timestamp=int(self.clock())
        with self.factory.begin() as db:
            row=self._row(db,oid)
            attempt=dict(db.execute(select(attempts).where(attempts.c.id==row['attempt_id'])).mappings().one())
            if row['cancel_requested']:raise Conflict('cancelled')
            if attempt['worker_id']:
                raise Conflict('execution_busy' if attempt['lease_until']>timestamp else 'termination_unconfirmed')
            if row['status'] not in {'queued','blocked'}:raise Conflict('state_conflict')
            if row['expires_at'] and row['expires_at']<=timestamp:raise Conflict('environment_expired')
            if not row['expires_at'] and timestamp-row['queued_at']>=1800:raise Conflict('queue_expired')
            expires=row['expires_at'] or timestamp+7200
            self._cas(db,row,status='preparing',expires_at=expires)
            db.execute(update(attempts).where(attempts.c.id==row['attempt_id']).values(
                epoch=attempt['epoch']+1,worker_id=worker,lease_until=min(timestamp+300,expires),
                expires_at=expires,state='preparing'))
        return self.get(oid)

    def _fenced(self,db,token):
        row=self._row(db,token['id'])
        attempt=db.execute(select(attempts).where(attempts.c.id==row['attempt_id'])).mappings().one()
        if row['cancel_requested']:raise Conflict('cancelled')
        if attempt['epoch']!=token['epoch'] or row['attempt_id']!=token['attempt_id']:raise Conflict('epoch_conflict')
        if attempt['lease_until']<=self.clock() or not attempt['worker_id']:raise Conflict('lease_expired')
        return row,attempt

    def heartbeat(self,token):
        with self.factory.begin() as db:
            row,attempt=self._fenced(db,token)
            self._cas(db,row)
            db.execute(update(attempts).where(attempts.c.id==attempt['id']).values(lease_until=min(int(self.clock())+300,row['expires_at'])))

    def advance(self,token,state):
        transitions={'preparing':{'ready','blocked','failed'},'ready':{'running','blocked'},
                     'running':{'blocked','passed','failed'},'blocked':{'preparing','running'}}
        with self.factory.begin() as db:
            row,attempt=self._fenced(db,token)
            if state not in transitions.get(row['status'],set()):raise Conflict('state_conflict')
            values={'status':state}
            if state=='running':
                values['checks_deadline']=row['checks_deadline'] or min(int(self.clock())+3600,row['expires_at'])
                if values['checks_deadline']<=self.clock():raise Conflict('acceptance_budget_expired')
            self._cas(db,row,**values)
            db.execute(update(attempts).where(attempts.c.id==attempt['id']).values(state=state))
        return self.get(token['id'])

    def cancel(self,oid,expected_version):
        with self.factory.begin() as db:
            row=self._row(db,oid)
            if row['cancel_requested']:return self.get(oid)
            if row['version']!=expected_version:raise Conflict('version_conflict')
            self._cas(db,row,cancel_requested=1,status='cancelled',reason_code='user_stopped')
            db.execute(update(attempts).where(attempts.c.id==row['attempt_id']).values(epoch=attempts.c.epoch+1,state='cancelled'))
        return self.get(oid)

    def recover(self,oid,epoch,*,terminated):
        with self.factory.begin() as db:
            row=self._row(db,oid)
            attempt=db.execute(select(attempts).where(attempts.c.id==row['attempt_id'])).mappings().one()
            if not terminated:raise Conflict('termination_unconfirmed')
            if attempt['epoch']!=epoch:raise Conflict('epoch_conflict')
            self._cas(db,row,status='cancelled' if row['cancel_requested'] else 'blocked',reason_code='worker_interrupted')
            db.execute(update(attempts).where(attempts.c.id==attempt['id']).values(epoch=epoch+1,worker_id=None,lease_until=0,state='blocked'))
        return self.get(oid)

    def resume(self,oid,expected_version):
        with self.factory.begin() as db:
            row=self._row(db,oid)
            if row['cancel_requested']:raise Conflict('cancelled')
            if row['version']!=expected_version:raise Conflict('version_conflict')
            a=db.execute(select(attempts).where(attempts.c.id==row['attempt_id'])).mappings().one()
            if a['worker_id']:raise Conflict('termination_unconfirmed')
            if row['status']!='blocked':raise Conflict('state_conflict')
            if row['expires_at'] and row['expires_at']<=self.clock():raise Conflict('environment_expired')
            if row['checks_deadline'] and row['checks_deadline']<=self.clock():raise Conflict('acceptance_budget_expired')
            if row['cleanup_state'] not in {'released','not_created'}:raise Conflict('cleanup_required')
            next_id=str(uuid4())
            self._cas(db,row,status='queued',reason_code=None,attempt_id=next_id,cleanup_state='not_created')
            db.execute(insert(attempts).values(**{**identity(),'id':next_id},operation_id=oid,
                sequence=a['sequence']+1,epoch=0,worker_id=None,lease_until=0,input_digest=row['input_digest'],
                state='queued',expires_at=row['expires_at'],template_digest=a['template_digest']))
            for previous in db.execute(select(results).where(results.c.attempt_id==row['attempt_id'])).mappings():
                retained=previous['status']=='passed'
                record={**identity(),'updated_at':previous['updated_at'] if retained else now()}
                db.execute(insert(results).values(**record,attempt_id=next_id,ac_id=previous['ac_id'],
                    input_digest=row['input_digest'],status='passed' if retained else 'pending',
                    evidence_json=previous['evidence_json'] if retained else '{}',reason_code=None))
        return self.get(oid)

    def bind_template(self, token, digest):
        """Retained ACs are valid only for the same approved deployment template."""
        if not re.fullmatch(r'[a-f0-9]{64}',digest):raise Conflict('template_digest_invalid')
        mismatch=False
        with self.factory.begin() as db:
            row,attempt=self._fenced(db,token)
            mismatch=bool(attempt['template_digest'] and attempt['template_digest']!=digest)
            if mismatch:
                self._cas(db,row,status='blocked',reason_code='template_changed')
                db.execute(update(results).where(results.c.attempt_id==attempt['id']).values(
                    status='stale',reason_code='template_changed'))
                db.execute(update(attempts).where(attempts.c.id==attempt['id']).values(
                    epoch=attempt['epoch']+1,state='blocked'))
            elif not attempt['template_digest']:
                self._cas(db,row)
                db.execute(update(attempts).where(attempts.c.id==attempt['id']).values(template_digest=digest))
        if mismatch:raise Conflict('template_changed')

    def result(self,token,ac,status,*,evidence,reason=None):
        if status not in {'passed','failed','blocked'}:raise Conflict('result_invalid')
        if not isinstance(evidence,dict):raise Conflict('evidence_invalid')
        if reason is not None and not re.fullmatch(r'[a-z][a-z0-9_]{0,79}',reason):
            raise Conflict('reason_invalid')
        if status=='passed' and (evidence.get('kind') not in {'command','database','browser','product_turn'} or not evidence.get('digest')):
            raise Conflict('evidence_missing')
        # Only non-secret references may cross into persisted result metadata.
        safe={k:v for k,v in evidence.items() if k in {'kind','digest','artifact_id','environment_id','deployment_digest'}}
        if any(not isinstance(v,str) or len(v)>128 for v in safe.values()):raise Conflict('evidence_invalid')
        if any(k in safe and not re.fullmatch(r'[a-f0-9]{64}',safe[k]) for k in ('digest','deployment_digest')):
            raise Conflict('evidence_invalid')
        with self.factory.begin() as db:
            row,_=self._fenced(db,token)
            check=next((c for c in json.loads(row['plan_json'])['checks'] if c['id']==ac),None)
            if check is None:raise Conflict('ac_unknown')
            states=dict(db.execute(select(results.c.ac_id,results.c.status).where(results.c.attempt_id==row['attempt_id'])).all())
            if any(states.get(dep)!='passed' for dep in dependencies(check)):raise Conflict('dependency_not_ready')
            self._cas(db,row)
            previous=db.execute(select(results).where(results.c.attempt_id==row['attempt_id'],results.c.ac_id==ac)).mappings().first()
            if previous and previous['status'] not in {'pending'}:
                db.execute(insert(steps).values(**identity(),attempt_id=row['attempt_id'],
                    step_key='result-history:'+uuid4().hex,epoch=token['epoch'],status='complete',
                    facts_json=json.dumps({'ac_id':ac,'input_digest':previous['input_digest'],
                        'status':previous['status'],'evidence':json.loads(previous['evidence_json']),
                        'reason_code':previous['reason_code']})))
            changed=db.execute(update(results).where(results.c.attempt_id==row['attempt_id'],results.c.ac_id==ac).values(
                status=status,evidence_json=json.dumps(safe),reason_code=reason,updated_at=now())).rowcount
            if changed!=1:raise Conflict('ac_unknown')

    def runnable(self,oid):
        row=self.get(oid)
        if row['cancel_requested']:return []
        states={c['ac_id']:c['status'] for c in row['checks']}
        return [c['id'] for c in json.loads(row['plan_json'])['checks']
            if states[c['id']] in {'pending','stale'} and all(states[d]=='passed' for d in dependencies(c))]

    def invalidate(self,oid,paths):
        row=self.get(oid);checks=json.loads(row['plan_json'])['checks']
        affected={c['id'] for c in checks if set(c['inputs']) & set(paths)}
        while True:
            expanded=affected|{c['id'] for c in checks if set(dependencies(c)) & affected}
            if expanded==affected:break
            affected=expanded
        with self.factory.begin() as db:
            current=self._row(db,oid)
            if current['version']!=row['version']:raise Conflict('version_conflict')
            self._cas(db,current,status='blocked',reason_code='input_changed')
            db.execute(update(attempts).where(attempts.c.id==row['attempt_id']).values(epoch=attempts.c.epoch+1,state='blocked'))
            db.execute(update(results).where(results.c.attempt_id==row['attempt_id'],results.c.ac_id.in_(affected)).values(status='stale',reason_code='input_changed'))
        return sorted(affected)

    def cleanup(self,oid,*,released):
        with self.factory.begin() as db:
            row=self._row(db,oid)
            self._cas(db,row,cleanup_state='released' if released else 'cleanup_failed')
        return self.get(oid)

    def request_cleanup(self,oid,expected_version):
        with self.factory.begin() as db:
            row=self._row(db,oid)
            if row['cleanup_state']=='releasing':return self.get(oid)
            if row['version']!=expected_version:raise Conflict('version_conflict')
            if row['cleanup_state']!='cleanup_failed':raise Conflict('cleanup_not_retryable')
            attempt=db.execute(select(attempts).where(attempts.c.id==row['attempt_id'])).mappings().one()
            if attempt['worker_id']:raise Conflict('termination_unconfirmed')
            self._cas(db,row,cleanup_state='releasing')
            db.execute(update(steps).where(steps.c.attempt_id==row['attempt_id'],steps.c.step_key=='cleanup-policy').values(
                status='pending',facts_json=json.dumps({'count':0,'next_at':int(self.clock())})))
            db.execute(insert(steps).values(**identity(),attempt_id=row['attempt_id'],
                step_key='cleanup-request:'+str(row['version']),epoch=attempt['epoch'],
                status='pending',facts_json='{}'))
        return self.get(oid)

    def deliver(self,token,delivery_id,*,terminated,authorized=False):
        key='delivery:'+hashlib.sha256(delivery_id.encode()).hexdigest()
        with self.factory.begin() as db:
            row,attempt=self._fenced(db,token)
            old=db.execute(select(steps).where(steps.c.attempt_id==attempt['id'],steps.c.step_key==key)).mappings().first()
            if old:return 'already_delivered' if old['status']=='complete' else 'delivery_pending'
            if terminated:
                if not authorized:raise Conflict('resume_not_authorized')
                if row['resume_count']>=1:raise Conflict('resume_budget_exhausted')
                self._cas(db,row,resume_count=row['resume_count']+1)
            else:self._cas(db,row)
            db.execute(insert(steps).values(**identity(),attempt_id=attempt['id'],step_key=key,
                epoch=attempt['epoch'],status='pending',facts_json=json.dumps({'mode':'resume' if terminated else 'deliver'})))
        return 'resume' if terminated else 'deliver'

    def acknowledge_delivery(self, token, delivery_id):
        """Only a receiver acknowledgement completes a reserved delivery."""
        key='delivery:'+hashlib.sha256(delivery_id.encode()).hexdigest()
        with self.factory.begin() as db:
            row,attempt=self._fenced(db,token)
            old=db.execute(select(steps).where(steps.c.attempt_id==attempt['id'],steps.c.step_key==key)).mappings().first()
            if not old:raise Conflict('delivery_not_reserved')
            if old['status']=='complete':return
            self._cas(db,row)
            db.execute(update(steps).where(steps.c.id==old['id']).values(status='complete',updated_at=now()))
