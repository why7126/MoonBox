"""Prepare a fresh personal session without sending a model prompt."""
import hashlib
from sqlalchemy import insert, select, update
from app.chat import service, relations
from app.chat.schema import governance_candidates as candidates, turns, conversations
from app.chat.workspace import git, snapshot as code_snapshot
from app.governance import scope, store
from app.governance.reader import ProjectReader
from app.governance.snapshot import stable
from app.governance.candidates import frontmatter, validate


def prepare(db,actor,space_id,repository_id,object_id,request_id=None):
    project=scope.authorize(db,actor,space_id,repository_id,write=True)
    store.root()  # Fail before creating a conversation if private storage is unavailable.
    reader=ProjectReader(db,actor,project);baseline=reader.snapshot()
    entry=reader.authorize_object(baseline,object_id)[0];object_id=entry['id'];base=entry['path'].rstrip('/')
    if not object_id.startswith('REQ-') or base!=f'issues/requirements/plan/{object_id}':
        raise service.ChatError(2604,'首版仅支持采集池需求的 req-generate',422)
    # Execution sees the project governance context. Do not copy objects hidden from this actor.
    if any(not scope.visible(db,actor,project,item['id']) for item in reader.entries(baseline)):
        raise service.ChatError(2601,'当前权限不足以准备完整项目治理上下文',403)
    try:
        metadata,_=frontmatter(baseline.files[f'{base}/trace.md'])
        if metadata.get('status')!='captured' or not baseline.files[f'{base}/capture.md'].strip(): raise ValueError()
    except (KeyError,ValueError): raise service.ChatError(2604,'需求需处于采集池且 capture、trace 完整',409)
    parent=service.create_conversation(db,actor,space_id,repository_id,f'{object_id} · 生成需求')
    relations.set_relations(db,actor,parent['id'],object_id,[])
    row={**service.identity(),'actor_id':actor,'space_id':space_id,'repository_id':repository_id,
         'scope_key':project.key,'conversation_id':parent['id'],'object_id':object_id,'action':'req-generate',
         'binding_revision':project.binding_revision,'baseline_hash':baseline.revision,'state':'prepared','revision':1}
    store.write(row['id'],'baseline',{'files':{name:body.decode() for name,body in baseline.files.items()},'base_path':base})
    db.execute(insert(candidates).values(**row))
    from app.governance.observability import trace
    trace(db,row['id'],'prepared',actor=actor,request_id=request_id)
    db.commit()
    return {'preparation_id':row['id'],'conversation_id':parent['id'],'object_id':object_id,
            'prompt':f'/req-generate {object_id}\n所有生成Markdown必须有中文业务title与一致一级标题，辅助文档标题结合业务主题及用途；requirement.md业务title同步注册表，禁止使用纯文档类别标题。本次仅生成目标 requirement.md，并同步目标 trace、注册表条目与当前态索引行。请保留其他文件与对象；治理成果以实际差异校验，禁止推进评审或 Sprint。四个文件之外的 AI Usage 与治理记录仅在回复汇报，不落盘；同步前先检查 dry-run，只更新目标条目。控制读取范围，不打印整份注册表、索引或历史归档。','state':'prepared'}


def for_conversation(db,cid):
    return db.execute(select(candidates).where(candidates.c.conversation_id==cid)).mappings().first()


def check_send(db,actor,parent):
    row=for_conversation(db,parent['id'])
    if not row: return None
    if row['state']!='prepared' or row['prepared_turn_id']:
        raise service.ChatError(2604,'该治理基准已使用，请新建治理会话',409)
    project=scope.authorize(db,actor,row['space_id'],row['repository_id'],write=True)
    if project.binding_revision!=row['binding_revision'] or stable(project.root).revision!=row['baseline_hash']:
        raise service.ChatError(2606,'项目文件已变化，请重新准备治理动作',409)
    return row


