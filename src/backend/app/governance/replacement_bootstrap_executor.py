"""Install only the independently signed mechanism transition, then expose active."""
from datetime import datetime,timedelta,timezone
import json
from types import SimpleNamespace
from sqlalchemy import select
from . import scope,replacement_bootstrap_commit as commit
from .replacement_schema import activations
from .replacement_bootstrap import Installation,verify_installation
from .replacement_trust import load
from .replacement_activation import inputs
from .replacement_inputs import fingerprint
from .replacement_recovery import observe
from .replacement_executor import ArchiveDriver
from .replacement_coordinator import publish
from .replacement_proof import digest
from .controlled_successor import authority,proof_path
from .archive_admission import change_acceptance
from .archive_recovery import tree_hash,archive_paths,recovery_admission
from .writer import project_lock
from .replacement_commit import STAGES
from .replacement_permissions import authorize_write
from .replacement_commit_evidence import bindings as journal_bindings
from .replacement_proof import canonical,strict_json


def prepare_proof(db,path,record,row,manifest,trust,project):
    if not path.exists():
        publish(path,record)
        return
    if path.is_symlink() or path.stat().st_size>256*1024:raise ValueError('unsafe_bootstrap_proof')
    raw=path.read_bytes();previous=strict_json(raw)
    if previous==record:return
    if (set(previous)!=set(record) or previous.get('schema_version')!=2
            or previous.get('installation')!=record['installation'] or previous.get('commit') is not None
            or row['state']!='authorized' or row['stage']!='prepared' or row['fence']!=0):
        raise ValueError('bootstrap_proof_exists')
    verify_installation(manifest,trust,ops_receipt=previous['ops_receipt'],owner_receipt=previous['owner_receipt'],
        project=project,current_policy=manifest.from_policy,release_digest=trust.release_digest,
        verifier_digest=manifest.verifier_digest,historical=True)
    from .replacement_schema import events
    for name in ('ops_receipt','owner_receipt'):
        event=db.execute(select(events).where(events.c.proposal_id==row['id'],
            events.c.request_key==digest(previous[name]),events.c.revision<row['revision'])).mappings().first()
        if not event or strict_json(event['receipt'].encode())!=previous[name]:raise ValueError('bootstrap_proof_exists')
    publish(path,record,previous=raw)


