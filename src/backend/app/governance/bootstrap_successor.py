"""Exact installation edge, independently authorized by deployment and owner."""
import hashlib
import json
from sqlalchemy import select,text
from .replacement_bootstrap import Installation,verify_installation
from .replacement_proof import digest
from .replacement_schema import activations
from .replacement_inputs import replacement_delivery_hash
from .compatible_successor import acceptance_binding
from .archive_recovery import tree_hash,completed_archive,archive_paths


def verify(root,successor,folder,key,before,after,*,record,path,raw,context,trust,source_root=None):
    if set(record)!={'schema_version','installation','ops_receipt','owner_receipt','commit'} or record['schema_version']!=2:
        raise ValueError('unsupported_installation_proof')
    db,project,actor,operation_id,fence=context
    manifest=Installation.model_validate(record['installation'])
    transition={'capability':key[0],'requirement':key[1],'before_sha256':hashlib.sha256(before.encode()).hexdigest(),
                'after_sha256':hashlib.sha256(after.encode()).hexdigest()}
    if (manifest.mechanism_change!=successor or transition not in [x.model_dump() for x in manifest.transitions]
            or tree_hash(folder/'specs')!=manifest.delta_digest or replacement_delivery_hash(folder)!=manifest.delivery_digest
            or acceptance_binding(root,folder,source_root=source_root)!=manifest.acceptance_digest):
        raise ValueError('installation_edge_mismatch')
    state=db.execute(select(activations).where(activations.c.scope_key==project.key)).mappings().first()
    historical=folder.parent.name=='archive'
    if not state or state['manifest_hash']!=digest(manifest.model_dump()) or state['operation_id']!=manifest.operation_id:
        raise ValueError('installation_authority_missing')
    claimed=state['state']=='activating'
    if historical and claimed and operation_id==manifest.operation_id:
        from .replacement_bootstrap_commit import assert_fence
        assert_fence(db,project,operation_id,fence)
        if len(archive_paths(root,successor))!=1 or (root/'openspec/changes'/successor).exists():
            raise ValueError('installation_archive_ambiguous')
        historical=False
    if historical:
        if state['state']!='active' or not completed_archive(folder,successor) or len(archive_paths(root,successor))!=1 or (root/'openspec/changes'/successor).exists():
            raise ValueError('installation_not_completed')
    elif state['state']=='authorized':
        if tree_hash(root/'openspec/specs')!=manifest.baseline_digest:raise ValueError('installation_baseline_changed')
    elif claimed:
        from .replacement_bootstrap_commit import assert_fence
        if operation_id!=manifest.operation_id:raise ValueError('installation_operation_mismatch')
        assert_fence(db,project,operation_id,fence)
    else:raise ValueError('installation_not_authorized')
    if not historical:
        from .scope import authorize
        authorize(db,actor,project.space_id,project.repository_id,write=True)
        owner=db.scalar(text('SELECT owner_id FROM admin_spaces WHERE id=:space'),{'space':project.space_id})
        if not claimed and owner!=record['owner_receipt'].get('payload',{}).get('actor_id'):
            raise ValueError('installation_owner_changed')
    verify_installation(manifest,trust,ops_receipt=record['ops_receipt'],owner_receipt=record['owner_receipt'],
        project=project,current_policy=manifest.from_policy,release_digest=trust.release_digest,
        verifier_digest=manifest.verifier_digest,historical=historical or claimed)
    commit_bindings={'project_id':project.key,'binding_revision':project.binding_revision,
        'installation_digest':digest(manifest.model_dump()),'operation_id':manifest.operation_id,
        'archive_identity':folder.name,'release_digest':trust.release_digest}
    dependencies=[]
    if historical:
        from .replacement_commit_evidence import bindings as journal_bindings
        from .archive_recovery import journal_path
        journal=journal_bindings(root,successor)
        if journal['baseline_spec_hash']!=manifest.baseline_digest or journal['expected_spec_hash']!=manifest.expected_digest:
            raise ValueError('installation_journal_changed')
        commit_bindings.update(journal)
        trust.verify(record['commit'],purpose='bootstrap.commit',bindings=commit_bindings,historical=True)
        dependencies.append({'path':journal_path(root,successor).relative_to(root).as_posix(),'sha256':journal['journal_sha256']})
    if path.read_bytes()!=raw:raise ValueError('installation_proof_changed')
    return {'proof_sha256':hashlib.sha256(raw).hexdigest(),'proof_path':path.relative_to(root).as_posix(),'dependencies':dependencies,
        'bootstrap':{'record':record,'commit_bindings':commit_bindings,'historical':historical,'claimed':claimed,
                     'revision':state['revision'],'state':state['state']}}


def recheck(certificate,context,trust):
    from sqlalchemy.orm import Session
    db,project,actor,operation_id,fence=context
    record=certificate['record'];manifest=Installation.model_validate(record['installation'])
    with Session(db.get_bind()) as fresh:
        state=fresh.execute(select(activations).where(activations.c.scope_key==project.key)).mappings().first()
        if not state or state['revision']!=certificate['revision'] or state['state']!=certificate['state']:
            raise ValueError('installation_authority_changed')
        if certificate['claimed']:
            from .replacement_bootstrap_commit import assert_fence
            assert_fence(fresh,project,operation_id,fence)
        if not certificate['historical']:
            from .scope import authorize
            current=authorize(fresh,actor,project.space_id,project.repository_id,write=True)
            if current.binding_revision!=project.binding_revision:raise ValueError('installation_binding_changed')
            if not certificate['claimed']:
                owner=fresh.scalar(text('SELECT owner_id FROM admin_spaces WHERE id=:space'),{'space':project.space_id})
                if owner!=record['owner_receipt']['payload']['actor_id']:raise ValueError('installation_owner_changed')
    verify_installation(manifest,trust,ops_receipt=record['ops_receipt'],owner_receipt=record['owner_receipt'],
        project=project,current_policy=manifest.from_policy,release_digest=trust.release_digest,
        verifier_digest=manifest.verifier_digest,historical=certificate['historical'] or certificate['claimed'])
    if certificate['historical']:
        trust.verify(record['commit'],purpose='bootstrap.commit',bindings=certificate['commit_bindings'],historical=True)
