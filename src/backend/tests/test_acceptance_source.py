"""Real Git/content-store export; authority and runtime are separate boundaries."""
import hashlib
import json
import pytest
from sqlalchemy import select,update
from app.chat.snapshot_store import capture
from app.moonbox_rollout.catalog import publish
from app.moonbox_rollout.schema import entries
from app.verification.acceptance_source import export_checkpoint
from app.verification.acceptance_state import Conflict
from test_recovery_catalog import data
from test_managed_worktree_git import repo,git


def checkpoint(data,repo):
    factory,wid=data;root=repo[0].root
    from app.chat.content_schema import TABLES
    for table in TABLES:table.create(factory.kw['bind'],checkfirst=True)
    from app.chat.schema import usage_accounts
    usage_accounts.create(factory.kw['bind'],checkfirst=True)
    (root/'requirements.txt').write_text('locked\n')
    (root/'src').mkdir();(root/'src/app.py').write_text('baseline\n')
    (root/'src/deleted.py').write_text('delete me\n')
    git(root,'add','.');git(root,'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','baseline')
    head=git(root,'rev-parse','HEAD')
    (root/'src/app.py').write_text('authorized uncommitted\n');(root/'src/deleted.py').unlink()
    version=capture(factory,'c','t',root,'after',policy_roots=['src'])
    with factory.begin() as db:
        point=publish(db,wid,version['version_id'],policy_version='test',head_commit=head,changed=True,scope=['src'])
    reference={'point_id':point['id'],'workspace_id':wid,'head_commit':head,'manifest_hash':point['manifest_hash']}
    template={'lock_path':'requirements.txt','lock_digest':hashlib.sha256(b'locked\n').hexdigest()}
    return factory,root,reference,template


def test_export_uses_immutable_authorized_content_and_deletions(data,repo,tmp_path):
    factory,root,reference,template=checkpoint(data,repo)
    (root/'src/app.py').write_text('later unrelated edit\n')
    target=tmp_path/'export'
    export_checkpoint(factory,reference,target,template)
    assert (target/'src/app.py').read_text()=='authorized uncommitted\n'
    assert not (target/'src/deleted.py').exists()
    assert (target/'requirements.txt').read_text()=='locked\n'
    assert (root/'src/app.py').read_text()=='later unrelated edit\n'


def test_export_rejects_corrupt_checkpoint_and_unapproved_lock(data,repo,tmp_path):
    factory,root,reference,template=checkpoint(data,repo)
    with pytest.raises(Conflict,match='snapshot_dependencies_unapproved'):
        export_checkpoint(factory,reference,tmp_path/'bad-lock',{**template,'lock_digest':'0'*64})
    with factory.begin() as db:
        db.execute(update(entries).where(entries.c.point_id==reference['point_id']).values(digest='0'*64))
    with pytest.raises(Conflict,match='snapshot_integrity_failed'):
        export_checkpoint(factory,reference,tmp_path/'corrupt',template)


