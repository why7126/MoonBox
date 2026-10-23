"""Read-only authoritative decision shared by product and online CLI callers."""
import json
from sqlalchemy import select
from app.chat.service import ChatError
from .replacement_schema import proposals, activations
from .replacement_proof import parse
from .replacement_trust import load
from .replacement_inputs import validate, fingerprint
from .replacement_permissions import authorize_write
from .controlled_successor import authority
from .archive_admission import change_acceptance


def admit(db, project, actor, row):
    result = {'decision': 'blocked', 'reason_code': 'replacement_not_ready', 'blockers': [],
              'proposal_revision': row['revision'], 'proposal_digest': row['digest'],
              'policy_version': None, 'input_fingerprint': None, 'operation_id': row['operation_id']}
    reason = 'replacement_not_ready'
    try:
        trust = load(project.root)
        result['policy_version'] = trust.policy_version
        proposal = parse(row['body'].encode())
        authorize_write(db, project, actor, lock=False)
        policy = db.execute(select(activations).where(activations.c.scope_key == project.key)).mappings().first()
        if not policy or policy['state'] != 'active' or policy['policy_version'] != trust.policy_version or policy['binding_revision'] != project.binding_revision:
            reason = 'policy_not_active'
        elif row['binding_revision'] != project.binding_revision:
            reason = 'replacement_binding_changed'
        elif row['state'] == 'claimed':
            # This is a direction to recover the same operation, never permission
            # to repeat a merge. The coordinator independently observes its state.
            return {**result, 'decision': 'resume', 'reason_code': 'original_operation_required'}
        elif row['state'] not in {'approved', 'completed'}:
            reason = 'authorization_required'
        else:
            if row['state'] == 'approved':
                receipt = json.loads(row['receipt'])
                trust.verify(receipt, purpose='replacement.approve', bindings={
                    'project_id': project.key, 'binding_revision': project.binding_revision,
                    'proposal_id': row['id'], 'proposal_digest': row['digest'], 'revision': row['revision'],
                    'policy_version': trust.policy_version, 'release_digest': trust.release_digest})
                authorize_write(db, project, actor, expected_owner=receipt['payload']['actor_id'], lock=False)
                validate(project, proposal, trust)
                result['input_fingerprint'] = fingerprint(project, proposal)
            with authority(db, project, actor):
                if row['state'] == 'completed':
                    from .archive_recovery import archive_paths
                    from .controlled_successor import verify
                    from .compatible_successor import recheck
                    folders=archive_paths(project.root,proposal.successor)
                    if len(folders)!=1:raise ValueError('archive_history_changed')
                    certificate=verify(project.root,proposal.successor,folders[0],
                        (proposal.capability,proposal.requirement),proposal.before,proposal.after,
                        source_root=project.source_root)
                    recheck(project.root,certificate)
                admission = change_acceptance(project.root, proposal.successor, source_root=project.source_root)
            if admission['ready']:
                # A fresh transaction detects revocation during the file scan.
                from sqlalchemy.orm import Session
                with Session(db.get_bind()) as fresh:
                    current = fresh.execute(select(proposals).where(proposals.c.id == row['id'])).mappings().one()
                    if current['revision'] != row['revision'] or current['state'] != row['state']:
                        raise ValueError('authorization_changed')
                    authorize_write(fresh, project, actor, expected_owner=(receipt['payload']['actor_id']
                        if row['state']=='approved' else None), lock=False)
                return {**result, 'decision': 'ready', 'reason_code': 'archive_ready'}
            reason = 'independent_archive_gate_blocked'
    except ChatError:
        reason = 'permission_or_scope_changed'
    except (ValueError, OSError, KeyError, TypeError):
        reason = 'trust_authorization_or_evidence_changed'
    return {**result, 'reason_code': reason, 'blockers': [reason]}