def execute(db,*,actor,space_id,repository_id,manifest_hash,sign,driver_type=ArchiveDriver):
    from .archive_finalization import needs_finalize, require_finalized
    project=scope.authorize(db,actor,space_id,repository_id,write=True)
    with project_lock(project):
        db.commit();project=scope.authorize(db,actor,space_id,repository_id,write=True)
        row=db.execute(select(activations).where(activations.c.scope_key==project.key)).mappings().one()
        if row['manifest_hash']!=manifest_hash:raise ValueError('bootstrap_manifest_changed')
        manifest=Installation.model_validate(json.loads(row['manifest']));trust=load(project.root)
        ops=json.loads(row['ops_receipt'] or '{}');owner=json.loads(row['owner_receipt'] or '{}')
        if row['state'] not in {'authorized','activating','active'}:raise ValueError('bootstrap_not_authorized')
        verify_installation(manifest,trust,ops_receipt=ops,owner_receipt=owner,project=project,
            current_policy=manifest.from_policy,release_digest=trust.release_digest,verifier_digest=manifest.verifier_digest,
            historical=row['state'] in {'activating','active'})
        change=manifest.mechanism_change;operation_id=manifest.operation_id
        facade=SimpleNamespace(successor=change,delta_sha256=manifest.delta_digest,delivery_sha256=manifest.delivery_digest)
        transition=manifest.transitions[0];key=(transition.capability,transition.requirement)
        path=proof_path(project.root,change,key)
        if row['state']=='active':
            if path.is_symlink() or any(p.is_symlink() for p in (path.parent,path.parent.parent)):
                raise ValueError('unsafe_bootstrap_proof')
            from .replacement_inputs import replacement_delivery_hash
            from .compatible_successor import acceptance_binding
            archives=archive_paths(project.root,change)
            if len(archives)!=1:raise ValueError('bootstrap_history_changed')
            proof=strict_json(path.read_bytes())
            if (proof.get('installation')!=manifest.model_dump() or proof.get('ops_receipt')!=ops or proof.get('owner_receipt')!=owner
                    or tree_hash(archives[0]/'specs')!=manifest.delta_digest or replacement_delivery_hash(archives[0])!=manifest.delivery_digest
                    or acceptance_binding(project.root,archives[0])!=manifest.acceptance_digest):
                raise ValueError('bootstrap_history_changed')
            trust.verify(proof.get('commit'),purpose='bootstrap.commit',bindings={'project_id':project.key,
                'binding_revision':project.binding_revision,'installation_digest':manifest_hash,'operation_id':operation_id,
                'release_digest':trust.release_digest,'archive_identity':archives[0].name,
                **journal_bindings(project.root,change)},historical=True)
            with authority(db,project,actor):
                if not recovery_admission(project.root,change)['ready']:raise ValueError('bootstrap_history_changed')
            require_finalized(project.root,change)
            return {'state':'active','revision':row['revision'],'operation_id':operation_id}
        driver=driver_type(project)
        if row['state']=='authorized':
            authorize_write(db,project,actor,expected_owner=owner.get('payload',{}).get('actor_id'))
            inputs(project,manifest,trust)
            record={'schema_version':2,'installation':manifest.model_dump(),'ops_receipt':ops,'owner_receipt':owner,'commit':None}
            prepare_proof(db,path,record,row,manifest,trust,project)
            with authority(db,project,actor):
                if not change_acceptance(project.root,change,source_root=project.source_root)['ready']:
                    raise ValueError('independent_archive_gate_blocked')
                driver.validate_static(change)
                if driver.prepare(change)!=manifest.expected_digest:raise ValueError('bootstrap_expected_effect_mismatch')
            fence=commit.claim(db,project,operation_id,row['revision'],fingerprint(project,facade));db.commit()
            state='unmerged'
        else:
            operation={**dict(row),'expected_hash':manifest.expected_digest}
            state=observe(project,facade,operation)
            fence=commit.renew(db,project,operation_id);db.commit()
        with authority(db,project,actor,operation_id,fence):
            row=commit.assert_fence(db,project,operation_id,fence)
            if state=='unmerged':
                authorize_write(db,project,actor)
                inputs(project,manifest,trust)
                if not change_acceptance(project.root,change,source_root=project.source_root)['ready']:
                    raise ValueError('independent_archive_gate_blocked')
                if fingerprint(project,facade)!=row['input_hash']:raise ValueError('bootstrap_inputs_changed')
                commit.assert_fence(db,project,operation_id,fence);driver.merge_and_move(change)
                state=observe(project,facade,{**dict(row),'expected_hash':manifest.expected_digest})
            if state=='merged':
                authorize_write(db,project,actor)
                commit.assert_fence(db,project,operation_id,fence);driver.merge_and_move(change,move_only=True)
                state=observe(project,facade,{**dict(row),'expected_hash':manifest.expected_digest})
            if state not in {'moved','synced'}:raise ValueError('bootstrap_effect_unknown')
            for stage in ('merge_verified','move_verified'):
                row=commit.assert_fence(db,project,operation_id,fence)
                if STAGES.index(row['stage'])<STAGES.index(stage):
                    commit.checkpoint(db,project,operation_id,fence,stage,tree_hash(project.root/'openspec/specs'),manifest.expected_digest);db.commit()
            if row['stage']!='synced' and (state!='synced' or needs_finalize(project.root,change)):
                authorize_write(db,project,actor)
                commit.assert_fence(db,project,operation_id,fence);driver.finalize(change)
            row=commit.assert_fence(db,project,operation_id,fence)
            if observe(project,facade,{**dict(row),'expected_hash':manifest.expected_digest})!='synced':
                raise ValueError('bootstrap_sync_unverified')
            if row['stage']=='move_verified':
                commit.checkpoint(db,project,operation_id,fence,'synced',tree_hash(project.root/'openspec/specs'),manifest.expected_digest);db.commit()
            require_finalized(project.root,change)
            authorize_write(db,project,actor)
            raw=path.read_bytes();record=strict_json(raw)
            if (record.get('installation')!=manifest.model_dump() or record.get('ops_receipt')!=ops
                    or record.get('owner_receipt')!=owner or record.get('schema_version')!=2
                    or set(record)!={'schema_version','installation','ops_receipt','owner_receipt','commit'}):
                raise ValueError('bootstrap_proof_changed')
            archives=archive_paths(project.root,change)
            if len(archives)!=1:raise ValueError('bootstrap_archive_ambiguous')
            bindings={'project_id':project.key,'binding_revision':project.binding_revision,'installation_digest':manifest_hash,
                'operation_id':operation_id,'release_digest':trust.release_digest,'archive_identity':archives[0].name,
                **journal_bindings(project.root,change)}
            if bindings['baseline_spec_hash']!=manifest.baseline_digest or bindings['expected_spec_hash']!=manifest.expected_digest:
                raise ValueError('bootstrap_journal_changed')
            if record['commit']:
                trust.verify(record['commit'],purpose='bootstrap.commit',bindings=bindings,historical=True)
            else:
                now=datetime.now(timezone.utc).replace(microsecond=0)
                record['commit']=sign({**bindings,'schema_version':1,'purpose':'bootstrap.commit','actor_id':actor,
                    'issued_at':now.isoformat(),'expires_at':(now+timedelta(hours=24)).isoformat()})
                trust.verify(record['commit'],purpose='bootstrap.commit',bindings=bindings)
                publish(path,record,previous=raw)
            # Single DB transaction publishes active only after the mechanism's
            # archive, sync and immutable commit receipt can all be reread.
            if (path.read_bytes()!=canonical(record)
                    or journal_bindings(project.root,change)!={key:bindings[key] for key in ('journal_sha256','baseline_spec_hash','expected_spec_hash')}
                    or observe(project,facade,{**dict(row),'expected_hash':manifest.expected_digest})!='synced'):
                raise ValueError('bootstrap_commit_changed')
            commit.checkpoint(db,project,operation_id,fence,'completed',tree_hash(project.root/'openspec/specs'),manifest.expected_digest);db.commit()
            row=db.execute(select(activations).where(activations.c.scope_key==project.key)).mappings().one()
            return {'state':'active','revision':row['revision'],'operation_id':operation_id}
