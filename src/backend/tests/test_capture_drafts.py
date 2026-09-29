import pytest
from pydantic import ValidationError
from sqlalchemy import select
from app.chat.service import ChatError
from app.governance import capture_drafts as service
from app.governance.capture_schema import revisions
from app.schemas.capture_drafts import Candidate
from test_chat import chat
from test_governance_writer import writing


def content():
    return {'text':'反馈附图，并保留列表位置','media_ids':[], 'candidates':[
        {'type':'bug','title':'列表刷新位置丢失','description':'用户描述实际与期望差异，复现待补',
         'severity':'medium','source_refs':['text']}]}

def test_unconfirmed_draft_cas_sources_and_type_change(writing):
    factory,project,before,_,_=writing
    with factory() as db:
        draft=service.create(db,'alice',project)
        first=service.save(db,'alice',project,draft['id'],1,content())
        cid=first['content']['candidates'][0]['id']
        update=first['content'];item=update['candidates'][0];item.pop('severity');item.update(type='requirement',priority='P1')
        second=service.save(db,'alice',project,draft['id'],2,update)
        assert second['content']['candidates'][0]['id']==cid
        with pytest.raises(ChatError):service.save(db,'alice',project,draft['id'],2,update)
        db.rollback()
        assert len(db.execute(select(revisions).where(revisions.c.draft_id==draft['id'])).all())==3
    from app.governance.snapshot import stable
    assert stable(project.root).files==before

def test_delete_and_ownership(writing):
    factory,project,*_=writing
    with factory() as db:
        draft=service.create(db,'alice',project)
        with pytest.raises(ChatError):service.get(db,'bob',project,draft['id'])
        service.remove(db,'alice',project,draft['id'],1)
        with pytest.raises(ChatError) as exc:service.get(db,'alice',project,draft['id'])
        assert exc.value.status==410
        assert service.listing(db,'alice',project)['total']==0

def test_draft_limit_and_recovery_after_delete(writing):
    factory,project,*_=writing
    with factory() as db:
        rows=[service.create(db,'alice',project) for _ in range(50)]
        with pytest.raises(ChatError):service.create(db,'alice',project)
        service.remove(db,'alice',project,rows[0]['id'],1)
        assert service.create(db,'alice',project)

def test_candidate_contract():
    data=content()['candidates'][0]
    with pytest.raises(ValidationError):Candidate(**data,priority='P1')
    with pytest.raises(ValidationError):Candidate(**data,issue_id='BUG-9999')
    with pytest.raises(ValidationError):Candidate(**{**data,'title':' '*5})

def test_merge_lineage_and_forged_candidate(writing):
    factory,project,*_=writing
    with factory() as db:
        draft=service.create(db,'alice',project);first=service.save(db,'alice',project,draft['id'],1,content())
        parent=first['content']['candidates'][0]['id'];data=content();data['candidates'][0]['parents']=[parent]
        merged=service.save(db,'alice',project,draft['id'],2,data)
        assert merged['content']['candidates'][0]['id']!=parent
        bad=merged['content'];bad['candidates'][0]['id']='forged'
        with pytest.raises(ChatError):service.save(db,'alice',project,draft['id'],3,bad)


def test_confirm_batch_different_keys_and_recovery(writing):
    from app.governance import capture_confirmations as confirm, writer, readiness, store
    from app.governance.capture_schema import confirmations
    from app.governance.snapshot import stable
    import yaml
    factory,project,before,*_=writing;readiness.publish()
    with factory() as db:
        draft=service.create(db,'alice',project);data=content()
        data['candidates'] += [{'type':'requirement','title':'支持截图反馈','description':'新增图文反馈能力','priority':'P1','source_refs':['text']},
                               {'type':'requirement','title':'保留反馈草稿','description':'新增保存能力','priority':'P2','source_refs':['text']}]
        service.save(db,'alice',project,draft['id'],1,data)
        first=confirm.confirm(db,'alice',project,draft['id'],2,'first')
        assert confirm.confirm(db,'alice',project,draft['id'],2,'different')['id']==first['id']
        assert stable(project.root).files==before
        oid=db.scalar(select(confirmations.c.operation_id).where(confirmations.c.id==first['id']))
        def crash(*_):raise SystemExit('synthetic power loss')
        with pytest.raises(SystemExit):writer.process(db,oid,after_write=crash)
        planned=store.read(oid,'operation')['issue_links']
        with pytest.raises(ChatError):writer.assert_readable(db,project)
    with factory() as db:
        assert writer.process(db,oid)['state']=='applied'
        result=confirm.status(db,'alice',project,first['id'])
        assert result['state']=='completed' and len(result['issue_links'])==3
        assert len({i['issue_id'] for i in result['issue_links']})==3
        assert store.read(oid,'operation')['issue_links']==planned
        for link in result['issue_links']:
            kind='bugs' if link['issue_id'].startswith('BUG-') else 'requirements'
            path=project.root/'issues'/kind/'plan'/link['issue_id']
            assert {p.name for p in path.iterdir()}=={'capture.md','trace.md'}
            meta=yaml.safe_load((path/'trace.md').read_text().split('---',2)[1])
            assert meta['captured_via']=='capture' and meta['capture_source']['candidate_id']==link['candidate_id']
        assert confirm.confirm(db,'alice',project,draft['id'],2,'after-done')['id']==first['id']


