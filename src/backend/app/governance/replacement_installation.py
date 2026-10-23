"""Read-only installation review bundles; no authorization or archive writes."""
from pathlib import Path
import hashlib
import json
from uuid import uuid4
from .replacement_bootstrap import Installation
from .replacement_proof import PROTECTED, digest
from .replacement_activation import inputs
from .replacement_inputs import replacement_delivery_hash
from .compatible_successor import acceptance_binding
from .archive_recovery import tree_hash, delta_operations, requirement_blocks, archive_paths
from .replacement_executor import ArchiveDriver
from .acceptance_evidence import readiness

KEY = ('governance-command-durable-recovery', '归档连续证明的条文冲突范围')


def content_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()


def describe(project, manifest):
    """Display only the bound requirement and sanitized acceptance summary."""
    folder = project.root/'openspec/changes'/manifest.mechanism_change
    archived = archive_paths(project.root, manifest.mechanism_change)
    if not folder.is_dir():
        if len(archived) != 1: raise ValueError('bootstrap_history_changed')
        folder = archived[0]
    operations = delta_operations(folder)
    rows=[]
    for transition in manifest.transitions:
        key=(transition.capability, transition.requirement)
        after=operations.get(key, ('',''))[1]
        if content_hash(after)!=transition.after_sha256: raise ValueError('bootstrap_inputs_changed')
        paths=[project.root/'openspec/specs'/key[0]/'spec.md']
        paths += [p/'specs'/key[0]/'spec.md' for p in (project.root/'openspec/archive').glob('????-??-??-*')]
        before=None
        for path in paths:
            if path.is_file() and not path.is_symlink() and path.stat().st_size <= 1024*1024:
                block=requirement_blocks(path.read_text()).get(key[1])
                if block and content_hash(block)==transition.before_sha256:
                    before=block;break
        rows.append({**transition.model_dump(),'before':before,'after':after})
    return {'manifest':manifest.model_dump(),'manifest_hash':digest(manifest.model_dump()),
            'transitions':rows,'protected_obligations':sorted(PROTECTED),
            'evidence':{'acceptance_digest':manifest.acceptance_digest,'delivery_digest':manifest.delivery_digest,
                        'delta_digest':manifest.delta_digest},
            'archive_identity':folder.name if folder in archived else None}


def build(project, change, trust, *, driver_type=ArchiveDriver):
    folder=project.root/'openspec/changes'/change
    if not folder.is_dir() or archive_paths(project.root,change):raise ValueError('bootstrap_candidate_missing')
    before_tree=tree_hash(project.root/'openspec/specs');delivery=replacement_delivery_hash(folder)
    evidence=readiness(project.root,change,source_root=project.source_root)
    if evidence.get('status')!='ready':raise ValueError('bootstrap_acceptance_not_ready')
    operations=delta_operations(folder)
    if operations.get(KEY, ('',))[0]!='MODIFIED' or any(kind not in {'ADDED','MODIFIED'} or kind=='MODIFIED' and key!=KEY for key,(kind,_) in operations.items()):
        raise ValueError('unsupported_policy_installation')
    before=requirement_blocks((project.root/'openspec/specs'/KEY[0]/'spec.md').read_text()).get(KEY[1])
    if not before:raise ValueError('bootstrap_baseline_missing')
    from . import replacement_bootstrap
    driver=driver_type(project)
    driver.validate_static(change)
    expected=driver.preview(change)  # temporary directory only; never classify/write a journal
    value=Installation(schema_version=1,kind='policy_installation',project_id=project.key,
        binding_revision=project.binding_revision,mechanism_change=change,from_policy='legacy-v1',to_policy=trust.policy_version,
        release_digest=trust.release_digest,verifier_digest=hashlib.sha256(Path(replacement_bootstrap.__file__).read_bytes()).hexdigest(),
        delta_digest=tree_hash(folder/'specs'),acceptance_digest=acceptance_binding(project.root,folder,source_root=project.source_root),
        delivery_digest=delivery,baseline_digest=before_tree,expected_digest=expected,
        protected_obligations=sorted(PROTECTED),operation_id='install-'+uuid4().hex,
        transitions=[{'capability':KEY[0],'requirement':KEY[1],'before_sha256':content_hash(before),'after_sha256':content_hash(operations[KEY][1])}])
    inputs(project,value,trust)
    return describe(project,value)


def validate_bundle(bundle):
    """Offline reviewer rejects detached text, altered digests, or unknown fields."""
    if not isinstance(bundle,dict) or set(bundle)!={'manifest','manifest_hash','transitions','protected_obligations','evidence','archive_identity'}:
        raise ValueError('invalid_installation_bundle')
    manifest=Installation.model_validate(bundle['manifest'])
    if (bundle['manifest_hash']!=digest(manifest.model_dump()) or bundle['protected_obligations']!=sorted(PROTECTED)
            or set(manifest.protected_obligations)!=PROTECTED or bundle['archive_identity'] is not None):
        raise ValueError('invalid_installation_bundle')
    if bundle['evidence']!={'acceptance_digest':manifest.acceptance_digest,'delivery_digest':manifest.delivery_digest,'delta_digest':manifest.delta_digest}:
        raise ValueError('invalid_installation_bundle')
    if len(bundle['transitions'])!=len(manifest.transitions):raise ValueError('invalid_installation_bundle')
    for row,transition in zip(bundle['transitions'],manifest.transitions):
        if set(row)!={'capability','requirement','before_sha256','after_sha256','before','after'} or any(row[k]!=v for k,v in transition.model_dump().items()):raise ValueError('invalid_installation_bundle')
        if not isinstance(row['before'],str) or not isinstance(row['after'],str) or content_hash(row['before'])!=transition.before_sha256 or content_hash(row['after'])!=transition.after_sha256:
            raise ValueError('invalid_installation_bundle')
    return manifest
