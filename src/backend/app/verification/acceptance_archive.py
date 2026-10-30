"""Immutable, allowlisted long-term summaries under the authorized Change.

Raw command output, credentials, paths and screenshots are never copied here.
Online visual artifacts keep their independent seven-day access boundary.
"""
import hashlib
import json
import re
from sqlalchemy import insert, select, update
from app.chat.service import identity, ChatError
from app.governance.writer import project_lock, replace_file
from app.chat.relations import _read_file
from app.verification.acceptance_schema import archives,operations,attempts
from app.verification.acceptance_service import authorize
from app.verification.acceptance_state import AcceptanceState, Conflict


def canonical(value):
    return (json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()


def summary(row):
    checks=[]
    for check in row['checks']:
        evidence=json.loads(check['evidence_json'])
        safe={key:evidence[key] for key in ('kind','digest','deployment_digest') if key in evidence}
        if safe and (safe.get('kind') not in {'command','database','browser','product_turn'} or
                     not re.fullmatch('[a-f0-9]{64}',safe.get('digest',''))):
            raise Conflict('evidence_invalid')
        checks.append({'ac_id':check['ac_id'],'status':check['status'],
                       'input_digest':check['input_digest'],'evidence':safe,
                       'reason_code':check['reason_code'],'recorded_at':check['updated_at']})
    return {'schema_version':1,'category':'sanitized_acceptance_summary',
            'operation_id':row['id'],'attempt_id':row['attempt_id'],'change_id':row['change_id'],
            'input_digest':row['input_digest'],'template_digest':row['template_digest'],
            'status':row['status'],'cleanup_state':row['cleanup_state'],
            'visual_artifacts_included':False,'checks':sorted(checks,key=lambda check:check['ac_id'])}


def publish(factory, operation_id):
    state=AcceptanceState(factory);row=state.get(operation_id)
    if row['cancel_requested']:raise Conflict('cancelled')
    if row['status'] not in {'passed','failed','blocked'} or row['lease_until']:
        raise Conflict('evidence_not_settled')
    with factory() as db:
        _,project=authorize(db,row['actor_id'],operation_id,write=True)
    # Share the existing project writer lock; a second process cannot replace history.
    with project_lock(project):
        _read_file(project.root,f"openspec/changes/{row['change_id']}/trace.md")
        with factory.begin() as db:
            current,project=authorize(db,row['actor_id'],operation_id,write=True)
            if current['version']!=row['version'] or current['cancel_requested']:
                raise Conflict('version_conflict')
            stored=db.execute(select(archives).where(archives.c.attempt_id==row['attempt_id'])).mappings().first()
            if stored:
                record=dict(stored)
            else:
                payload=canonical(summary(row));digest=hashlib.sha256(payload).hexdigest()
                record={**identity(),'operation_id':operation_id,'attempt_id':row['attempt_id'],
                    'digest':digest,'relative_path':f"openspec/changes/{row['change_id']}/evidence/runtime/{row['attempt_id']}/summary.json",
                    'manifest_json':payload.decode(),'state':'pending'}
                db.execute(insert(archives).values(**record))
        if record['state']=='published':
            if hashlib.sha256(_read_file(project.root,record['relative_path']).encode()).hexdigest()!=record['digest']:
                raise Conflict('archive_integrity_failed')
            return {'artifact_id':record['id'],'digest':record['digest'],'path':record['relative_path']}
        # Recheck cancellation/authority immediately before the bounded file effect.
        with factory.begin() as db:
            current,project=authorize(db,row['actor_id'],operation_id,write=True)
            if current['attempt_id']!=row['attempt_id'] or current['input_digest']!=row['input_digest']:
                raise Conflict('input_changed')
            state._cas(db,current)  # Serialize stop against publication; no external process runs here.
            if current['cancel_requested']:raise Conflict('cancelled')
            payload=record['manifest_json'].encode()
            if hashlib.sha256(payload).hexdigest()!=record['digest']:raise Conflict('archive_integrity_failed')
            try:
                previous=_read_file(project.root,record['relative_path']).encode()
            except ChatError as error:
                if error.status!=503:raise
                previous=None
            if previous is not None and previous!=payload:raise Conflict('archive_integrity_failed')
            if previous is None:
                replace_file(project.root,record['relative_path'],None,payload,record['id'],create_parents=True)
            if _read_file(project.root,record['relative_path']).encode()!=payload:
                raise Conflict('archive_integrity_failed')
            db.execute(update(archives).where(archives.c.id==record['id']).values(state='published'))
        return {'artifact_id':record['id'],'digest':record['digest'],'path':record['relative_path']}


def read(db,factory,actor,operation_id):
    operation,project=authorize(db,actor,operation_id)
    records=db.execute(select(archives).where(archives.c.operation_id==operation_id,
        archives.c.state=='published').order_by(archives.c.created_at,archives.c.id)).mappings().all()
    items=[]
    for record in records:
        relative=record['relative_path']
        expected=f"openspec/changes/{operation['change_id']}/evidence/runtime/{record['attempt_id']}/summary.json"
        if relative!=expected:raise Conflict('archive_integrity_failed')
        try:
            try:payload=_read_file(project.root,relative).encode()
            except ChatError as error:
                if error.status!=503:raise
                from app.chat.relations import _entries
                matches=[entry for entry in _entries(project.root,operation['change_id'])
                    if entry['id']==operation['change_id'] and entry['status']=='archived']
                if len(matches)!=1:raise Conflict('archive_unavailable') from None
                relative=matches[0]['path']+f"/evidence/runtime/{record['attempt_id']}/summary.json"
                payload=_read_file(project.root,relative).encode()
        except (OSError,ValueError):raise Conflict('archive_unavailable') from None
        if hashlib.sha256(payload).hexdigest()!=record['digest']:raise Conflict('archive_integrity_failed')
        items.append({'artifact_id':record['id'],'digest':record['digest'],
                      'path':relative,'summary':json.loads(payload)})
    return {'operation_id':operation_id,'items':items}


def tick(factory,limit=10):
    cursor=getattr(factory,'_acceptance_archive_cursor','')
    with factory() as db:
        ids=list(db.scalars(select(operations.c.id).join(attempts,attempts.c.id==operations.c.attempt_id)
            .outerjoin(archives,archives.c.attempt_id==operations.c.attempt_id).where(
                operations.c.cancel_requested==0,operations.c.status.in_(['passed','failed','blocked']),
                attempts.c.worker_id.is_(None),
                (archives.c.id.is_(None)) | (archives.c.state=='pending'),operations.c.id>cursor)
            .order_by(operations.c.id).limit(limit)))
    factory._acceptance_archive_cursor=ids[-1] if len(ids)==limit else ''
    for oid in ids:
        try:publish(factory,oid)
        except (Conflict,ChatError,OSError,ValueError):continue
