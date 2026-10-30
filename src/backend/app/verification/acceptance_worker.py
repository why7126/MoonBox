"""Single-daemon acceptance dispatch/reconciliation under per-operation process locks."""
import json
import hashlib
import os
from pathlib import Path
from types import SimpleNamespace
from sqlalchemy import select, update, or_, and_
from app.verification.acceptance_schema import operations, attempts, identities
from app.verification.acceptance_state import AcceptanceState, Conflict
from app.verification.acceptance_service import authorize
from app.verification.acceptance_template import approved_template
from app.verification.acceptance_controller import Controller
from app.verification.acceptance_runtime import DockerRuntime
from app.verification.acceptance_resources import release
from app.verification.candidate import locked, DockerEnvironment, CandidateError
from app.chat.workspace import trusted_directory,WorkspaceError


def root_directory():
    value=os.getenv('MOONBOX_ACCEPTANCE_ROOT')
    if not value or not Path(value).is_absolute():raise Conflict('acceptance_storage_unconfigured')
    root=Path(value)
    try:
        root.mkdir(mode=0o700,parents=True,exist_ok=True)
        trusted_directory(root)
    except (OSError,WorkspaceError):raise Conflict('acceptance_storage_untrusted') from None
    if root.stat().st_mode&0o022:raise Conflict('acceptance_storage_untrusted')
    return root


def run_one(factory, operation_id, worker_id):
    state=AcceptanceState(factory)
    try:
        root=root_directory()
        template=approved_template()
    except (Conflict,OSError) as error:
        with factory.begin() as db:
            row=state._row(db,operation_id)
            if row['status']=='queued' and not row['cancel_requested']:
                state._cas(db,row,status='blocked',reason_code=str(error) if isinstance(error,Conflict) else 'acceptance_template_unavailable')
        return state.get(operation_id)
    def allowed(oid):
        item=state.get(oid)
        if item.get('template_digest') and approved_template().key!=item['template_digest']:
            paths={path for check in json.loads(item['plan_json'])['checks'] for path in check['inputs']}
            state.invalidate(oid,paths)
            raise Conflict('template_changed')
        with factory() as db:
            _,project=authorize(db,item['actor_id'],oid,write=True)
            from app.verification.acceptance_source import resolve,verify_files
            try:
                ref=json.loads(item['source_ref_json'])
                _,_,managed,point,recorded,_,source=resolve(db,item['actor_id'],item['conversation_id'],item['source_turn_id'],item['change_id'],
                    source_point_id=ref.get('point_id') if ref.get('kind')=='tool_checkpoint' else None)
                digest=verify_files(managed,point,recorded,project.binding_revision)
                current=hashlib.sha256(json.dumps([digest,source],sort_keys=True).encode()).hexdigest()
                if current!=item['input_digest']:raise Conflict('input_changed')
            except Conflict:
                db.rollback()
                paths={path for check in json.loads(item['plan_json'])['checks'] for path in check['inputs']}
                state.invalidate(oid,paths)
                raise Conflict('input_changed') from None
    with locked(root,'operation-'+operation_id,True):
        try:
            allowed(operation_id)
            from app.moonbox_core.schema import workspaces
            source=json.loads(state.get(operation_id)['source_ref_json'])
            with factory() as db:
                source_root=db.scalar(select(workspaces.c.root_locator).where(workspaces.c.id==source.get('workspace_id')))
            if not source_root:raise Conflict('source_workspace_unbound')
            template=approved_template(source_root)
            if root.resolve().is_relative_to(Path(source_root).resolve()):
                raise Conflict('acceptance_storage_untrusted')
        except Exception as error:
            with factory.begin() as db:
                row=state._row(db,operation_id)
                if row['status']=='queued' and not row['cancel_requested']:
                    state._cas(db,row,status='blocked',reason_code=str(error) if isinstance(error,Conflict) else 'source_authorization_changed')
            return state.get(operation_id)
        try:
            runtime=DockerRuntime(state,template,root)
            return Controller(state,runtime,allowed).run(operation_id,worker_id)
        except Conflict as error:
            with factory.begin() as db:
                row=state._row(db,operation_id)
                if row['status']=='queued' and not row['cancel_requested']:
                    state._cas(db,row,status='blocked',reason_code=str(error))
            return state.get(operation_id)


def reconcile(factory, limit=10):
    """Acquire controller lock, prove owned resources gone, then release a stale lease."""
    state=AcceptanceState(factory)
    try:root=root_directory()
    except Conflict:return 0
    with factory() as db:
        rows=list(db.execute(select(operations).join(attempts,attempts.c.id==operations.c.attempt_id).where(or_(
            operations.c.cleanup_state.in_(['releasing','cleanup_failed']),
            and_(operations.c.status.in_(['preparing','ready','running','cancelled','blocked','passed','failed']),
                 attempts.c.worker_id.is_not(None),attempts.c.lease_until<=state.clock())),
        ).order_by(operations.c.updated_at)).mappings())
    count=0
    visited=0
    for row in rows:
        try:
            with locked(root,'operation-'+row['id'],True):
                item=state.get(row['id'])
                from app.verification.acceptance_cleanup import due,record
                if item['cleanup_state']=='cleanup_failed' and not due(state,item):continue
                if not item['lease_until'] and not due(state,item):continue
                if visited>=limit:break
                visited+=1
                path=root/item['attempt_id']/'ownership.json'
                if path.is_symlink() or not path.is_file() or path.stat().st_size>8192:
                    record(state,item['id'],False)
                    with factory.begin() as db:
                        state._cas(db,state._row(db,item['id']),reason_code='ownership_checkpoint_missing')
                    continue
                owner=json.loads(path.read_text())
                if (owner['id']!=item['attempt_id'] or owner['space_id']!=item['space_id'] or
                    owner['repository_id']!=item['repository_id'] or owner['expires_at']!=item['expires_at']):continue
                clean=DockerEnvironment(root,owner,SimpleNamespace(data={})).cleanup()
                record(state,item['id'],clean)
                if not clean:continue
                if item['lease_until']:
                    state.recover(item['id'],item['epoch'],terminated=True)
                release(factory,item['id'],resources_confirmed_absent=True)
                with factory.begin() as db:
                    refs=list(db.scalars(select(identities.c.identity_ref).where(identities.c.attempt_id==item['attempt_id'])))
                    db.execute(update(identities).where(identities.c.attempt_id==item['attempt_id']).values(revocation_state='revoked'))
                for ref in refs:
                    if len(ref)==32 and all(c in '0123456789abcdef' for c in ref):
                        (root/'identities'/ref).unlink(missing_ok=True)
                count+=1
        except (Conflict,CandidateError,OSError,ValueError,KeyError):
            continue
    return count


def next_queued(factory):
    with factory() as db:
        return db.scalar(select(operations.c.id).where(operations.c.status=='queued')
                         .order_by(operations.c.queued_at,operations.c.id).limit(1))
