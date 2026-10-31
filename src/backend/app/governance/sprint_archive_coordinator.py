"""Close an already fully archived Sprint under the common project fence."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import yaml
from sqlalchemy import select
from . import scope
from .replacement_schema import archive_operations as operations,activations
from .replacement_trust import load
from .replacement_proof import digest
from .replacement_permissions import authorize_write
from .archive_coordinator import acquire,assert_fence,checkpoint,STAGES
from .controlled_successor import authority
from .replacement_executor import ArchiveDriver
from .sprint_object import require_final,resolve
from .archive_recovery import tree_hash
from .writer import project_lock


def fingerprint(root,item,*,include_history=True):
    """Bind every manual byte; only lifecycle fields and generated notes vary."""
    folder=root/item['path'];values={}
    for path in sorted(folder.rglob('*')):
        if path.is_symlink():raise ValueError('unsafe_sprint_input')
        if not path.is_file():continue
        if path.stat().st_size>1024*1024:raise ValueError('sprint_input_too_large')
        rel=path.relative_to(folder).as_posix();raw=path.read_bytes()
        if rel=='sprint.yaml':
            data=yaml.safe_load(raw)
            for key in ('status','lifecycle_stage','updated_at','archived_at'):data.pop(key,None)
            raw=json.dumps(data,sort_keys=True,ensure_ascii=False,default=str).encode()
        elif rel in {'sprint.md','acceptance-report.md','release-note.md'}:
            body=raw.decode();data={}
            if body.startswith('---\n'):
                _,meta,body=body.split('---',2);data=yaml.safe_load(meta)
                if not isinstance(data,dict):raise ValueError('invalid_sprint_document')
            # Workflow Sync can add document timestamps to legacy documents.
            # Signatures, scope and every non-generated field remain bound.
            for field in ('note','created_at','updated_at'):data.pop(field,None)
            raw=json.dumps(data,sort_keys=True,ensure_ascii=False,default=str).encode()+body.lstrip('\n').encode()
        values[rel]=hashlib.sha256(raw).hexdigest()
    value={'files':values}
    if include_history:
        value.update(specs=tree_hash(root/'openspec/specs'),archives=tree_hash(root/'openspec/archive'))
    return digest(value)


def update_plan(path):
    original=path.read_bytes();plan=yaml.safe_load(original)
    plan.update(status='completed',lifecycle_stage='archive')
    data=yaml.safe_dump(plan,allow_unicode=True,sort_keys=False).encode()
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as stream:
        tmp=Path(stream.name);stream.write(data);stream.flush();os.fsync(stream.fileno())
    try:
        if path.read_bytes()!=original:raise ValueError('sprint_inputs_changed')
        os.replace(tmp,path)
    finally:tmp.unlink(missing_ok=True)


def execute(db,*,actor,space_id,repository_id,sprint,operation_id,driver_type=ArchiveDriver):
    project=scope.authorize(db,actor,space_id,repository_id,write=True)
    with project_lock(project):
        db.commit();project=scope.authorize(db,actor,space_id,repository_id,write=True)
        # Sprint close keeps its independent readiness and signing gates; it
        # no longer depends on the retired per-project policy installation.
        row=db.execute(select(operations).where(operations.c.scope_key==project.key,operations.c.change_id==sprint)).mappings().first()
        if row and (row['id']!=operation_id or row['actor_id']!=actor or row['binding_revision']!=project.binding_revision):
            raise ValueError('original_operation_required')
        from .archive_tools import selected, check_binding
        package = selected()
        if row:
            check_binding(json.loads(row['manifest']), package)
        with authority(db,project,actor):
            item=require_final(project.root,sprint,allow_closing=bool(row))
            current=fingerprint(project.root,item)
            if row:
                manifest=json.loads(row['manifest'])
                if row['stage']=='completed':
                    if manifest.get('closure_fingerprint')!=fingerprint(project.root,item,include_history=False):
                        raise ValueError('sprint_inputs_changed')
                    if item['path']!='iterations/archive/'+sprint or item['plan'].get('lifecycle_stage')!='archive':
                        raise ValueError('sprint_result_unknown')
                    return {'operation_id':operation_id,'stage':'completed','replayed':True}
                if manifest.get('release')=='builtin-v2' and manifest.get('policy')=='builtin-v2':
                    policy_matches=True
                else:
                    trust=load(project.root)
                    policy_matches=manifest.get('release')==trust.release_digest and manifest.get('policy')==trust.policy_version
                if manifest.get('fingerprint')!=current or not policy_matches:
                    raise ValueError('sprint_inputs_changed')
            else:
                manifest={'kind':'sprint_close','fingerprint':current,'closure_fingerprint':fingerprint(project.root,item,include_history=False),
                    'release':'builtin-v2','policy':'builtin-v2',
                    'archive_tool_digest': package.digest if package else None}
            driver=driver_type(project)
            for name,args in (('validate-sprint-archive-readiness.py',['--sprint',sprint]),
                    ('validate-env-ignore-policy.py',[]),('check-sprint-close-stale-scan.py',['--sprint',sprint])):
                driver._run([sys.executable,str(driver.scripts/name),*args],project.root)
        fence=acquire(db,project,actor,sprint,operation_id,manifest,row)
        with authority(db,project,actor,operation_id,fence):
            authorize_write(db,project,actor)
            item=require_final(project.root,sprint,allow_closing=True)
            if fingerprint(project.root,item)!=current:raise ValueError('sprint_inputs_changed')
            active=project.root/'iterations/change'/sprint;archived=project.root/'iterations/archive'/sprint
            assert_fence(db,project,operation_id,fence)
            if active.exists():
                update_plan(active/'sprint.yaml')
                if fingerprint(project.root,resolve(project.root,sprint))!=current:raise ValueError('sprint_inputs_changed')
                archived.parent.mkdir(parents=True,exist_ok=True)
                if archived.exists() or archived.is_symlink() or archived.parent.is_symlink():raise ValueError('sprint_identity_ambiguous')
                assert_fence(db,project,operation_id,fence);os.rename(active,archived)
            for stage in ('merge_verified','move_verified'):
                row=assert_fence(db,project,operation_id,fence)
                if STAGES.index(row['stage'])<STAGES.index(stage):checkpoint(db,project,operation_id,fence,stage)
            row=assert_fence(db,project,operation_id,fence)
            if row['stage']=='move_verified':
                authorize_write(db,project,actor)
                driver._run([sys.executable,str(driver.scripts/'sync-workflow-status.py'),'--event','sprint.archive','--sprint',sprint],project.root)
                if fingerprint(project.root,resolve(project.root,sprint))!=current:raise ValueError('sprint_inputs_changed')
                checkpoint(db,project,operation_id,fence,'synced')
            require_final(project.root,sprint,allow_closing=True)
            item=resolve(project.root,sprint)
            if (item['path']!='iterations/archive/'+sprint or item['plan'].get('status')!='completed'
                    or item['plan'].get('lifecycle_stage')!='archive' or fingerprint(project.root,item)!=current):
                raise ValueError('sprint_result_unknown')
            authorize_write(db,project,actor);checkpoint(db,project,operation_id,fence,'completed')
        return {'operation_id':operation_id,'stage':'completed','replayed':False}
