"""Pure req-generate validation; model output cannot expand the allowed write set."""
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


def validate(before, after, object_id, base_path):
    """Both maps are complete snapshots, not caller-selected differences."""
    try:
        if not re.fullmatch(r'REQ-\d{4}-[a-z0-9-]+',object_id): raise ValueError('id')
        if base_path.strip('/') != f'issues/requirements/plan/{object_id}': raise ValueError('path')
        base_path=base_path.rstrip('/')
        prd=f'{base_path}/requirement.md';trace=f'{base_path}/trace.md'
        registry='issues/requirements/_registry.yaml';index='issues/requirements/CHANGELOG.md'
        allowed={prd,trace,registry,index}
        changed={name for name in before.keys()|after.keys() if before.get(name)!=after.get(name)}
        if changed != allowed or any(not after.get(name,b'').strip() for name in allowed): raise ValueError('write_set')
        if sum(len(after[name]) for name in allowed)>512*1024: raise ValueError('size')
        prior,_=frontmatter(before[trace]);following,_=frontmatter(after[trace]);doc,body=frontmatter(after[prd])
        if prior.get('status')!='captured' or following.get('status')!='draft': raise ValueError('stage')
        if doc.get('requirement_id')!=object_id or doc.get('status')!='draft' or len(body.strip())<20: raise ValueError('prd')
        if following.get('requirement_id')!=object_id: raise ValueError('trace_id')
        if without(prior,{'status','updated_at','lifecycle'})!=without(following,{'status','updated_at','lifecycle'}): raise ValueError('trace_scope')
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
            elif new.get('status')!='draft' or without(old,{'status','updated_at'})!=without(new,{'status','updated_at'}): raise ValueError('registry_scope')
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
        files=[]
        for name in sorted(allowed):
            patch=''.join(difflib.unified_diff(before.get(name,b'').decode().splitlines(True),after[name].decode().splitlines(True),fromfile=name,tofile=name))
            files.append({'path':name,'before_sha256':hashlib.sha256(before[name]).hexdigest() if name in before else None,
                          'after_sha256':hashlib.sha256(after[name]).hexdigest(),'diff':patch})
        if sum(len(f['diff'].encode()) for f in files)>1024*1024: raise ValueError('diff_size')
        return {'files':files,'manifest_hash':digest({name:after[name] for name in allowed})}
    except (ValueError,KeyError,TypeError,UnicodeError,yaml.YAMLError):
        raise ChatError(2604,'成果不符合 req-generate 的对象、状态或文件边界，不能应用',409) from None
