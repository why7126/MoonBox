"""Disposable real archive runtime fixture; never uses a user's runtime database."""
import argparse
import ast
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess


def prepare(root, source):
    root.mkdir(mode=0o700, parents=True, exist_ok=False)
    project = root/'project'; project.mkdir()
    module = ast.parse((source/'scripts/validate-directory-structure.py').read_text())
    values = {n.targets[0].id: ast.literal_eval(n.value) for n in module.body
              if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
              and n.targets[0].id in {'REQUIRED_PATHS','REQUIRED_DIRS'}}
    for name in values['REQUIRED_DIRS']: (project/name).mkdir(parents=True, exist_ok=True)
    for name in values['REQUIRED_PATHS']:
        target=project/name; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source/name,target)
    shutil.copytree(source/'scripts',project/'scripts',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(source/'rules',project/'rules',dirs_exist_ok=True)
    shutil.copytree(source/'src/backend/app',project/'src/backend/app',dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__'))
    (project/'issues/requirements/_registry.yaml').write_text('entries: []\n')
    (project/'issues/bugs/_registry.yaml').write_text('entries: []\n')
    (project/'openspec/config.yaml').write_text('schema: spec-driven\n')
    samples=['fix-diag-cli','fix-diag-product','fix-diag-move','fix-diag-block']
    for cid in samples:
        folder=project/'openspec/changes'/cid; (folder/'specs'/cid).mkdir(parents=True)
        for name, title, body in [('proposal.md','隔离归档验证提案','## 为什么\n验证归档闭环。\n## 变更内容\n独立样本。\n## 影响\n仅隔离环境。'),
            ('design.md','隔离归档验证设计','使用独立样本。'),('tasks.md','隔离归档验证任务','- [x] 独立样本已准备。'),
            ('acceptance.md','隔离归档验证记录','测试命令：样本预检。验收结论：通过，仅代表样本已准备。'),
            ('trace.md','隔离归档验证追溯','')]:
            meta=f'title: {title}\n'
            if name=='trace.md':meta+=f'change_id: {cid}\nstatus: applied\nexecution:\n  schema_version: 1\n  started_at: "2026-10-30 08:00:00"\n  completed_at: "2026-10-30 08:01:00"\n  last_event: opsx.apply\n'
            (folder/name).write_text(f'---\n{meta}---\n# {title}\n\n{body}\n')
        (folder/'specs'/cid/'spec.md').write_text('## ADDED Requirements\n\n### Requirement: 隔离归档样本\n系统 SHALL 保留该样本。\n\n#### Scenario: 读取样本\n- **WHEN** 读取\n- **THEN** 样本保留\n')
    notes=project/'issues/requirements/review/REQ-9001-diag-notes';notes.mkdir(parents=True)
    (notes/'requirement.md').write_text('---\nstatus: in_sprint\n---\n# 当前说明\nfix-diag-block\n')
    (notes/'acceptance.md').write_text('---\nacceptance_status: partial\n---\n# 当前证据导航\nfix-diag-block [补充证据](evidence.md)\n')
    (project/'issues/requirements/_registry.yaml').write_text('entries:\n- id: REQ-9001-diag-notes\n  status: in_sprint\n  path: issues/requirements/review/REQ-9001-diag-notes\n')
    for name in ('state','private','runtime','workspaces','backups'):(root/name).mkdir(mode=0o700)
    password=secrets.token_urlsafe(24)+'9A!'
    (root/'login.json').write_text(json.dumps({'username':'alice','password':password}));(root/'login.json').chmod(0o600)
    binding={'id':'repo','space_id':'space','governance_root':'/project','source_root':'/project','workspace_root':'/data/workspaces','workspace_mode':'source'}
    env={'APP_ENV':'isolated-test','APP_SECRET_KEY':secrets.token_urlsafe(32),'DATABASE_TYPE':'sqlite',
         'DATABASE_URL':'sqlite:////data/moonbox.db','SQLITE_DATABASE_URL':'sqlite:////data/moonbox.db',
         'ADMIN_INITIAL_PASSWORD':secrets.token_urlsafe(24)+'9A!','MOONBOX_GOVERNANCE_STATE_ROOT':'/data/private',
         'MOONBOX_CHAT_STATE_ROOT':'/data/state','MOONBOX_CHAT_RUNTIME_ROOT':'/data/runtime',
         'MOONBOX_CHAT_REPOSITORIES':json.dumps([{'id':'repo','space_id':'space'}]),
         'MOONBOX_CHAT_REPOSITORY_BINDINGS':json.dumps([binding]),'PYTHONPATH':'/app:/harness',
         'GIT_CONFIG_COUNT':'1','GIT_CONFIG_KEY_0':'safe.directory','GIT_CONFIG_VALUE_0':'/project'}
    (root/'runtime.env').write_text('\n'.join(f'{k}={v}' for k,v in env.items())+'\n');(root/'runtime.env').chmod(0o600)
    subprocess.run(['git','init','-q',str(project)],check=True)
    subprocess.run(['git','-C',str(project),'add','README.md'],check=True)
    subprocess.run(['git','-C',str(project),'-c','user.name=Acceptance','-c','user.email=acceptance@example.invalid','commit','-qm','Initialize isolated fixture'],check=True)
    print('isolated fixture prepared')


def serve():
    from app.db.session import init_database, get_session_factory
    from app.repositories.admin_auth import hash_password
    from app.chat.service import now
    from sqlalchemy import text
    init_database()
    password=json.loads(Path('/data/login.json').read_text())['password']
    with get_session_factory()() as db:
        if not db.execute(text("SELECT id FROM admin_users WHERE id='alice'")).first():
            for uid in ('alice','bob'):
                db.execute(text("INSERT INTO admin_users(id,username,nickname,role,status,password_hash,created_at,updated_at) VALUES(:id,:id,:id,'前台用户','正常',:hash,:now,:now)"),{'id':uid,'hash':hash_password(password),'now':now()})
            db.execute(text("INSERT INTO admin_spaces(id,name,code,owner_id,status,source,member_count,member_quota,storage_quota_gb,ai_quota_tokens,expiry_type,created_at,updated_at) VALUES('space','隔离归档验收','archive-diag','alice','ACTIVE','后台创建',2,2,1,400000,'long_term',:now,:now)"),{'now':now()})
            db.commit()
    from app.main import app
    import uvicorn
    uvicorn.run(app,host='0.0.0.0',port=8000,access_log=False,log_level='warning')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','serve']);parser.add_argument('--root',type=Path);parser.add_argument('--source',type=Path)
    args=parser.parse_args()
    if args.mode=='prepare':prepare(args.root,args.source)
    else:serve()
