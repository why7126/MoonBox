"""Bounded Issue completion validation, including untouched-object protection."""
import difflib
import hashlib
import re
import yaml
from app.chat.service import ChatError
from app.governance.candidates import frontmatter, without
from app.governance.snapshot import digest
from app.governance.titles import validate_document

REGISTRY='issues/requirements/_registry.yaml'
INDEX='issues/requirements/CHANGELOG.md'
DOCUMENTS=('requirement.md','user-stories.md','business-flow.md','acceptance.md','trace.md')
COMPLETION_REASONS=frozenset({
    'identity','scope','size','document','document_identity','root_cause_status',
    'root_cause_status_conflict','root_cause_evidence','stage','trace_scope',
    'unfinished_lifecycle','lifecycle','knowledge_refs','prototype',
    'prototype_acceptance','registry','registry_ids','other_object',
    'registry_scope','index','document_format',
})


def allowed_paths(base):
    if base.startswith('issues/bugs/'):
        return {f'{base}/{name}' for name in ('bug.md','root-cause.md','workaround.md','acceptance.md','trace.md')} | {'issues/bugs/_registry.yaml','issues/bugs/CHANGELOG.md'}
    return {f'{base}/{name}' for name in (*DOCUMENTS,'prototype/web/context.md','prototype/web/prototype.html')} | {REGISTRY,INDEX}