def initialize_workspace(db,parent,source,workspace):
    row=for_conversation(db,parent['id'])
    if not row: return
    if row['state']!='prepared': raise service.ChatError(2604,'治理基准不可重复覆盖',409)
    project=scope.authorize(db,parent['owner_id'],row['space_id'],row['repository_id'],write=True)
    baseline=store.read(row['id'],'baseline')
    if stable(project.root).revision!=row['baseline_hash'] or stable(source).revision!=row['baseline_hash']:
        raise service.ChatError(2606,'源仓库与治理目录不一致或基准已过期',409)
    if git(workspace,'status','--porcelain').strip(): raise service.ChatError(2604,'工作区已有修改，拒绝覆盖',409)
    # Explicit control-file whitelist: current working-tree skills and sync implementation,
    # read without following links. Never bring in local env/auth/runtime files.
    from app.chat.relations import _read_file
    control_names=['AGENTS.md','openspec/project.md','.agents/skills/req-generate/SKILL.md',
        '.agents/skills/workflow-sync/SKILL.md','scripts/sync-workflow-status.py','scripts/ai_usage.py',
        'scripts/validate-document-titles.py','src/backend/app/governance/titles.py']
    control_names += [str(path.relative_to(source)) for path in (source/'scripts/workflow_sync').glob('*.py')]
    controls={name:_read_file(source,name) for name in sorted(control_names)}
    if controls!={name:_read_file(source,name) for name in controls}:
        raise service.ChatError(2606,'治理控制文件正在变化，请重新准备',409)
    # New clean workspace only. Overlay the stable uncommitted governance tree.
    for folder in ('issues','iterations','openspec','docs','rules'):
        import shutil
        target=workspace/folder
        if target.exists(): shutil.rmtree(target)
    for relative,body in baseline['files'].items():
        target=workspace/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(body)
    for relative,body in controls.items():
        target=workspace/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(body)
    baseline['control_manifest']={name:hashlib.sha256(body.encode()).hexdigest() for name,body in controls.items()}
    git(workspace,'add','--',*controls.keys())
    git(workspace,'add','--',*[name for name in ('issues','iterations','openspec','docs','rules') if (workspace/name).exists()])
    git(workspace,'-c','user.name=MoonBox','-c','user.email=moonbox@invalid','commit','--allow-empty','-m','治理动作隔离基准')
    before=code_snapshot(workspace)
    baseline['workspace_manifest']={name:{k:v for k,v in item.items() if k in ('kind','sha256','executable')} for name,item in before['files'].items()}
    baseline['code_revision']=git(source,'rev-parse','HEAD').decode().strip()
    store.write(row['id'],'baseline',baseline)
    db.execute(update(candidates).where(candidates.c.id==row['id'],candidates.c.state=='prepared').values(state='running',updated_at=service.now()))
    from app.governance.observability import trace
    trace(db,row['id'],'running',actor=parent['owner_id'])
    db.commit()


def collect(db,parent,turn_id,workspace,terminal):
    row=for_conversation(db,parent['id'])
    if not row: return
    if row['state']!='running': return
    try:
        actual=db.execute(select(turns).where(turns.c.id==turn_id,turns.c.conversation_id==parent['id'])).mappings().one()
        if terminal!='completed' or actual['status']!='completed': raise service.ChatError(2604,'执行未成功，保留普通差异',409)
        baseline=store.read(row['id'],'baseline');before={n:b.encode() for n,b in baseline['files'].items()}
        current=code_snapshot(workspace,text_bytes=1024*1024,max_text_bytes=32*1024*1024)
        old=baseline['workspace_manifest']
        changed={n for n in old.keys()|current['files'].keys() if old.get(n)!={k:v for k,v in current['files'].get(n,{}).items() if k in ('kind','sha256','executable')}}
        after=dict(before)
        for name in changed:
            item=current['files'].get(name)
            if item is None: after.pop(name,None)
            elif item['kind']!='file' or item['text'] is None: raise service.ChatError(2604,'成果包含不可应用文件',409)
            else: after[name]=item['text'].encode()
        result=validate(before,after,row['object_id'],baseline['base_path'])
        # Include non-governance changes in the rejection: never discard a forbidden delta.
        if changed != {file['path'] for file in result['files']}: raise service.ChatError(2604,'成果包含越界改动',409)
        result['after']={f['path']:after[f['path']].decode() for f in result['files']}
        store.write(row['id'],'result',result)
        db.execute(update(candidates).where(candidates.c.id==row['id']).values(turn_id=turn_id,state='pending',manifest_hash=result['manifest_hash'],updated_at=service.now()))
    except (service.ChatError,ValueError,KeyError,OSError):
        db.execute(update(candidates).where(candidates.c.id==row['id']).values(turn_id=turn_id,state='rejected',error_code='invalid_governance_result',updated_at=service.now()))
    from app.governance.observability import trace
    state=db.scalar(select(candidates.c.state).where(candidates.c.id==row['id']))
    trace(db,row['id'],state,actor=parent['owner_id'])
    db.commit()


def list_candidates(db,actor,cid):
    service.conversation(db,actor,cid)
    row=for_conversation(db,cid)
    if not row: return {'items':[]}
    project=scope.authorize(db,actor,row['space_id'],row['repository_id'])
    if not scope.visible(db,actor,project,row['object_id']): raise service.ChatError(2601,'对象不可访问',403)
    public={k:row[k] for k in ('id','object_id','state','manifest_hash','revision','error_code')}
    public['files']=store.read(row['id'],'result')['files'] if row['manifest_hash'] else []
    return {'items':[public]}