@pytest.mark.parametrize('live',[False,True])
def test_create_resolves_closed_turn_checkpoint_and_rejects_later_input(data,repo,tmp_path,monkeypatch,live):
    from types import SimpleNamespace
    from sqlalchemy import insert
    from app.verification.acceptance_schema import TABLES
    from app.verification.acceptance_service import create
    from app.moonbox_core.schema import delivery_sessions,execution_receipts
    from app.moonbox_rollout.catalog import reference as link
    factory,root,source,template=checkpoint(data,repo)
    for table in TABLES:table.create(factory.kw['bind'],checkfirst=True)
    project=SimpleNamespace(root=root,binding_revision='b'*64)
    context={'delivery_root':'REQ-0048-synthetic'}
    grant=lambda *args,**kwargs:(project,context)
    monkeypatch.setattr('app.chat.service.authorize_space',lambda *args:None)
    monkeypatch.setattr('app.chat.settings.repository_catalog',lambda:[{'id':'repo','space_id':'space'}])
    monkeypatch.setattr('app.chat.relations.authorize_history',lambda *args:None)
    monkeypatch.setattr('app.verification.acceptance_source.delivery',grant)
    monkeypatch.setattr('app.moonbox_core.authority.delivery',grant)
    plan_dir=root/'openspec/changes/synthetic-change';plan_dir.mkdir(parents=True)
    (plan_dir/'acceptance-plan.json').write_text(json.dumps({'change_id':'synthetic-change','checks':[{'id':'AC-001','inputs':['src/app.py']}]}))
    with factory.begin() as db:
        db.execute(insert(delivery_sessions).values(conversation_id='c',change_id='synthetic-change',delivery_root='REQ-0048-synthetic'))
        db.execute(insert(execution_receipts).values(turn_id='t',executor_closed=int(not live),files_collected=int(not live),scope_json='["src"]'))
        link(db,source['workspace_id'],source['point_id'],'acceptance' if live else 'turn_after','t')
        if live:
            from app.verification.acceptance_schema import tool_waits
            from app.chat.service import identity
            db.execute(insert(tool_waits).values(**identity(),source_turn_id='t',call_id='call-test',
                generation=1,point_id=source['point_id'],state='waiting'))
    options={'source_point_id':source['point_id']} if live else {}
    with factory() as db:
        first=create(db,factory,'a','c','t','synthetic-change','same-key',**options)
    with factory() as db:
        assert create(db,factory,'a','c','t','synthetic-change','same-key',**options)['id']==first['id']
    (root/'src/app.py').write_text('later edit')
    with factory() as db,pytest.raises(Conflict,match='source_inputs_changed'):
        create(db,factory,'a','c','t','synthetic-change','new-key',**options)


def test_live_tool_creates_real_checkpoint_and_recovers_link_after_restart(data,repo,tmp_path,monkeypatch):
    from types import SimpleNamespace
    from sqlalchemy import insert
    from app.verification.acceptance_schema import TABLES,tool_waits,operations
    from app.verification.acceptance_tool import begin
    from app.moonbox_core.schema import delivery_sessions,execution_receipts
    from app.chat.schema import conversations,turns
    factory,root,source,template=checkpoint(data,repo)
    for table in TABLES:table.create(factory.kw['bind'],checkfirst=True)
    project=SimpleNamespace(root=root,binding_revision='b'*64)
    grant=lambda *args,**kwargs:(project,{'delivery_root':'REQ-0048-synthetic'})
    monkeypatch.setattr('app.chat.service.authorize_space',lambda *args:None)
    monkeypatch.setattr('app.chat.settings.repository_catalog',lambda:[{'id':'repo','space_id':'space'}])
    monkeypatch.setattr('app.chat.relations.authorize_history',lambda *args:None)
    monkeypatch.setattr('app.verification.acceptance_source.delivery',grant)
    monkeypatch.setattr('app.moonbox_core.authority.delivery',grant)
    def owner(db,token):
        return (dict(db.execute(select(turns)).mappings().one()),dict(db.execute(select(conversations)).mappings().one()))
    monkeypatch.setattr('app.chat.execution.owned',owner)
    plan_dir=root/'openspec/changes/synthetic-change';plan_dir.mkdir(parents=True)
    (plan_dir/'acceptance-plan.json').write_text(json.dumps({'change_id':'synthetic-change','checks':[{'id':'AC-001','inputs':['src/app.py']}]}))
    with factory.begin() as db:
        db.execute(update(turns).values(status='running'))
        db.execute(insert(delivery_sessions).values(conversation_id='c',change_id='synthetic-change',delivery_root='REQ-0048-synthetic'))
        db.execute(insert(execution_receipts).values(turn_id='t',executor_closed=0,files_collected=0,scope_json='["src"]'))
    token={'turn_id':'t','generation':1}
    oid=begin(factory,token,root,'call-test')
    assert begin(factory,token,root,'call-test')==oid
    with factory.begin() as db:db.execute(update(tool_waits).values(operation_id=None))
    assert begin(factory,token,root,'call-test')==oid
    with factory() as db:
        assert len(db.execute(select(operations)).all())==1
        assert db.scalar(select(tool_waits.c.operation_id))==oid