def test_draft_api_version_and_formal_id_rejection(chat,writing):
    client,_=chat;query={'space_id':'space','repository_id':'repo'}
    created=client.post('/api/v1/requirement-center/capture-drafts',params=query)
    assert created.status_code==200,created.text
    draft=created.json()['data'];url=f'/api/v1/requirement-center/capture-drafts/{draft["id"]}'
    result=client.patch(url,params=query,json={**content(),'expected_revision':1})
    assert result.status_code==200,result.text
    assert client.patch(url,params=query,json={**content(),'expected_revision':1}).status_code==409
    assert client.patch(url,params=query,json={**content(),'expected_revision':2,'issue_id':'REQ-9999'}).status_code==422
    assert client.get(url,params=query).json()['data']['revision']==2


def test_organizer_preserves_manual_revision_and_rejects_model_ids(writing):
    from app.governance import capture_organizer as organizer
    import json
    factory,project,before,*_=writing
    with factory() as db:
        draft=service.create(db,'alice',project);service.save(db,'alice',project,draft['id'],1,content())
        task=organizer.start(db,'alice',project,draft['id'],2)
        changed=content();changed['text']='人工补充，不允许被迟到模型覆盖';service.save(db,'alice',project,draft['id'],2,changed)
    organizer.run(factory,task['id'],lambda prompt,images:json.dumps({'candidates':content()['candidates']}))
    with factory() as db:
        assert organizer.status(db,'alice',project,draft['id'],task['id'])['state']=='ready'
        assert service.public(service.get(db,'alice',project,draft['id']))['content']['text']==changed['text']
    bad=content()['candidates'][0];bad['id']='REQ-0099'
    with pytest.raises(ValueError):organizer.validate_result(json.dumps({'candidates':[bad]}),content())
    from app.governance.snapshot import stable
    assert stable(project.root).files==before


@pytest.mark.parametrize('fail_index',range(10))
def test_every_batch_file_boundary(writing,fail_index):
    from app.governance import capture_confirmations as confirm, writer, readiness, store
    from app.governance.capture_schema import confirmations,links
    factory,project,*_=writing;readiness.publish()
    with factory() as db:
        draft=service.create(db,'alice',project);data=content()
        data['candidates'] += [{'type':'requirement','title':f'独立需求{i}','description':'合成验收材料','priority':'P1','source_refs':['text']} for i in range(2)]
        service.save(db,'alice',project,draft['id'],1,data);task=confirm.confirm(db,'alice',project,draft['id'],2,'once')
        oid=db.scalar(select(confirmations.c.operation_id).where(confirmations.c.id==task['id']))
        def crash(index,_):
            if index==fail_index:raise SystemExit('file boundary')
        with pytest.raises(SystemExit):writer.process(db,oid,after_write=crash)
        expected=store.read(oid,'operation')['issue_links']
    with factory() as db:
        assert writer.process(db,oid)['state']=='applied'
        assert store.read(oid,'operation')['issue_links']==expected
        assert len(db.execute(select(links).where(links.c.task_id==task['id'])).all())==3


def test_concurrent_confirmation_has_one_business_task(writing):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from app.governance import capture_confirmations as confirm,readiness
    from app.governance.capture_schema import confirmations
    factory,project,*_=writing;readiness.publish()
    with factory() as db:
        draft=service.create(db,'alice',project);service.save(db,'alice',project,draft['id'],1,content())
    gate=Barrier(2)
    def submit(key):
        with factory() as db:
            gate.wait()
            return confirm.confirm(db,'alice',project,draft['id'],2,key)['id']
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(submit,['a','b']))
    assert len(set(results))==1
    with factory() as db:assert len(db.execute(select(confirmations)).all())==1