def validate_completion(before,after,oid,base,action='req-complete'):
    try:
        bug=action=='bug-complete'
        prefix,folder,id_field,primary=('BUG','bugs','bug_id','bug.md') if bug else ('REQ','requirements','requirement_id','requirement.md')
        registry=f'issues/{folder}/_registry.yaml';index=f'issues/{folder}/CHANGELOG.md'
        if not re.fullmatch(rf'{prefix}-\d{{4}}-[a-z0-9-]+',oid) or base!=f'issues/{folder}/plan/{oid}':raise ValueError('identity')
        changed={p for p in before.keys()|after.keys() if before.get(p)!=after.get(p)}
        if not changed<=allowed_paths(base) or any(not after.get(p,b'').strip() for p in changed):raise ValueError('scope')
        if sum(len(after[p]) for p in changed)>2*1024*1024:raise ValueError('size')
        docs={}
        for name in (('bug.md','root-cause.md','workaround.md','acceptance.md','trace.md') if bug else DOCUMENTS):
            body=after[f'{base}/{name}'];data,text=frontmatter(body)
            if validate_document(body.decode()) or len(text.strip())<20:raise ValueError('document')
            if data.get(id_field)!=oid:raise ValueError('document_identity')
            docs[name]=data
        old,_=frontmatter(before[f'{base}/trace.md']);new=docs['trace.md']
        stage='pending_review'
        if bug:
            root_status=docs['root-cause.md'].get('status')
            if root_status not in ('unknown','hypothesis','probable','confirmed'):raise ValueError('root_cause_status')
            stage='pending_review' if root_status=='confirmed' else 'enriching'
            root_text=after[f'{base}/root-cause.md'].decode()
            status_section=re.search(r'^##\s+根因状态\s*\n(.*?)(?=^##\s|\Z)',root_text,re.M|re.S)
            if status_section:
                declared=re.search(r'(?im)^\s*(?:status|root_cause_status|状态)\s*[:：]\s*`?([a-z_]+)',status_section[1])
                if declared and declared[1]!=root_status:raise ValueError('root_cause_status_conflict')
            section=re.search(r'^##\s+证据链\s*\n(.*?)(?=^##\s|\Z)',root_text,re.M|re.S)
            evidence=False
            for line in section[1].splitlines() if section else []:
                cells=[cell.strip(' `') for cell in line.strip().strip('|').split('|')]
                if line.strip().startswith('|') and len(cells)>=4 and re.match(r'^E\d+',cells[0],re.I) and all(cells[1:4]):evidence=True
                if re.match(r'^\s*[-*]\s+(?:E\d+|证据|evidence)\b.+\S',line,re.I):evidence=True
            if stage=='pending_review' and not evidence:
                raise ValueError('root_cause_evidence')
        if old.get('status') not in (('draft','enriching') if changed else (stage,)) or new.get('status')!=stage or docs[primary].get('status')!=stage:raise ValueError('stage')
        mutable={'status','updated_at','lifecycle','knowledge_base_refs','prototype_refs','prototype_gate','cross_cutting_tags','product_data_collection_observability'}
        if without(old,mutable)!=without(new,mutable):raise ValueError('trace_scope')
        old_life=old.get('lifecycle',{});new_life=new.get('lifecycle',{})
        if stage=='enriching':
            if old_life!=new_life:raise ValueError('unfinished_lifecycle')
        elif without(old_life,{'completed'})!=without(new_life,{'completed'}) or not new_life.get('completed'):raise ValueError('lifecycle')
        if not bug and not isinstance(new.get('knowledge_base_refs'),list):raise ValueError('knowledge_refs')
        if not bug and any(p.startswith(base+'/prototype/') for p in after):
            context=after[f'{base}/prototype/web/context.md'];html=after[f'{base}/prototype/web/prototype.html']
            if not html.strip() or validate_document(context.decode()) or new.get('prototype_gate',{}).get('decomposition')!='done':raise ValueError('prototype')
            if not new.get('prototype_refs') or b'AC-PROTOTYPE' not in after[f'{base}/acceptance.md']:raise ValueError('prototype_acceptance')
        a=yaml.safe_load(before[registry]);b=yaml.safe_load(after[registry])
        if without(a,{'entries','updated_at'})!=without(b,{'entries','updated_at'}):raise ValueError('registry')
        if [e['id'] for e in a['entries']]!=[e['id'] for e in b['entries']]:raise ValueError('registry_ids')
        for old_entry,new_entry in zip(a['entries'],b['entries']):
            if old_entry['id']!=oid:
                if old_entry!=new_entry:raise ValueError('other_object')
            elif new_entry.get('status')!=stage or new_entry.get('title')!=docs[primary].get('title') or without(old_entry,{'status','updated_at'})!=without(new_entry,{'status','updated_at'}):raise ValueError('registry_scope')
        def index_parts(body):
            meta,text=frontmatter(body);rows=[];rest=[]
            for line in text.splitlines():
                (rows if re.match(r'^\|\s*'+re.escape(oid)+r'\s*\|',line) else rest).append(line)
            return without(meta,{'updated_at'}),rest,rows
        a,b=index_parts(before[index]),index_parts(after[index])
        if a[:2]!=b[:2] or len(a[2])!=1 or len(b[2])!=1 or stage not in [cell.strip() for cell in b[2][0].split('|')] or base not in b[2][0]:raise ValueError('index')
        files=[]
        for p in sorted(changed):
            patch=''.join(difflib.unified_diff(before.get(p,b'').decode().splitlines(True),after[p].decode().splitlines(True),fromfile=p,tofile=p))
            files.append({'path':p,'before_sha256':hashlib.sha256(before[p]).hexdigest() if p in before else None,'after_sha256':hashlib.sha256(after[p]).hexdigest(),'diff':patch})
        return {'files':files,'manifest_hash':digest({p:after[p] for p in changed})}
    except (ValueError,KeyError,TypeError,UnicodeError,yaml.YAMLError) as error:
        # Only our fixed rule identifiers may leave the validator; parser errors and
        # document content must never be copied into product diagnostics.
        reason=str(error) if type(error) is ValueError and str(error) in COMPLETION_REASONS else 'document_format'
        raise ChatError(2604,'完善成果未通过文件范围、身份、就绪或状态校验，已保留成果',409,
                        kind='governance_validation_failed',details={'reason':reason}) from None
