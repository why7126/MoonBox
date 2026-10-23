"""Adopt only attributable completion changes without resetting an isolated workspace."""
import hashlib
import logging
from pathlib import Path
from sqlalchemy import insert, select
from app.chat import service
from app.chat.schema import governance_candidates as candidates, turns
from app.chat.settings import repository_binding
from app.chat.workspace import git, snapshot, trusted_directory
from app.governance import store
from app.governance.requirement_completion import allowed_paths


def checkpoint_applied_completions(factory, resolve_workspace):
    """Worker-only baseline acknowledgement, serialized against new sends."""
    from sqlalchemy import update
    from app.chat.schema import conversations
    from app.chat.workspace import WorkspaceError
    from app.governance.preparation import _checkpoint_applied_workspace
    with factory() as db:
        rows=list(db.execute(select(candidates).where(candidates.c.action.in_(('req-complete','bug-complete','req-review','bug-review')),
            candidates.c.state=='applied').order_by(candidates.c.updated_at.desc()).limit(50)).mappings())
    for row in rows:
        with factory() as db:
            try:
                baseline=store.read(row['id'],'baseline')
                if baseline.get('workspace_checkpoint_commit') or baseline.get('workspace_mode')=='source':
                    continue
                parent=db.execute(select(conversations).where(conversations.c.id==row['conversation_id'])).mappings().one()
                if parent['active_turn_id'] or parent['deleted_at']:
                    continue
                locked=db.execute(update(conversations).where(conversations.c.id==parent['id'],
                    conversations.c.active_turn_id.is_(None),conversations.c.generation==parent['generation'])
                    .values(updated_at=parent['updated_at'])).rowcount
                if not locked:
                    db.rollback();continue
                _,workspace=resolve_workspace(parent['id'])
                _checkpoint_applied_workspace(db,parent,workspace)
                baseline['workspace_checkpoint_commit']=git(workspace,'rev-parse','HEAD').decode().strip()
                store.write(row['id'],'baseline',baseline)
                db.commit()
            except (service.ChatError,WorkspaceError,OSError,ValueError) as error:
                db.rollback()
                logging.getLogger(__name__).warning('chat.workspace_checkpoint_blocked candidate_id=%s exception_type=%s',row['id'],type(error).__name__)


def recovery_manifest(current, files, base, action='req-complete'):
    manifest={p:{k:v for k,v in item.items() if k in ('kind','sha256','executable')} for p,item in current['files'].items()}
    for p in command_paths(base, files, action):
        if p in files:
            manifest[p]={'kind':'file','sha256':hashlib.sha256(files[p]).hexdigest(),'executable':manifest.get(p,{}).get('executable',False)}
        else:manifest.pop(p,None)
    return manifest


def command_paths(base, files, action):
    if action in ('req-review','bug-review'):
        from app.governance.review import allowed_paths as review_paths
        return review_paths(base, files)
    return allowed_paths(base)


def prepare_completion(db,actor,parent,project,item,baseline,client_id,action='req-complete'):
    from app.governance.preparation import _candidate_id, _command_baseline_id, _write_command
    oid=item['id'];folder='bugs' if action.startswith('bug-') else 'requirements';base=f'issues/{folder}/plan/{oid}'
    binding=repository_binding(parent['repository_id'],parent['space_id'])
    workspace=(Path(binding['workspace_root'])/parent['id']) if binding.get('workspace_root') and binding.get('workspace_mode')!='source' else None
    record={'files':{p:b.decode() for p,b in baseline.files.items()},'base_path':base,
            'binding_revision':project.binding_revision}
    if workspace is not None and workspace.exists():
        workspace=trusted_directory(workspace)
    applied=False
    if workspace is not None and workspace.exists() and git(workspace,'status','--porcelain').strip():
        from app.governance.preparation import _applied_workspace_result
        try:
            _applied_workspace_result(db,parent,workspace)
            applied=True
        except service.ChatError:
            pass
    if not applied and workspace is not None and workspace.exists() and git(workspace,'status','--porcelain').strip():
        dirty=set(git(workspace,'diff','--name-only','-z','HEAD').decode().strip('\0').split('\0')) | set(git(workspace,'ls-files','--others','--exclude-standard','-z').decode().strip('\0').split('\0'))
        dirty.discard('')
        if not dirty<=command_paths(base,baseline.files,action):
            raise service.ChatError(2604,'工作区包含其他文件的未应用修改，不能自动续接',409,kind='workspace_unapplied_changes')
        prior=None
        for turn in db.execute(select(turns).where(turns.c.conversation_id==parent['id'],turns.c.executor_turn_id.is_not(None),turns.c.status.in_(('completed','stopped','failed'))).order_by(turns.c.created_at.desc()).limit(50)).mappings():
            if _write_command(turn['prompt'])!=(action,oid):continue
            try: candidate=store.read(_command_baseline_id(parent['id'],turn['client_request_id']),'baseline')
            except (OSError,service.ChatError):continue
            if candidate.get('object_id')==oid:
                prior=candidate;break
        if prior is None:
            raise service.ChatError(2604,'缺少上轮原始基准，成果保留，不能自动续接',409,kind='workspace_unapplied_changes')
        for p in command_paths(base,baseline.files,action):
            old=prior['files'].get(p)
            if (old.encode() if old is not None else None)!=baseline.files.get(p):
                raise service.ChatError(2606,'目标事实源自上轮后已变化，不能自动覆盖',409,kind='workspace_fact_source_stale')
        current=snapshot(workspace)
        record.update(recovery_hash=current['hash'],workspace_manifest=recovery_manifest(current,baseline.files,base,action))
    row={**_candidate_id(actor,project.key,oid,action,client_id),'actor_id':actor,'space_id':parent['space_id'],
        'repository_id':parent['repository_id'],'scope_key':project.key,'conversation_id':parent['id'],
        'object_id':oid,'action':action,'binding_revision':project.binding_revision,
        'baseline_hash':baseline.revision,'state':'prepared','revision':1}
    if db.scalar(select(candidates.c.id).where(candidates.c.id==row['id'])):return
    store.write(row['id'],'baseline',record)
    db.execute(insert(candidates).values(**row))
    db.flush()
