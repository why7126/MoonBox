"""A terminal status is not sufficient evidence for releasing a workspace."""
from sqlalchemy import insert, select
from app.chat import service
from app.chat.schema import turns
from app.moonbox_core import completion, workspaces
from app.moonbox_core.schema import session_bindings, execution_receipts, write_locks
from test_chat import chat, create
from test_managed_worktree_git import repo


def test_unknown_executor_keeps_lease_without_starving_closed_executor(chat, repo, monkeypatch):
    client, factory = chat
    source, managed = repo
    with factory.begin() as db:
        main = workspaces.register_main(db, 'space', 'repo', source.root)
        child = workspaces.reserve_development(db, main, 'REQ-0001-example', managed)
    with factory.begin() as db:
        child = workspaces.materialize(db, main, child)
    identifiers = []
    for index, workspace in enumerate((main, child)):
        cid = create(client)
        identity = service.identity(); identifiers.append(identity['id'])
        with factory.begin() as db:
            db.execute(insert(session_bindings).values(conversation_id=cid, workspace_id=workspace['id']))
            db.execute(insert(turns).values(**identity, conversation_id=cid, client_request_id='completed',
                status='completed', generation=1, prompt='synthetic completion'))
            db.execute(insert(execution_receipts).values(turn_id=identity['id'], executor_id=None,
                executor_closed=index, files_collected=0, scope_json='[]'))
            workspaces.acquire(db, workspace['id'], identity['id'], 1)
    import app.governance.preparation
    monkeypatch.setattr(app.governance.preparation, 'collect', lambda *_: None)
    assert completion.reconcile(factory) == 1
    with factory() as db:
        assert list(db.scalars(select(write_locks.c.operation_id))) == [identifiers[0]]
        assert db.scalar(select(execution_receipts.c.files_collected).where(execution_receipts.c.turn_id == identifiers[1])) == 1


def test_batch_limit_does_not_starve_unknown_receipts(chat,repo,monkeypatch):
    client,factory=chat;source,managed=repo
    with factory.begin() as db: main=workspaces.register_main(db,'space','repo',source.root)
    for index in range(3):
        cid=create(client); identity=service.identity()
        with factory.begin() as db:
            child=workspaces.reserve_development(db,main,'REQ-000'+str(index)+'-test',managed)
            db.execute(insert(turns).values(**identity,conversation_id=cid,client_request_id='done',status='completed',generation=1,prompt='sample'))
            db.execute(insert(execution_receipts).values(turn_id=identity['id'],executor_closed=0,files_collected=0))
            workspaces.acquire(db,child['id'],identity['id'],1)
    seen=[]
    monkeypatch.setattr(completion,'_reconcile_one',lambda factory,item: seen.append(item['id']) or False)
    for _ in range(3): completion.reconcile(factory,limit=1)
    assert len(set(seen))==3
