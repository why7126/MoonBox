"""Validate generated governance candidates; model output cannot expand write sets."""
from app.governance.titles import validate_document
import difflib
import hashlib
import re
import yaml
from app.chat.service import ChatError
from app.governance.snapshot import digest


def frontmatter(body):
    value=body.decode('utf-8')
    parts=value.split('---',2)
    if not value.startswith('---\n') or len(parts)!=3: raise ValueError('frontmatter')
    data=yaml.safe_load(parts[1])
    if not isinstance(data,dict): raise ValueError('frontmatter')
    return data,parts[2]


def without(data, fields):
    return {key:value for key,value in data.items() if key not in fields}


def action_spec(action):
    if action in ('req-review', 'bug-review'):
        spec = dict(action_spec('bug-generate' if action == 'bug-review' else 'req-generate'))
        spec.update(skill=action, title='发起评审', command='/'+action,
            prompt='/'+action+' {object_id}\n遵循评审技能，仅修改目标对象评审记录、主文档、trace及注册表目标条目和索引目标行。通过时迁移目标完整目录到review，保留所有子文档，仅修正迁移路径引用；不得修改其他对象、Sprint、OpenSpec或源码。先dry-run再同步，校验实际差异。AI Usage与治理日志仅回复，不新增文件。模型执行完成不代表项目事实源已应用，最终以后端应用结果为准。')
        return spec
    if action == 'bug-complete':
        spec = dict(action_spec('bug-generate'))
        spec.update(skill=action,title='完善缺陷',command='/bug-complete',
            prompt='/bug-complete {object_id}\n在当前 /work 目标缺陷目录保存正式治理草稿，不要只写 /tmp。保留既有成果，仅更新目标 bug.md、root-cause.md、workaround.md、acceptance.md、trace.md、BUG 注册表目标条目及索引目标行。所有 Markdown 使用中文业务 title 与一致一级标题。根因 unknown/hypothesis/probable 时，保存补证清单、草稿和 enriching 状态，lifecycle.completed 保持原值，不调用完成态同步强推待评审。仅 confirmed 且证据链有效时执行 dry-run、完成校验及 Workflow Sync 到 pending_review。bug.md、trace、注册表与索引状态必须一致。禁止修改其他对象、评审、Sprint、OpenSpec、源码。用真实文件差异验证成果；AI Usage 与治理日志仅回复，不新增文件。')
        return spec
    if action == 'req-complete':
        spec = dict(action_spec('req-generate'))
        spec.update(skill='req-complete',title='完善需求',command='/req-complete',
            prompt='/req-complete {object_id}\n保留当前工作区已生成成果，只补齐剩余校验。遵循 req-complete 技能与门禁；只更新目标需求的 requirement.md、user-stories.md、business-flow.md、acceptance.md、trace.md、prototype/web/context.md、prototype/web/prototype.html，以及注册表目标条目和当前索引目标行。不得改动其他对象、评审、Sprint 或 OpenSpec。先执行同步 dry-run，按实际门禁结果同步状态；无法通过时保留成果明确汇报，不伪造完成。AI Usage与治理复盘仅回复，不新增日志文件。')
        return spec
    specs={
        'req-generate':{
            'prefix':'REQ-','folder':'issues/requirements','doc':'requirement.md','id_field':'requirement_id',
            'registry':'issues/requirements/_registry.yaml','index':'issues/requirements/CHANGELOG.md',
            'skill':'req-generate','title':'生成需求','kind_cn':'需求','command':'/req-generate',
            'prompt':'/req-generate {object_id}\n所有生成Markdown必须有中文业务title与一致一级标题，辅助文档标题结合业务主题及用途；requirement.md业务title同步注册表，禁止使用纯文档类别标题。本次仅生成目标 requirement.md，并同步目标 trace、注册表条目与当前态索引行。请保留其他文件与对象；治理成果以实际差异校验，禁止推进评审或 Sprint。四个文件之外的 AI Usage 与治理记录仅在回复汇报，不落盘；同步前先检查 dry-run，只更新目标条目。控制读取范围，不打印整份注册表、索引或历史归档。'
        },
        'bug-generate':{
            'prefix':'BUG-','folder':'issues/bugs','doc':'bug.md','id_field':'bug_id',
            'registry':'issues/bugs/_registry.yaml','index':'issues/bugs/CHANGELOG.md',
            'skill':'bug-generate','title':'生成 Bug','kind_cn':'缺陷','command':'/bug-generate',
            'prompt':'/bug-generate {object_id}\n所有生成Markdown必须有中文业务title与一致一级标题，辅助文档标题结合业务主题及用途；bug.md业务title同步注册表，禁止使用纯文档类别标题。本次仅生成目标 bug.md，并同步目标 trace、BUG注册表条目与当前态索引行。请保留其他文件与对象；治理成果以实际差异校验，禁止推进完善、评审、Sprint 或 OpenSpec。四个文件之外的 AI Usage 与治理记录仅在回复汇报，不落盘；同步前先检查 dry-run，只更新目标条目。控制读取范围，不打印整份注册表、索引或历史归档。'
        },
    }
    try:return specs[action]
    except KeyError:raise ChatError(2604,'该治理命令尚未接入产品写入链路',422) from None


