"""Prepare and authorize an exact installation, without exposing policy as active."""
from datetime import datetime, timedelta, timezone
import json
from sqlalchemy import insert, select, update
from app.chat.service import identity, ChatError
from .replacement_schema import activations, events
from .replacement_proof import PROTECTED, canonical, digest
from .replacement_bootstrap import Installation, verify_installation
from .archive_recovery import tree_hash, delta_operations
from .compatible_successor import acceptance_binding


def audit(db,row,receipt,revision):
    """Installation receipts use the same database-enforced immutable ledger."""
    payload=receipt['payload']
    db.execute(insert(events).values(**identity(),scope_key=row['scope_key'],proposal_id=row['id'],
        actor_id=payload['actor_id'],purpose=payload['purpose'],request_key=digest(receipt),
        request_hash=digest({'manifest_hash':row['manifest_hash'],'receipt':receipt}),revision=revision,
        receipt=canonical(receipt).decode()))


def inputs(project, manifest, trust):
    import hashlib
    from pathlib import Path
    from . import replacement_bootstrap
    actual_verifier = hashlib.sha256(Path(replacement_bootstrap.__file__).read_bytes()).hexdigest()
    if (manifest.project_id!=project.key or manifest.binding_revision!=project.binding_revision
            or manifest.to_policy!=trust.policy_version or manifest.release_digest!=trust.release_digest
            or manifest.from_policy==manifest.to_policy or set(manifest.protected_obligations)!=PROTECTED
            or manifest.verifier_digest!=actual_verifier):
        raise ValueError('bootstrap_binding_mismatch')
    folder=project.root/'openspec/changes'/manifest.mechanism_change
    from .replacement_inputs import replacement_delivery_hash
    if (tree_hash(folder/'specs')!=manifest.delta_digest
            or replacement_delivery_hash(folder)!=manifest.delivery_digest
            or acceptance_binding(project.root,folder,source_root=project.source_root)!=manifest.acceptance_digest
            or tree_hash(project.root/'openspec/specs')!=manifest.baseline_digest):
        raise ValueError('bootstrap_inputs_changed')
    operations=delta_operations(folder)
    if not operations or any(kind not in {'ADDED','MODIFIED'} for kind,_ in operations.values()):
        raise ValueError('unsupported_policy_installation')
    # First installation may only replace this mechanism's protected policy rule.
    if any(kind=='MODIFIED' and key!=('governance-command-durable-recovery','归档连续证明的条文冲突范围')
           for key,(kind,_) in operations.items()):
        raise ValueError('unsupported_policy_installation')
    from .archive_recovery import requirement_blocks
    expected=[]
    for (capability,title),(kind,after) in operations.items():
        if kind!='MODIFIED':continue
        before=requirement_blocks((project.root/'openspec/specs'/capability/'spec.md').read_text()).get(title)
        if not before:raise ValueError('bootstrap_baseline_missing')
        expected.append({'capability':capability,'requirement':title,
            'before_sha256':hashlib.sha256(before.encode()).hexdigest(),
            'after_sha256':hashlib.sha256(after.encode()).hexdigest()})
    if [item.model_dump() for item in manifest.transitions]!=expected:
        raise ValueError('bootstrap_transition_mismatch')


def prepare(db,project,manifest:Installation,ops_receipt,trust):
    inputs(project,manifest,trust)
    bindings={'project_id':project.key,'binding_revision':project.binding_revision,
              'installation_digest':digest(manifest.model_dump()),'operation_id':manifest.operation_id,
              'release_digest':trust.release_digest}
    trust.verify(ops_receipt,purpose='bootstrap.ops',bindings=bindings)
    if not trust.independent_bootstrap():
        raise ValueError('bootstrap_roles_not_independent')
    previous=db.execute(select(activations).where(activations.c.scope_key==project.key)).mappings().first()
    if previous:
        if previous['manifest_hash']!=bindings['installation_digest']:
            raise ValueError('bootstrap_operation_exists')
        if previous['state'] in {'prepared','authorized'}:
            expired=any(datetime.fromisoformat(json.loads(previous[name])['payload']['expires_at'])<=datetime.now(timezone.utc)
                for name in ('ops_receipt','owner_receipt') if previous[name])
            if expired:
                # Preserve the exact installation and operation. Fresh deployment
                # authorization always requires a fresh independent owner action.
                revision=previous['revision']+1
                won=db.execute(update(activations).where(activations.c.id==previous['id'],
                    activations.c.revision==previous['revision'],activations.c.state==previous['state']).values(
                    state='prepared',ops_receipt=canonical(ops_receipt).decode(),owner_receipt=None,revision=revision)).rowcount
                if won!=1:raise ValueError('bootstrap_revision_changed')
                audit(db,previous,ops_receipt,revision)
                return {**previous,'state':'prepared','ops_receipt':canonical(ops_receipt).decode(),
                        'owner_receipt':None,'revision':revision}
        return dict(previous)
    if manifest.from_policy != 'legacy-v1':
        raise ValueError('bootstrap_previous_policy_unknown')
    row={**identity(),'scope_key':project.key,'binding_revision':project.binding_revision,
         'policy_version':manifest.to_policy,'state':'prepared','manifest_hash':bindings['installation_digest'],
         'manifest':canonical(manifest.model_dump()).decode(),'ops_receipt':canonical(ops_receipt).decode(),
         'revision':1,'operation_id':manifest.operation_id}
    db.execute(insert(activations).values(**row))
    audit(db,row,ops_receipt,1)
    return row


def confirm(db,project,actor,expected_revision,manifest_hash,trust,sign):
    row=db.execute(select(activations).where(activations.c.scope_key==project.key)).mappings().one()
    if row['manifest_hash']==manifest_hash and row['revision']==expected_revision+1 and row['state']=='authorized':
        receipt=json.loads(row['owner_receipt'])
        trust.verify(receipt,purpose='bootstrap.owner',bindings={'actor_id':actor,'project_id':project.key,
            'binding_revision':project.binding_revision,'installation_digest':manifest_hash})
        return {'id':row['id'],'state':row['state'],'revision':row['revision']}
    if row['manifest_hash']!=manifest_hash or row['revision']!=expected_revision or row['state']!='prepared':
        raise ValueError('bootstrap_revision_changed')
    manifest=Installation.model_validate(json.loads(row['manifest']))
    inputs(project,manifest,trust)
    now=datetime.now(timezone.utc).replace(microsecond=0)
    receipt=sign({'schema_version':1,'purpose':'bootstrap.owner','actor_id':actor,
        'project_id':project.key,'binding_revision':project.binding_revision,
        'installation_digest':manifest_hash,'operation_id':manifest.operation_id,'release_digest':trust.release_digest,
        'issued_at':now.isoformat(),'expires_at':(now+timedelta(hours=24)).isoformat()})
    verify_installation(manifest,trust,ops_receipt=json.loads(row['ops_receipt']),owner_receipt=receipt,
        project=project,current_policy=manifest.from_policy,release_digest=trust.release_digest,
        verifier_digest=manifest.verifier_digest,now=now)
    won=db.execute(update(activations).where(activations.c.id==row['id'],activations.c.revision==expected_revision,
        activations.c.state=='prepared').values(owner_receipt=canonical(receipt).decode(),state='authorized',revision=expected_revision+1)).rowcount
    if won!=1: raise ValueError('bootstrap_revision_changed')
    audit(db,row,receipt,expected_revision+1)
    return {'id':row['id'],'state':'authorized','revision':expected_revision+1}
