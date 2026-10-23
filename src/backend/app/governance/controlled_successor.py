"""Controlled edges require authority context; ordinary append proofs stay separate."""
from .replacement_inputs import replacement_delivery_hash
from contextlib import contextmanager
from contextvars import ContextVar
import hashlib
import json
from sqlalchemy import select, text
from .replacement_proof import parse, digest, classify, strict_json, canonical
from .replacement_trust import load
from .replacement_schema import proposals, activations
from .compatible_successor import evidence_file, acceptance_binding

_authority = ContextVar('replacement_authority', default=None)


@contextmanager
def authority(db, project, actor, operation_id=None, fence=None):
    token = _authority.set((db, project, actor, operation_id, fence))
    try: yield
    finally: _authority.reset(token)


def proof_path(root, successor, key):
    from .archive_recovery import IDENTITY
    if not IDENTITY.fullmatch(successor): raise ValueError('invalid_successor')
    return root / 'openspec/archive/.controlled-successors' / successor / (hashlib.sha256('\0'.join(key).encode()).hexdigest()+'.json')


def verify(root, successor, folder, key, before, after, *, source_root=None):
    from .archive_recovery import tree_hash, completed_archive, archive_paths, delivery_input_hash
    context = _authority.get()
    if context is None:
        raise ValueError('replacement_authority_unavailable')
    db, project, actor, operation_id, fence = context
    if folder == root/'openspec/changes'/successor and operation_id is None:
        raise ValueError('legacy_replacement_candidate_retired')
    trust = load(project.root)
    path = proof_path(root, successor, key)
    virtual = False
    if path.is_symlink() or any(p.is_symlink() for p in (path.parent, path.parent.parent)):
        raise ValueError('unsafe_replacement_proof')
    if not path.exists() and folder == root/'openspec/changes'/successor:
        # Read-only candidate admission uses the signed authoritative row. It
        # must not publish a sidecar or turn a candidate into archived history.
        matches = []
        for row in db.execute(select(proposals).where(proposals.c.scope_key==project.key,
                proposals.c.change_id==successor, proposals.c.state=='approved')).mappings():
            value = parse(row['body'].encode())
            if ((value.capability,value.requirement)==key and value.before==before and value.after==after
                    and value.delta_sha256==tree_hash(folder/'specs')
                    and value.delivery_sha256==replacement_delivery_hash(folder)
                    and value.acceptance_sha256==acceptance_binding(root,folder,source_root=source_root)):
                matches.append({'schema_version':1,'proposal':value.model_dump(),
                    'authorization':strict_json(row['receipt'].encode()),'commit':None})
        if len(matches)!=1:raise ValueError('replacement_candidate_ambiguous')
        raw=canonical(matches[0]);virtual=True
    else:
        if path.stat().st_size > 256*1024:raise ValueError('unsafe_replacement_proof')
        raw = path.read_bytes()
    record = strict_json(raw)
    if record.get('schema_version') == 2:
        from .bootstrap_successor import verify as verify_bootstrap
        return verify_bootstrap(root,successor,folder,key,before,after,record=record,path=path,raw=raw,
            context=context,trust=trust,source_root=source_root)
    if set(record) != {'schema_version','proposal','authorization','commit'} or record['schema_version'] != 1:
        raise ValueError('unsupported_replacement_proof')
    proposal = parse(json.dumps(record['proposal'], ensure_ascii=False).encode())
    classify(proposal, trust.profiles)
    if (proposal.project_id != project.key or proposal.binding_revision != project.binding_revision
            or proposal.successor != successor or (proposal.capability,proposal.requirement) != key
            or proposal.before != before or proposal.after != after
            or proposal.policy_version != trust.policy_version):
        raise ValueError('replacement_identity_mismatch')
    if (proposal.delta_sha256 != tree_hash(folder/'specs')
            or proposal.delivery_sha256 != replacement_delivery_hash(folder)
            or proposal.acceptance_sha256 != acceptance_binding(root,folder,source_root=source_root)):
        raise ValueError('replacement_evidence_changed')
    certificate = record['authorization']
    proposal_digest = digest(proposal.model_dump())
    historical = folder.parent.name == 'archive'
    bindings = {'project_id': project.key, 'binding_revision': project.binding_revision,
                'proposal_digest': proposal_digest, 'policy_version': trust.policy_version}
    claimed = False
    if operation_id:
        from .replacement_schema import commits
        from .replacement_commit import assert_fence
        claim = db.execute(select(commits).where(commits.c.id==operation_id,
            commits.c.scope_key==project.key)).mappings().first()
        if claim and claim['proposal_id']==certificate.get('payload',{}).get('proposal_id'):
            assert_fence(db,operation_id,fence)
            if claim['actor_id']!=actor:raise ValueError('replacement_operation_mismatch')
            claimed = True
            if historical:
                if len(archive_paths(root,successor))!=1 or (root/'openspec/changes'/successor).exists():
                    raise ValueError('incomplete_replacement_archive')
                # Only the fenced original operation may inspect its moved but
                # not yet committed edge while synchronizing workflow facts.
                historical = False
        elif not historical:
            raise ValueError('replacement_operation_mismatch')
    payload = trust.verify(certificate,purpose='replacement.approve',bindings=bindings,historical=historical or claimed)
    if historical:
        if not completed_archive(folder, successor) or len(archive_paths(root,successor)) != 1 or (root/'openspec/changes'/successor).exists():
            raise ValueError('incomplete_replacement_archive')
        for predecessor in proposal.predecessors:
            previous = archive_paths(root,predecessor)
            if len(previous)!=1 or not completed_archive(previous[0],predecessor) or (root/'openspec/changes'/predecessor).exists():
                raise ValueError('incomplete_replacement_archive_chain')
        from .replacement_commit_evidence import bindings as journal_bindings
        journal = journal_bindings(root,successor)
        commit_bindings = {**bindings, **journal,
            'authorization_sha256':digest(certificate),'archive_identity':folder.name,
            'delta_sha256':proposal.delta_sha256,'acceptance_sha256':proposal.acceptance_sha256}
        commit_payload=trust.verify(record['commit'],purpose='replacement.commit',bindings=commit_bindings,historical=True)
        from .replacement_schema import commits
        completed=db.execute(select(commits).where(commits.c.id==commit_payload['operation_id'],
            commits.c.proposal_id==payload['proposal_id'],commits.c.scope_key==project.key,commits.c.stage=='completed')).mappings().first()
        if not completed:raise ValueError('replacement_commit_not_completed')
    else:
        state = db.execute(select(proposals).where(proposals.c.id==payload['proposal_id'],proposals.c.scope_key==project.key)).mappings().first()
        policy = db.execute(select(activations).where(activations.c.scope_key==project.key)).mappings().first()
        if (not state or state['digest']!=proposal_digest or state['state']!=('claimed' if claimed else 'approved')
                or state['revision']!=payload['revision']+(1 if claimed else 0) or not policy or policy['state']!='active'
                or policy['binding_revision']!=project.binding_revision or policy['policy_version']!=trust.policy_version):
            raise ValueError('replacement_authorization_changed')
        owner=db.scalar(text('SELECT owner_id FROM admin_spaces WHERE id=:space'),{'space':project.space_id})
        if not claimed and owner!=payload['actor_id']: raise ValueError('replacement_owner_changed')
        from .scope import authorize
        authorize(db,actor,project.space_id,project.repository_id,write=True)
    dependencies = [proposal.review.model_dump(),proposal.regression.model_dump(),*[o.source.model_dump() for o in proposal.obligations]]
    if historical:
        from .archive_recovery import journal_path
        dependencies.append({'path':journal_path(root,successor).relative_to(root).as_posix(), 'sha256':journal['journal_sha256']})
    for item in dependencies: evidence_file(root,item)
    if (path.exists() if virtual else path.read_bytes()!=raw): raise ValueError('replacement_proof_changed')
    return {'proof_sha256':hashlib.sha256(raw).hexdigest(),'proof_path':path.relative_to(root).as_posix(),'dependencies':dependencies,
            'virtual':virtual,
            'controlled': {'receipt':certificate, 'bindings':bindings, 'historical':historical,
                'commit':record['commit'], 'commit_bindings':commit_bindings if historical else {},
                'id':payload['proposal_id'], 'revision':payload['revision']+(1 if claimed else 0), 'claimed':claimed}}


