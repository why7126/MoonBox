from sqlalchemy import insert,select,delete,update
from test_chat import chat,create
from test_managed_worktree_git import repo
from app.chat import service,snapshot_store
from app.chat.schema import turns
from app.chat.content_schema import entries,chunks
from app.moonbox_core import workspaces
from app.moonbox_core.schema import session_bindings
from app.moonbox_rollout.migration import adopt
from app.moonbox_rollout.schema import points


def test_verified_history_adopted_once_but_corruption_not_promoted(chat,repo):
    client,factory=chat;source,_=repo;cid=create(client)
    with factory.begin() as db:
        main=workspaces.register_main(db,'space','repo',source.root)
        db.execute(insert(session_bindings).values(conversation_id=cid,workspace_id=main['id']))
        identity=service.identity()
        db.execute(insert(turns).values(**identity,conversation_id=cid,client_request_id='old',status='completed',prompt='sample'))
    snapshot=snapshot_store.capture(factory,cid,identity['id'],source.root,'before',policy_roots=('',))
    with factory.begin() as db:
        assert adopt(db,main,cid)==1
        assert adopt(db,main,cid)==0
        row=db.execute(select(points)).mappings().one()
        assert row['scope_json'] is None
        assert row['policy_version']=='legacy-verified-v2'
    (source.root/'file.txt').write_text('another historical value')
    corrupt=snapshot_store.capture(factory,cid,identity['id'],source.root,'after',policy_roots=('',))
    with factory.begin() as db:
        oid=db.scalar(select(entries.c.object_id).where(entries.c.version_id==corrupt['version_id']))
        db.execute(delete(chunks).where(chunks.c.object_id==oid))
        assert adopt(db,main,cid)==0
