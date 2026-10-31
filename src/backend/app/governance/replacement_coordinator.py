"""One authoritative archive operation across merge, move and workflow sync.

No Agent/model invocation occurs here. Callers must supply the authenticated
actor and deployment signer, never caller-provided readiness booleans.
"""
from datetime import datetime,timedelta,timezone
import json
import os
from pathlib import Path
import tempfile
from sqlalchemy import select
from . import scope
from .replacement_schema import proposals,commits
from .replacement_proof import parse,canonical,digest,strict_json
from .replacement_trust import load
from .replacement_inputs import validate,fingerprint
from .replacement_commit import claim,assert_fence,checkpoint,STAGES
from .replacement_recovery import observe,resume,bound_inputs_match
from .controlled_successor import authority,proof_path
from .replacement_executor import ArchiveDriver
from .archive_admission import change_acceptance
from .archive_recovery import tree_hash,archive_paths
from .writer import project_lock
from .replacement_permissions import authorize_write


def publish(path,record,*,previous=None):
    path.parent.mkdir(parents=True,exist_ok=True)
    if any(p.is_symlink() for p in (path,path.parent,path.parent.parent)):
        raise ValueError('unsafe_replacement_proof')
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as handle:
        temporary=Path(handle.name)
        handle.write(canonical(record));handle.flush();os.fsync(handle.fileno())
    try:
        if previous is None:
            os.link(temporary,path)
        else:
            if path.read_bytes()!=previous:raise ValueError('replacement_proof_changed')
            os.replace(temporary,path)
        fd=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(fd)
        finally:os.close(fd)
    finally:
        temporary.unlink(missing_ok=True)


def prepare_proof(db, path, record, row, trust, project):
    """Refresh only an older authenticated, never-claimed version of this proof."""
    if not path.exists():
        publish(path, record)
        return
    if path.is_symlink() or path.stat().st_size > 256*1024:
        raise ValueError('unsafe_replacement_proof')
    raw = path.read_bytes()
    previous = strict_json(raw)
    if previous == record:
        return
    if (set(previous) != set(record) or previous.get('schema_version') != 1
            or previous.get('commit') is not None
            or row['state'] != 'approved' or row['operation_id'] is not None):
        raise ValueError('replacement_proof_exists')
    previous_row = row
    if previous.get('proposal') != record['proposal']:
        # A corrected, never-claimed candidate needs its own approval. Keep the
        # old ledger intact and permit replacing only its authenticated sidecar.
        old_body = previous.get('proposal', {})
        previous_row = db.execute(select(proposals).where(proposals.c.scope_key == project.key,
            proposals.c.digest == digest(old_body))).mappings().first()
        from .archive_recovery import journal_path
        if (not previous_row or previous_row['operation_id'] is not None
                or previous_row['binding_revision'] != project.binding_revision
                or strict_json(previous_row['body'].encode()) != old_body
                or any(old_body.get(key) != record['proposal'].get(key)
                       for key in ('project_id', 'binding_revision', 'successor', 'capability', 'requirement'))
                or journal_path(project.root, row['change_id']).exists()
                or archive_paths(project.root, row['change_id'])):
            raise ValueError('replacement_proof_exists')
    payload = trust.verify(previous['authorization'], purpose='replacement.approve', bindings={
        'project_id': project.key, 'binding_revision': project.binding_revision,
        'proposal_id': previous_row['id'], 'proposal_digest': previous_row['digest'],
        'policy_version': previous['proposal']['policy_version']}, historical=True)
    from .replacement_schema import events
    old = db.execute(select(events).where(events.c.proposal_id == previous_row['id'],
        events.c.revision == payload['revision'])).mappings().first()
    if (not old or strict_json(old['receipt'].encode()) != previous['authorization']
            or (previous_row['id'] == row['id'] and payload['revision'] >= row['revision'])
            or db.scalar(select(commits.c.id).where(commits.c.proposal_id.in_([row['id'], previous_row['id']])))):
        raise ValueError('replacement_proof_exists')
    publish(path, record, previous=raw)