def recheck_authority(record):
    context = _authority.get()
    if context is None: raise ValueError('replacement_authority_unavailable')
    db, project, actor, operation_id, fence = context
    trust = load(project.root)
    trust.verify(record['receipt'], purpose='replacement.approve', bindings=record['bindings'], historical=record['historical'] or record.get('claimed',False))
    if record['historical']:
        payload=trust.verify(record['commit'], purpose='replacement.commit', bindings=record['commit_bindings'], historical=True)
        from .replacement_schema import commits
        from sqlalchemy.orm import Session
        with Session(db.get_bind()) as fresh:
            if not fresh.scalar(select(commits.c.id).where(commits.c.id==payload['operation_id'],
                commits.c.proposal_id==record['id'],commits.c.scope_key==project.key,commits.c.stage=='completed')):
                raise ValueError('replacement_commit_not_completed')
    else:
        # An independent read transaction sees a revocation committed during the
        # preceding filesystem scan even on MySQL REPEATABLE READ.
        from sqlalchemy.orm import Session
        with Session(db.get_bind()) as fresh:
            row=fresh.execute(select(proposals).where(proposals.c.id==record['id'])).mappings().first()
            if not row or row['revision']!=record['revision'] or row['state']!=('claimed' if record.get('claimed') else 'approved'):
                raise ValueError('replacement_authorization_changed')
            if record.get('claimed'):
                from .replacement_commit import assert_fence
                assert_fence(fresh,operation_id,fence)
            from .scope import authorize
            current=authorize(fresh,actor,project.space_id,project.repository_id,write=True)
            if current.binding_revision!=project.binding_revision: raise ValueError('replacement_binding_changed')


def recheck_bootstrap(certificate):
    context=_authority.get()
    if context is None:raise ValueError('replacement_authority_unavailable')
    from .bootstrap_successor import recheck
    recheck(certificate,context,load(context[1].root))
