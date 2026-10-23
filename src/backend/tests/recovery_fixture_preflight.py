"""Normalize isolated pending-review fixtures and validate an actual sync preview.

Never call against the working repository or a live sample with an active turn.
"""
from pathlib import Path
import shutil, subprocess, sys, tempfile, os
import yaml
from app.governance.snapshot import stable, ROOTS
from app.governance.review import validate_review


def prepare(root, oid):
    root=Path(root).resolve()
    if not str(root).startswith('/private/tmp/moonbox-'):
        raise ValueError('isolated fixture required')
    shutil.copytree(Path(__file__).resolve().parents[1]/'app',root/'src/backend/app',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    kind='requirements' if oid.startswith('REQ-') else 'bugs'
    domain='req' if kind=='requirements' else 'bug'
    folder=root/f'issues/{kind}/plan/{oid}'
    for name in ('trace.md','requirement.md' if domain=='req' else 'bug.md'):
        path=folder/name;parts=path.read_text().split('---',2);meta=yaml.safe_load(parts[1])
        meta.update(related_requirement=None,related_requirements=[],related_change=None,related_changes=[],openspec_changes=[],iteration=None,status='pending_review',lifecycle_stage='plan')
        path.write_text('---\n'+yaml.safe_dump(meta,allow_unicode=True,sort_keys=False)+'---'+parts[2])
    acceptance=folder/'acceptance.md'
    sys.path.insert(0,str(root/'scripts'))
    from workflow_sync.issue_subdocuments import render_acceptance_block
    text=acceptance.read_text();parts=text.split('---',2);meta=yaml.safe_load(parts[1]);meta['acceptance_status']='not_started'
    body=parts[2].split('## 验收结果回填')[0].rstrip()+'\n\n'+render_acceptance_block(status='not_started',source_change=None,source_sprint=None,event=domain+'.complete')
    acceptance.write_text('---\n'+yaml.safe_dump(meta,allow_unicode=True,sort_keys=False)+'---'+body)
    primary=folder/('requirement.md' if domain=='req' else 'bug.md')
    meta=yaml.safe_load(primary.read_text().split('---',2)[1])
    registry=root/f'issues/{kind}/_registry.yaml';data=yaml.safe_load(registry.read_text())
    for item in data['entries']:
        if item['id']==oid:
            item.clear();item.update(id=oid,title=meta['title'],status='pending_review',path=f'issues/{kind}/plan/{oid}/',lifecycle_stage='plan',iteration=None,related_change=None)
            item['priority' if domain=='req' else 'severity']=meta.get('priority' if domain=='req' else 'severity','P2')
    registry.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False))
    environment={**os.environ,'PYTHONPATH':str(Path(__file__).resolve().parents[1])}
    command=[sys.executable,str(root/'scripts/sync-workflow-status.py'),'--event',domain+'.complete','--'+domain,oid]
    result=subprocess.run(command,cwd=root,env=environment,capture_output=True,text=True)
    if result.returncode:raise ValueError('fixture_complete_sync_failed')
    before=stable(root).files
    with tempfile.TemporaryDirectory(prefix='moonbox-review-preview-',dir='/private/tmp') as temporary:
        preview=Path(temporary)
        for name in (*ROOTS,'scripts'):
            if (root/name).exists():shutil.copytree(root/name,preview/name)
        shutil.copytree(root/'src/backend/app',preview/'src/backend/app')
        base=f'issues/{kind}/plan/{oid}';target=base.replace('/plan/','/review/')
        (preview/target).parent.mkdir(parents=True,exist_ok=True);shutil.move(str(preview/base),str(preview/target))
        for path in (preview/target).rglob('*'):
            if path.is_file() and path.suffix in ('.md','.html'):path.write_bytes(path.read_bytes().replace(base.encode(),target.encode()))
        field='requirement_id' if domain=='req' else 'bug_id'
        for name in ('requirement.md' if domain=='req' else 'bug.md','trace.md'):
            path=preview/target/name;parts=path.read_text().split('---',2);meta=yaml.safe_load(parts[1]);meta.update(status='approved',lifecycle_stage='review');meta.setdefault('lifecycle',{}).update(reviewed='2026-10-19',approved='2026-10-19');path.write_text('---\n'+yaml.safe_dump(meta,allow_unicode=True,sort_keys=False)+'---'+parts[2])
        (preview/target/'review.md').write_text('---\n'+yaml.safe_dump({field:oid,'title':'隔离样本评审记录','result':'approved'},allow_unicode=True,sort_keys=False)+'---\n# 隔离样本评审记录\n\n仅用于夹具合法迁移预检，不属于产品轮次。\n')
        registry=preview/f'issues/{kind}/_registry.yaml';data=yaml.safe_load(registry.read_text())
        for item in data['entries']:
            if item['id']==oid:item.update(status='approved',path=target+'/',lifecycle_stage='review')
        registry.write_text(yaml.safe_dump(data,allow_unicode=True,sort_keys=False))
        result=subprocess.run([sys.executable,str(preview/'scripts/sync-workflow-status.py'),'--event',domain+'.review','--'+domain,oid],cwd=preview,env=environment,capture_output=True,text=True)
        if result.returncode:raise ValueError('fixture_review_sync_failed')
        after=stable(preview).files
        try:
            checked=validate_review(before,after,oid,base,domain+'-review')
        except Exception as error:
            import json
            (root/'preflight-diagnostic.json').write_text(json.dumps({'reason':getattr(error,'details',{}),'metadata':{p:yaml.safe_load(b.decode().split('---',2)[1]) for p,b in after.items() if p.startswith(target+'/') and p.endswith(('trace.md','requirement.md','bug.md','review.md'))},'changed':[p for p in set(before)|set(after) if before.get(p)!=after.get(p)]},default=str))
            raise ValueError(str(getattr(error,'details',{}))) from None
        return {'sample':oid,'fixture_preflight':'passed','file_changes':len(checked['files']),'evidence_kind':'synthetic_fixture'}


if __name__=='__main__':
    import json
    print(json.dumps(prepare(sys.argv[1],sys.argv[2])))
