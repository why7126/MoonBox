"""Controller turns use no model and settle verified zero model tokens."""
from types import SimpleNamespace
import pytest
from sqlalchemy import insert,select,update
from test_chat import chat,create
from test_chat_accounting import LIMITS
from app.chat import service,worker
from app.chat.admission import enqueue
from app.chat.execution import run_claim
from app.chat.schema import turns,relations,reservations
from app.governance.replacement_schema import activations


@pytest.mark.parametrize('failed',[False,True,'before_snapshot','after_snapshot'])
def test_trusted_archive_turn_never_constructs_model(chat,tmp_path,monkeypatch,failed):
    client,factory=chat;cid=create(client);workspace=tmp_path/cid;workspace.mkdir()
    root=tmp_path/'repository';root.mkdir();(root/'sample.md').write_text('before')
    project=SimpleNamespace(key='a'*64,binding_revision='b'*64,root=root,space_id='space',repository_id='repo')
    monkeypatch.setattr('app.governance.scope.authorize',lambda *a,**k:project)
    monkeypatch.setattr('app.chat.relations.authorize_history',lambda *a,**k:None)
    calls=[]
    if failed in ('before_snapshot','after_snapshot'):
        from app.governance import archive_chat
        original=archive_chat.governance_snapshot
        snapshots=[]
        def controlled_snapshot(*args,**kwargs):
            snapshots.append(True)
            if len(snapshots)==(1 if failed=='before_snapshot' else 2):raise OSError('synthetic snapshot failure')
            return original(*args,**kwargs)
        monkeypatch.setattr(archive_chat,'governance_snapshot',controlled_snapshot)
    def execute(*args,**kwargs):
        calls.append(kwargs['object_id'])
        if failed is True:raise ValueError('synthetic guard refused')
        (root/'sample.md').write_text('after')
        return {'stage':'completed'}
    monkeypatch.setattr('app.governance.archive_dispatch.execute_object',execute)
    with factory() as db:
        row=enqueue(db,'alice',cid,'trusted','test',LIMITS)
        db.execute(update(turns).where(turns.c.id==row['id']).values(prompt='/opsx-archive sample-change'))
        db.execute(insert(relations).values(conversation_id=cid,object_id='sample-change',role='primary',title='合成对象'))
        db.execute(insert(activations).values(**service.identity(),scope_key=project.key,binding_revision=project.binding_revision,
            policy_version='controlled-v1',state='active',manifest_hash='c'*64,manifest='{}',revision=1))
        db.commit();token=worker.claim(db,'trusted-worker')
    def model(*args):raise AssertionError('model must not be called')
    assert run_claim(factory,token,workspace,model)==('failed' if failed else 'completed')
    assert calls==([] if failed=='before_snapshot' else ['sample-change'])
    with factory() as db:
        assert db.scalar(select(reservations.c.status))=='settled'
        assert db.scalar(select(reservations.c.actual_tokens))==0
        assert db.scalar(select(turns.c.executor_turn_id)) is None


def test_governance_snapshot_excludes_repository_credentials_and_git(tmp_path):
    from app.governance.archive_chat import governance_snapshot
    (tmp_path/'.git').mkdir();(tmp_path/'.env').write_text('private fixture')
    (tmp_path/'openspec').mkdir();(tmp_path/'openspec/spec.md').write_text('治理证据')
    value=governance_snapshot(tmp_path,max_text_bytes=1024)
    assert set(value['files'])=={'openspec/spec.md'}
    assert value['files']['openspec/spec.md']['text']=='治理证据'
