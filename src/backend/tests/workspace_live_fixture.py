"""Disposable UI acceptance app; synthetic identity/data, real authorization/API/Git.

Run with the project interpreter and PYTHONPATH=src/backend:src/backend/tests.
An approved MOONBOX_CANDIDATE_TEMPLATE is required for development/merge actions.
Never mount or point this harness at a production database or repository.
"""
import json
import tempfile
from pathlib import Path
import pytest
import uvicorn
import yaml
from fastapi import FastAPI
from sqlalchemy import insert
from test_chat import chat, create
from test_managed_worktree_git import repo, git
from app.chat import service, snapshot_store
from app.chat.schema import turns
from app.moonbox_core import workspaces
from app.moonbox_rollout import catalog
from app.moonbox_app_server.workspace_api import router
from app.main import app as original


def seed_project(root):
    issue = 'REQ-0042-example'
    issue_path = 'issues/requirements/review/' + issue
    files = {
        'issues/requirements/_registry.yaml': yaml.safe_dump({'entries': [dict(id=issue, title='隔离验收样本', status='in_sprint', path=issue_path)]}, allow_unicode=True),
        issue_path + '/requirement.md': '# 隔离验收样本\n',
        issue_path + '/trace.md': '---\n' + yaml.safe_dump(dict(status='in_sprint', iteration='sprint-015', openspec_changes=['example-change'])) + '---\n',
        'openspec/changes/example-change/trace.md': '---\n' + yaml.safe_dump(dict(status='in_progress', iteration='sprint-015', requirement_id=issue)) + '---\n',
        'iterations/change/sprint-015/sprint.yaml': yaml.safe_dump(dict(sprint_id='sprint-015', status='active', requirements=[issue], changes=['example-change'])),
        'iterations/change/sprint-015/sprint.md': '# 隔离验收迭代\n',
        'requirements.txt': 'fixture-lock\n',
        'src/server.py': "from fastapi import FastAPI\nfrom fastapi.responses import HTMLResponse\napp=FastAPI()\n@app.get('/',response_class=HTMLResponse)\ndef home(): return '<h1>Isolated candidate</h1>'\n",
        'src/migrate.py': "import os\nfrom sqlalchemy import create_engine,text\nwith create_engine(os.environ['DATABASE_URL']).begin() as db: db.execute(text('CREATE TABLE sample (id INTEGER PRIMARY KEY, value VARCHAR(32))'))\n",
        'src/seed.py': "import os\nfrom sqlalchemy import create_engine,text\nwith create_engine(os.environ['DATABASE_URL']).begin() as db: db.execute(text(\"INSERT INTO sample VALUES (1, 'synthetic')\"))\n",
        'src/check.py': "import os\nfrom sqlalchemy import create_engine,text\nwith create_engine(os.environ['DATABASE_URL']).connect() as db: assert db.scalar(text('SELECT value FROM sample WHERE id=1'))=='synthetic'\n",
    }
    for name, value in files.items():
        target = root/name; target.parent.mkdir(parents=True, exist_ok=True); target.write_text(value)
    git(root, 'add', '.')
    git(root, '-c', 'user.name=Acceptance', '-c', 'user.email=acceptance@example.invalid', 'commit', '-qm', 'synthetic governance and app baseline')


def main():
    with tempfile.TemporaryDirectory(prefix='moonbox-workspace-live-') as folder, pytest.MonkeyPatch.context() as patch:
        root = Path(folder).resolve()
        source, managed = repo.__wrapped__(root)
        seed_project(source.root)
        state = root/'state'; state.mkdir(mode=0o700)
        patch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT', str(state))
        patch.setenv('MOONBOX_CANDIDATE_ROOT', str(root/'candidate-environments'))
        generator = chat.__wrapped__(root, patch)
        client, factory = next(generator)
        patch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS', json.dumps([dict(id='repo',space_id='space',source_root=str(source.root),governance_root=str(source.root),workspace_root=str(managed),workspace_mode='source')]))
        cid = create(client)
        with factory.begin() as db:
            workspace = workspaces.register_main(db, 'space', 'repo', source.root)
            turn = service.identity()
            db.execute(insert(turns).values(**turn,conversation_id=cid,client_request_id='synthetic-live',status='completed',prompt='合成验收样本，无模型调用'))
        for phase in ('before', 'after'):
            if phase == 'after': (source.root/'file.txt').write_text('synthetic implementation change')
            snapshot = snapshot_store.capture(factory,cid,turn['id'],source.root,phase,policy_roots=('',))
            with factory.begin() as db:
                point = catalog.publish(db,workspace['id'],snapshot['version_id'],policy_version='scope-test-v1',head_commit=source.head(),changed=True,scope=[''])
                if phase == 'before': catalog.reference(db,workspace['id'],point['id'],'initial','initial','initial_baseline')
        # Restore the deliberate sample edit before creating any task baseline.
        (source.root/'file.txt').write_text('baseline')
        app = FastAPI(); app.include_router(router)
        app.dependency_overrides.update(original.dependency_overrides)
        @app.get('/api/v1/workspace-test/context')
        def context(): return {'conversation_id':cid,'sample':'synthetic-real-api-no-model'}
        # Private local controller file, never a browser/API field or persistent evidence.
        Path('/tmp/moonbox-workspace-fixture-locator.json').write_text(json.dumps({'source':str(source.root),'managed':str(managed),'database':str(root/'chat.db')}))
        try: uvicorn.run(app,host='127.0.0.1',port=8129,log_level='warning')
        finally:
            try: next(generator)
            except StopIteration: pass


if __name__ == '__main__': main()
