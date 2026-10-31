"""Read-only repository binding; never execute evidence or trust repo approvals."""
import json
from .replacement_proof import Proposal, classify, digest
from .compatible_successor import evidence_file, acceptance_binding
from .archive_recovery import (tree_hash, delta_operations, requirement_blocks,
                               archive_paths, completed_archive, delivery_input_hash)


def validate(project, proposal: Proposal, trust):
    if (proposal.project_id != project.key or proposal.binding_revision != project.binding_revision
            or proposal.policy_version != trust.policy_version):
        raise ValueError('proposal_binding_changed')
    classify(proposal, trust.profiles)
    root = project.root
    folder = root / 'openspec/changes' / proposal.successor
    key = (proposal.capability, proposal.requirement)
    initial = fingerprint(project, proposal)
    if archive_paths(root, proposal.successor) or not folder.is_dir():
        raise ValueError('ambiguous_candidate')
    operations = delta_operations(folder)
    operation = operations.get(key)
    # A replacement is an exact modified requirement, never a rename/removal.
    if not operation or operation[0] != 'MODIFIED' or operation[1] != proposal.after:
        raise ValueError('proposal_delta_mismatch')
    current = requirement_blocks((root / 'openspec/specs' / proposal.capability / 'spec.md').read_text())
    if current.get(proposal.requirement) != proposal.before:
        raise ValueError('proposal_baseline_changed')
    impacted = []
    for candidate in (root / 'openspec/archive').glob('????-??-??-*'):
        cid = candidate.name[11:]
        if key not in delta_operations(candidate):
            continue
        if not completed_archive(candidate, cid) or len(archive_paths(root, cid)) != 1 or (root / 'openspec/changes' / cid).exists():
            raise ValueError('incomplete_archive_chain')
        impacted.append(cid)
    if sorted(impacted) != sorted(proposal.predecessors):
        raise ValueError('incomplete_impact_scope')
    if (proposal.delta_sha256 != tree_hash(folder / 'specs')
            or proposal.delivery_sha256 != replacement_delivery_hash(folder)
            or proposal.acceptance_sha256 != acceptance_binding(root, folder, source_root=project.source_root)):
        raise ValueError('proposal_evidence_changed')
    for obligation in proposal.obligations:
        body = evidence_file(root, obligation.source.model_dump()).decode()
        if obligation.before not in body:
            raise ValueError('protected_obligation_missing')
    required = {'destructive_changes', 'broken_chain', 'concurrent_change', 'protected_obligations', 'exact_mapping'}
    for name, reference in [('review', proposal.review), ('regression', proposal.regression)]:
        evidence = json.loads(evidence_file(root, reference.model_dump()))
        if (evidence.get('status') != 'passed' or evidence.get('proposal_content_sha256') != content_digest(proposal)
                or not required <= set(evidence.get('checks', []))):
            raise ValueError('replacement_evidence_invalid')
        if name == 'review' and (not evidence.get('reviewer') or evidence.get('contradictions') != []):
            raise ValueError('replacement_review_incomplete')
    if fingerprint(project, proposal) != initial:
        raise ValueError('proposal_inputs_changed')
    return initial


def content_digest(proposal):
    # Evidence references excluded to avoid a self-referential hash cycle.
    return digest(proposal.model_dump(exclude={'review', 'regression'}))


def fingerprint(project, proposal):
    import hashlib
    config = {}
    for name in ('config.yaml', 'project.md'):
        path = project.root / 'openspec' / name
        if path.is_symlink() or (path.exists() and path.stat().st_size > 256*1024):
            raise ValueError('unsafe_archive_configuration')
        config[name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
    return digest({'specs': tree_hash(project.root / 'openspec/specs'),
                   'archives': archive_input_tree(project.root / 'openspec/archive'),
                   'candidate': tree_hash(project.root / 'openspec/changes' / proposal.successor),
                   'issues': tree_hash(project.root / 'issues'),
                   'iterations': tree_hash(project.root / 'iterations'), 'configuration': config,
                   'binding': project.binding_revision})


def replacement_delivery_hash(folder):
    """V1 projection preserves first execution, normalizes only archive outputs.

    Unknown files remain bound. Legal lifecycle state is checked independently;
    generated acceptance runs are bound by the separate manifest digest.
    """
    import hashlib
    import yaml
    h=hashlib.sha256(b'replacement-delivery-v1\0')
    if folder.is_symlink(): raise ValueError('unsafe_delivery')
    for path in sorted(folder.rglob('*')):
        if path.is_symlink(): raise ValueError('unsafe_delivery')
        if not path.is_file(): continue
        rel=path.relative_to(folder).as_posix()
        if rel.startswith('evidence/acceptance/'): continue
        raw=path.read_bytes()
        if rel=='trace.md':
            parts=raw.decode().split('---',2)
            if len(parts)!=3 or parts[0].strip(): raise ValueError('invalid_delivery_trace')
            meta=yaml.safe_load(parts[1])
            if meta.get('status') not in {'applied','archived'}: raise ValueError('delivery_not_complete')
            meta=dict(meta);meta['status']='applied';meta.pop('updated_at',None)
            execution=dict(meta.get('execution') or {})
            if execution.get('schema_version')!=1 or not execution.get('started_at') or not execution.get('completed_at'):
                raise ValueError('execution_not_complete')
            execution.pop('last_event',None);meta['execution']=execution
            raw=json.dumps(meta,sort_keys=True,ensure_ascii=False,default=str).encode()
        h.update(rel.encode()+b'\0'+hashlib.sha256(raw).digest())
    return h.hexdigest()


def archive_input_tree(root):
    from .archive_recovery import tree_hash
    if root.is_symlink():
        raise ValueError('unsafe_archive_path')
    if not (root / '.archive-tool-bindings').exists():
        return tree_hash(root)
    import hashlib
    h = hashlib.sha256()
    # Match tree_hash's exact stream while excluding only new tool bindings.
    for path in sorted(root.rglob('*')):
        if path.relative_to(root).parts[0] == '.archive-tool-bindings':
            continue
        if path.is_symlink(): raise ValueError('unsafe_archive_path')
        if path.is_file():
            h.update(path.relative_to(root).as_posix().encode() + b'\0' + hashlib.sha256(path.read_bytes()).digest())
    return h.hexdigest()