def test_retry_does_not_overwrite_external_change(writing):
    from app.governance import capture_confirmations as confirm,writer,readiness,store
    from app.governance.capture_schema import confirmations
    factory,project,*_=writing;readiness.publish()
    with factory() as db:
        draft=service.create(db,'alice',project);service.save(db,'alice',project,draft['id'],1,content())
        task=confirm.confirm(db,'alice',project,draft['id'],2,'once')
        oid=db.scalar(select(confirmations.c.operation_id).where(confirmations.c.id==task['id']))
        def crash(*_):raise SystemExit('fixture')
        with pytest.raises(SystemExit):writer.process(db,oid,after_write=crash)
        plan=store.read(oid,'operation');target=next(iter(plan['after']))
        path=project.root/target;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('external modification')
        assert writer.process(db,oid)['state']=='recovery_blocked'
        with pytest.raises(ChatError):confirm.retry(db,'alice',project,task['id'])
        assert path.read_text()=='external modification'
        path.write_text(plan['after'][target])
        assert confirm.retry(db,'alice',project,task['id'])['state']=='recovering'
        assert writer.process(db,oid)['state']=='applied'
        issue=confirm.status(db,'alice',project,task['id'])['issue_links'][0]['issue_id']
        assert confirm.source(db,'alice',project,issue)['revision']==2


def test_confirmation_key_cannot_be_rebound_to_another_draft(writing):
    from app.governance import capture_confirmations as confirm,readiness
    from app.governance.capture_schema import drafts,confirmations
    factory,project,*_=writing;readiness.publish()
    with factory() as db:
        first=service.create(db,'alice',project);second=service.create(db,'alice',project)
        for draft in (first,second):service.save(db,'alice',project,draft['id'],1,content())
        confirm.confirm(db,'alice',project,first['id'],2,'shared-key')
        confirm.confirm(db,'alice',project,first['id'],2,'alias-key')
        with pytest.raises(ChatError):confirm.confirm(db,'alice',project,second['id'],2,'alias-key')
        with pytest.raises(ChatError) as exc:confirm.confirm(db,'alice',project,second['id'],2,'shared-key')
        assert exc.value.status==409
        assert db.scalar(select(drafts.c.state).where(drafts.c.id==second['id']))=='editing'
        assert len(db.execute(select(confirmations)).all())==1


def test_delete_and_confirm_race_has_one_winner(writing):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from app.governance import capture_confirmations as confirm,readiness
    from app.governance.capture_schema import drafts,confirmations
    factory,project,*_=writing;readiness.publish()
    with factory() as db:
        draft=service.create(db,'alice',project);service.save(db,'alice',project,draft['id'],1,content())
    gate=Barrier(2)
    def compete(action):
        with factory() as db:
            gate.wait()
            try:
                if action=='delete':service.remove(db,'alice',project,draft['id'],2)
                else:confirm.confirm(db,'alice',project,draft['id'],2,'race')
                return action
            except ChatError:return 'rejected'
    with ThreadPoolExecutor(max_workers=2) as pool:out=list(pool.map(compete,['delete','confirm']))
    assert out.count('rejected')==1
    with factory() as db:
        state=db.scalar(select(drafts.c.state).where(drafts.c.id==draft['id']))
        assert state in ('deleted','confirmed')
        assert len(db.execute(select(confirmations)).all())==(1 if state=='confirmed' else 0)


def test_quota_last_slot_is_reserved_once(writing):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from app.governance.capture_schema import quotas
    factory,project,*_=writing
    with factory() as db:
        for _ in range(49):service.create(db,'alice',project)
    gate=Barrier(2)
    def create(_):
        with factory() as db:
            gate.wait()
            try:service.create(db,'alice',project);return True
            except ChatError:return False
    with ThreadPoolExecutor(max_workers=2) as pool:assert sum(pool.map(create,range(2)))==1
    with factory() as db:assert db.scalar(select(quotas.c.draft_count))==50