def execute(db,*,actor,space_id,repository_id,proposal_id,operation_id,expected_revision,proposal_digest,sign,driver_type=ArchiveDriver,request_id=None):
    from .archive_finalization import needs_finalize, require_finalized
    project=scope.authorize(db,actor,space_id,repository_id,write=True)
    with project_lock(project):
        db.commit()
        project=scope.authorize(db,actor,space_id,repository_id,write=True)
        row=db.execute(select(proposals).where(proposals.c.id==proposal_id,proposals.c.scope_key==project.key)).mappings().one()
        proposal=parse(row['body'].encode());trust=load(project.root)
        receipt=json.loads(row['receipt'] or '{}')
        if row['digest']!=proposal_digest or receipt.get('payload',{}).get('revision')!=expected_revision:
            raise ValueError('archive_request_version_changed')
        operation=db.execute(select(commits).where(commits.c.id==operation_id)).mappings().first()
        if operation and (operation['proposal_id']!=proposal_id or operation['scope_key']!=project.key):
            raise ValueError('archive_operation_mismatch')
        from .archive_tools import selected, operation_binding
        package = selected()
        if operation:
            operation_binding(project.root, operation_id, package, recorded=operation['input_hash'])
        if operation and operation['stage']=='completed':
            # Completed operations may have valid later successors; verify the
            # whole chain instead of demanding the original global tree hash.
            from .archive_recovery import recovery_admission
            from .controlled_successor import verify
            from .compatible_successor import recheck
            with authority(db,project,actor):
                archives=archive_paths(project.root,proposal.successor)
                if len(archives)!=1:raise ValueError('archive_history_changed')
                certificate=verify(project.root,proposal.successor,archives[0],(proposal.capability,proposal.requirement),proposal.before,proposal.after)
                if not recovery_admission(project.root,proposal.successor)['ready']:raise ValueError('archive_history_changed')
                recheck(project.root,certificate)
            require_finalized(project.root,proposal.successor)
            return {'operation_id':operation_id,'stage':'completed','replayed':True}
        driver=driver_type(project)
        path=proof_path(project.root,proposal.successor,(proposal.capability,proposal.requirement))
        record={'schema_version':1,'proposal':proposal.model_dump(),'authorization':json.loads(row['receipt'] or '{}'),'commit':None}
        if not operation:
            authorize_write(db,project,actor,expected_owner=receipt.get('payload',{}).get('actor_id'))
            validate(project,proposal,trust)
            prepare_proof(db,path,record,row,trust,project)
            with authority(db,project,actor):
                admission=change_acceptance(project.root,proposal.successor,source_root=project.source_root)
                if not admission['ready']:raise ValueError('independent_archive_gate_blocked')
                driver.validate_static(proposal.successor)
                expected=driver.prepare(proposal.successor)
            operation=claim(db,project=project,proposal_id=proposal_id,revision=row['revision'],actor=actor,
                operation_id=operation_id,input_hash=operation_binding(project.root, operation_id, package, original=fingerprint(project,proposal)),expected_hash=expected,trust=trust,request_id=request_id)
            db.commit()
            state='unmerged';fence=operation['fence']
        else:
            state,fence=resume(db,project=project,proposal=proposal,operation_id=operation_id,actor=actor,trust=trust)
            db.commit()
        with authority(db,project,actor,operation_id,fence):
            operation=assert_fence(db,operation_id,fence)
            if state=='unmerged':
                authorize_write(db,project,actor)
                # Fresh evidence, sign-off and external-input checks immediately
                # precede the write while the project OS lock remains held.
                validate(project,proposal,trust)
                admission=change_acceptance(project.root,proposal.successor,source_root=project.source_root)
                if not admission['ready']:raise ValueError('independent_archive_gate_blocked')
                if not bound_inputs_match(project, proposal, operation):raise ValueError('archive_inputs_changed')
                driver.recheck_tools();assert_fence(db,operation_id,fence)
                driver.merge_and_move(proposal.successor)
                state=observe(project,proposal,operation)
            if state=='merged':
                authorize_write(db,project,actor)
                assert_fence(db,operation_id,fence);driver.merge_and_move(proposal.successor,move_only=True)
                state=observe(project,proposal,operation)
            if state not in {'moved','synced'}:raise ValueError('archive_result_unknown')
            for stage in ('merge_verified','move_verified'):
                operation=assert_fence(db,operation_id,fence)
                if STAGES.index(operation['stage'])<STAGES.index(stage):
                    checkpoint(db,operation_id=operation_id,fence=fence,expected_revision=operation['revision'],stage=stage,
                        observed_hash=tree_hash(project.root/'openspec/specs'),request_id=request_id);db.commit()
            if operation['stage']!='synced' and (state!='synced' or needs_finalize(project.root,proposal.successor)):
                authorize_write(db,project,actor)
                assert_fence(db,operation_id,fence);driver.finalize(proposal.successor)
            operation=assert_fence(db,operation_id,fence)
            if observe(project,proposal,operation)!='synced':raise ValueError('archive_sync_unverified')
            if operation['stage']=='move_verified':
                checkpoint(db,operation_id=operation_id,fence=fence,expected_revision=operation['revision'],stage='synced',
                    observed_hash=tree_hash(project.root/'openspec/specs'),request_id=request_id);db.commit()
            require_finalized(project.root,proposal.successor)
            authorize_write(db,project,actor)
            raw=path.read_bytes();record=strict_json(raw)
            if (record.get('proposal')!=proposal.model_dump() or record.get('authorization')!=receipt
                    or set(record)!={'schema_version','proposal','authorization','commit'} or record['schema_version']!=1):
                raise ValueError('replacement_proof_changed')
            archive=archive_paths(project.root,proposal.successor)[0]
            from .replacement_commit_evidence import bindings as journal_bindings
            bindings={'project_id':project.key,'binding_revision':project.binding_revision,'proposal_digest':row['digest'],
                'policy_version':proposal.policy_version,'release_digest':trust.release_digest,
                'authorization_sha256':digest(record['authorization']),'archive_identity':archive.name,
                'delta_sha256':proposal.delta_sha256,'acceptance_sha256':proposal.acceptance_sha256,'operation_id':operation_id,
                **journal_bindings(project.root,proposal.successor)}
            if bindings['expected_spec_hash']!=operation['expected_hash']:
                raise ValueError('archive_journal_changed')
            if record['commit']:
                trust.verify(record['commit'],purpose='replacement.commit',bindings=bindings,historical=True)
            else:
                now=datetime.now(timezone.utc).replace(microsecond=0)
                record['commit']=sign({**bindings,'schema_version':1,'purpose':'replacement.commit','actor_id':actor,
                    'issued_at':now.isoformat(),'expires_at':(now+timedelta(hours=24)).isoformat()})
                trust.verify(record['commit'],purpose='replacement.commit',bindings=bindings)
                publish(path,record,previous=raw)
            operation=assert_fence(db,operation_id,fence)
            if (path.read_bytes()!=canonical(record) or observe(project,proposal,operation)!='synced'
                    or journal_bindings(project.root,proposal.successor)!=
                    {key:bindings[key] for key in ('journal_sha256','baseline_spec_hash','expected_spec_hash')}):
                raise ValueError('archive_commit_changed')
            checkpoint(db,operation_id=operation_id,fence=fence,expected_revision=operation['revision'],stage='completed',
                observed_hash=tree_hash(project.root/'openspec/specs'),request_id=request_id);db.commit()
        return {'operation_id':operation_id,'stage':'completed','replayed':False}