def display_prompt(action, object_id):
    spec=action_spec(action)
    return f"{spec['command']} {object_id}"


def execution_prompt(action, object_id):
    return action_spec(action)['prompt'].format(object_id=object_id)


def validate(before, after, object_id, base_path, action='req-generate'):
    """Both maps are complete snapshots, not caller-selected differences."""
    if action in ('req-review','bug-review'):
        from app.governance.review import validate_review
        return validate_review(before,after,object_id,base_path,action)
    if action in ('req-complete','bug-complete'):
        from app.governance.requirement_completion import validate_completion
        return validate_completion(before,after,object_id,base_path,action)
    spec=action_spec(action)
    try:
        if not re.fullmatch(rf"{spec['prefix']}\d{{4}}-[a-z0-9-]+",object_id): raise ValueError('id')
        if base_path.strip('/') != f"{spec['folder']}/plan/{object_id}": raise ValueError('path')
        base_path=base_path.rstrip('/')
        document=f"{base_path}/{spec['doc']}";trace=f'{base_path}/trace.md'
        registry=spec['registry'];index=spec['index']
        allowed={document,trace,registry,index}
        changed={name for name in before.keys()|after.keys() if before.get(name)!=after.get(name)}
        if (changed and changed != allowed) or any(not after.get(name,b'').strip() for name in allowed): raise ValueError('write_set')
        if sum(len(after[name]) for name in allowed)>512*1024: raise ValueError('size')
        for name in (document, trace):
            if validate_document(after[name].decode('utf-8')): raise ValueError('document_title')
        prior,_=frontmatter(before[trace]);following,_=frontmatter(after[trace]);doc,body=frontmatter(after[document])
        allowed_prior = ('captured', 'exploring') if changed and action == 'req-generate' else ('captured',) if changed else ('draft',)
        if prior.get('status') not in allowed_prior or following.get('status')!='draft': raise ValueError('stage')
        if doc.get(spec['id_field'])!=object_id or doc.get('status')!='draft' or len(body.strip())<20: raise ValueError('document')
        if following.get(spec['id_field'])!=object_id: raise ValueError('trace_id')
        if without(prior,{'status','updated_at','lifecycle','title'})!=without(following,{'status','updated_at','lifecycle','title'}): raise ValueError('trace_scope')
        old_lifecycle=prior.get('lifecycle',{});new_lifecycle=following.get('lifecycle',{})
        if not isinstance(old_lifecycle,dict) or not isinstance(new_lifecycle,dict): raise ValueError('lifecycle')
        if without(old_lifecycle,{'generated'})!=without(new_lifecycle,{'generated'}) or not new_lifecycle.get('generated'): raise ValueError('lifecycle')
        old_registry=yaml.safe_load(before[registry]);new_registry=yaml.safe_load(after[registry])
        if without(old_registry,{'entries','updated_at'})!=without(new_registry,{'entries','updated_at'}): raise ValueError('registry_header')
        old_entries=old_registry['entries'];new_entries=new_registry['entries']
        if [e['id'] for e in old_entries]!=[e['id'] for e in new_entries]: raise ValueError('registry_identity')
        for old,new in zip(old_entries,new_entries):
            if old['id']!=object_id:
                if old!=new: raise ValueError('other_object')
            elif new.get('status')!='draft' or without(old,{'status','updated_at','title'})!=without(new,{'status','updated_at','title'}): raise ValueError('registry_scope')
        if next(e for e in new_entries if e['id']==object_id).get('title') != doc.get('title'): raise ValueError('registry_title')
        # Preserve every line outside this object's exact table row and the header timestamp.
        def index_parts(content):
            metadata,body=frontmatter(content)
            rows=[];rest=[]
            for line in body.splitlines():
                if re.match(r'^\|\s*'+re.escape(object_id)+r'\s*\|',line): rows.append(line)
                else: rest.append(line)
            return without(metadata,{'updated_at'}),rest,rows
        old_meta,old_rest,old_rows=index_parts(before[index]);new_meta,new_rest,new_rows=index_parts(after[index])
        if old_meta!=new_meta or old_rest!=new_rest or len(old_rows)!=1 or len(new_rows)!=1: raise ValueError('index_scope')
        cells=[cell.strip() for cell in new_rows[0].split('|')]
        if 'draft' not in cells or base_path not in new_rows[0]: raise ValueError('index_stage')
        if action=='bug-generate' and spec['command'].replace('generate','complete') not in new_rows[0]: raise ValueError('index_next_step')
        files=[]
        for name in sorted(changed):
            patch=''.join(difflib.unified_diff(before.get(name,b'').decode().splitlines(True),after[name].decode().splitlines(True),fromfile=name,tofile=name))
            files.append({'path':name,'before_sha256':hashlib.sha256(before[name]).hexdigest() if name in before else None,
                          'after_sha256':hashlib.sha256(after[name]).hexdigest(),'diff':patch})
        if sum(len(f['diff'].encode()) for f in files)>1024*1024: raise ValueError('diff_size')
        return {'files':files,'manifest_hash':digest({name:after[name] for name in allowed})}
    except (ValueError,KeyError,TypeError,UnicodeError,yaml.YAMLError):
        raise ChatError(2604,f"成果不符合 {action} 的对象、状态或文件边界，不能应用",409) from None