def test_two_batches_share_the_formal_numbering_lock(writing):
    from app.governance import capture_confirmations as confirm,writer,readiness
    from app.governance.capture_schema import confirmations
    factory,project,*_=writing;readiness.publish()
    with factory() as db:
        tasks=[]
        for index in range(2):
            draft=service.create(db,'alice',project);service.save(db,'alice',project,draft['id'],1,content())
            tasks.append(confirm.confirm(db,'alice',project,draft['id'],2,'batch-'+str(index)))
        for task in tasks:
            oid=db.scalar(select(confirmations.c.operation_id).where(confirmations.c.id==task['id']))
            assert writer.process(db,oid)['state']=='applied'
        links=[confirm.status(db,'alice',project,t['id'])['issue_links'][0]['issue_id'] for t in tasks]
        assert len(set(links))==2 and all(item.startswith('BUG-') for item in links)


@pytest.mark.parametrize('boundary',['before_plan','after_plan','before_complete','after_complete','after_applied'])
def test_plan_and_database_completion_crash_boundaries(writing,monkeypatch,boundary):
    from app.governance import capture_confirmations as confirm,writer,readiness,store
    from app.governance.capture_schema import confirmations,links
    factory,project,*_=writing;readiness.publish()
    with factory() as db:
        draft=service.create(db,'alice',project);service.save(db,'alice',project,draft['id'],1,content())
        task=confirm.confirm(db,'alice',project,draft['id'],2,'boundary')
        oid=db.scalar(select(confirmations.c.operation_id).where(confirmations.c.id==task['id']))
        oldwrite=store.write;oldcomplete=confirm.complete;oldstate=writer.set_state
        def write(id,kind,record):
            if record.get('planned') and record.get('phase')!='prepared' and not str(record.get('phase','')).startswith('file-'):
                if boundary=='before_plan':raise SystemExit('before plan persist')
                oldwrite(id,kind,record)
                if boundary=='after_plan':raise SystemExit('after plan persist')
            else:oldwrite(id,kind,record)
        def complete(*args):
            if boundary=='before_complete':raise SystemExit('before completion mapping')
            oldcomplete(*args)
            if boundary=='after_complete':raise SystemExit('before DB commit')
        def state(*args,**kwargs):
            oldstate(*args,**kwargs)
            if args[2]=='applied' and boundary=='after_applied':raise SystemExit('lost response')
        with monkeypatch.context() as patch:
            patch.setattr(store,'write',write);patch.setattr(confirm,'complete',complete);patch.setattr(writer,'set_state',state)
            with pytest.raises(SystemExit):writer.process(db,oid)
        db.rollback()
    with factory() as db:
        assert writer.process(db,oid)['state']=='applied'
        assert len(db.execute(select(links).where(links.c.task_id==task['id'])).all())==1
        assert confirm.status(db,'alice',project,task['id'])['state']=='completed'


def test_missing_plan_after_partial_write_never_reallocates(writing):
    from app.governance import capture_confirmations as confirm,writer,readiness,store
    from app.governance.capture_schema import confirmations
    from app.governance.snapshot import read_once
    factory,project,*_=writing;readiness.publish()
    with factory() as db:
        draft=service.create(db,'alice',project);service.save(db,'alice',project,draft['id'],1,content())
        task=confirm.confirm(db,'alice',project,draft['id'],2,'missing-plan')
        oid=db.scalar(select(confirmations.c.operation_id).where(confirmations.c.id==task['id']))
        def crash(*_):raise SystemExit('power loss')
        with pytest.raises(SystemExit):writer.process(db,oid,after_write=crash)
        partial=read_once(project.root);record=store.read(oid,'operation')
        record.update(planned=False,before={},after={});store.write(oid,'operation',record)
        assert writer.process(db,oid)['state']=='recovery_blocked'
        assert read_once(project.root)==partial


def test_revoked_write_access_during_batch_stops_forward_writes(writing):
    from app.governance import capture_confirmations as confirm,writer,readiness
    from app.governance.capture_schema import confirmations
    from sqlalchemy import text
    factory,project,*_=writing;readiness.publish()
    with factory() as db:
        draft=service.create(db,'alice',project);service.save(db,'alice',project,draft['id'],1,content())
        task=confirm.confirm(db,'alice',project,draft['id'],2,'revoke')
        oid=db.scalar(select(confirmations.c.operation_id).where(confirmations.c.id==task['id']))
        written=[]
        def revoke(index,path):
            written.append(path)
            with factory() as permissions:
                permissions.execute(text("UPDATE admin_spaces SET status='FROZEN'"));permissions.commit()
        assert writer.process(db,oid,after_write=revoke)['state']=='recovery_blocked'
        assert len(written)==1
