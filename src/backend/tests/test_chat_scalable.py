import hashlib
import json
from sqlalchemy import insert, select, update
from test_chat import chat, create, queued
from app.chat import settings, snapshot_store, content_store
from app.chat.schema import diffs, turns
from app.chat.content_schema import versions, entries


def test_defaults_and_deprecated_turn_budget(monkeypatch):
    monkeypatch.delenv('MOONBOX_CHAT_LIMITS',raising=False)
    limits=settings.execution_limits()
    assert limits['user_monthly_tokens'] is None
    assert limits['turn_reserved_bytes']==0 and limits['turn_reserved_tokens'] is None
    monkeypatch.setenv('MOONBOX_CHAT_LIMITS',json.dumps({'user_monthly_tokens':42,'turn_reserved_tokens':1}))
    assert settings.execution_limits()['user_monthly_tokens']==42
    assert settings.execution_limits()['turn_reserved_tokens'] is None
    monkeypatch.setenv('MOONBOX_CHAT_LIMITS','{"user_monthly_tokens":-1}')
    assert settings.execution_limits() is None


def test_snapshot_diff_and_full_text_pages(chat,tmp_path):
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    root=tmp_path/'work';root.mkdir()
    text='你好'*100000
    (root/'large.txt').write_text(text)
    before=snapshot_store.capture(factory,cid,tid,root,'before')
    (root/'large.txt').write_text(text+'new')
    after=snapshot_store.capture(factory,cid,tid,root,'after')
    with factory() as db:
        delta=snapshot_store.diff_page(db,before['version_id'],after['version_id'])
        assert len(delta['files'])==1
        from app.chat import service
        db.execute(insert(diffs).values(**service.identity(),turn_id=tid,before_hash=before['hash'],
            after_hash=after['hash'],payload=json.dumps({'format_version':2,'before_version':before['version_id'],
                'after_version':after['version_id'],'files':delta['files']})))
        db.commit()
    cursor=None;parts=[]
    while True:
        response=client.get(f'/api/v1/chat/turns/{tid}/files/{delta["files"][0]["file_id"]}/content',
                            params={'cursor':cursor} if cursor else {})
        assert response.status_code==200,response.text
        data=response.json()['data'];parts.append(data['text']);cursor=data['next_cursor']
        if not cursor:break
    assert ''.join(parts)==text+'new'


def test_segments_long_output_are_readable_and_authorized(chat):
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    block=b'x'*48000
    with factory() as db:
        for n in range(20): content_store.result(db,cid,tid,'output','source',n*len(block),block)
        db.commit()
    cursor=None;count=0
    while True:
        result=client.get(f'/api/v1/chat/turns/{tid}/results',params={'cursor':cursor} if cursor else {})
        assert result.status_code==200,result.text
        data=result.json()['data'];count+=sum(item['byte_count'] for item in data['items'])
        cursor=data['next_cursor']
        if not cursor:break
    assert count==20*len(block)
    another=queued(factory,create(client))
    assert client.get(f'/api/v1/chat/turns/{another}/results',params={'cursor':data['resume_cursor']}).status_code==422


def test_v2_run_uses_chunk_output(chat,tmp_path,monkeypatch):
    from app.chat.admission import enqueue
    from app.chat import worker
    from app.chat.execution import run_claim
    from test_chat_assistant_output import Peer
    client,factory=chat;cid=create(client);path=tmp_path/cid;path.mkdir()
    monkeypatch.delenv('MOONBOX_CHAT_LIMITS',raising=False)
    with factory() as db:
        row=enqueue(db,'alice',cid,'once','synthetic',settings.execution_limits())
        token=worker.claim(db,'worker')
    assert run_claim(factory,token,path,lambda _:Peer(False),usage_grace_seconds=0)=='stopped'
    response=client.get(f'/api/v1/chat/turns/{row["id"]}/results')
    assert response.status_code==200,response.text
    assert response.json()['data']['items'][0]['text']=='synthetic assistant output'


def test_snapshot_resume_reuses_committed_content_and_detects_rename(chat,tmp_path,monkeypatch):
    import pytest
    from app.chat.content_schema import objects
    from sqlalchemy import func
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    root=tmp_path/'resume';root.mkdir();(root/'first.txt').write_text('stable content')
    original=snapshot_store.names
    def interrupted(path):
        yield 'first.txt'
        raise OSError('synthetic scan interruption')
    monkeypatch.setattr(snapshot_store,'names',interrupted)
    with pytest.raises(OSError):snapshot_store.capture(factory,cid,tid,root,'before')
    with factory() as db:vid=db.scalar(select(versions.c.id))
    monkeypatch.setattr(snapshot_store,'names',original)
    before=snapshot_store.capture(factory,cid,tid,root,'before')
    assert before['version_id']==vid
    (root/'first.txt').rename(root/'renamed.txt')
    after=snapshot_store.capture(factory,cid,tid,root,'after')
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(objects))==1
        delta=snapshot_store.diff_page(db,before['version_id'],after['version_id'])
        assert len(delta['files'])==1
        assert delta['files'][0]['status']=='renamed'
        assert delta['files'][0]['previous_path']=='first.txt'


def test_legacy_backfill_restart_and_missing_text(chat):
    from app.chat.schema import workspace_baselines, conversations
    from app.chat.content_migration import batch
    from app.chat.content_schema import objects
    from sqlalchemy import func
    client, factory = chat; cid = create(client); tid = queued(factory, cid)
    legacy = {'hash':'synthetic-hash','files':{
        'saved.txt':{'kind':'file','sha256':hashlib.sha256(b'saved').hexdigest(),'size':5,'text':'saved'},
        'missing.txt':{'kind':'file','sha256':hashlib.sha256(b'missing').hexdigest(),'size':7,'text':None}}}
    with factory() as db:
        db.execute(update(conversations).where(conversations.c.id == cid).values(active_turn_id=None))
        db.execute(insert(workspace_baselines).values(conversation_id=cid,workspace_id=cid,content_hash=legacy['hash'],payload=json.dumps(legacy)))
        db.commit()
    assert batch(factory)['migrated'] == 1
    assert batch(factory)['migrated'] == 0
    with factory() as db:
        reference = json.loads(db.scalar(select(workspace_baselines.c.payload)))
        assert reference['hash'] == legacy['hash']
        assert db.scalar(select(func.count()).select_from(objects)) == 1
        missing = db.execute(select(entries).where(entries.c.path == 'missing.txt')).mappings().one()
        assert missing['object_id'] is None and missing['digest'] == legacy['files']['missing.txt']['sha256']


def test_late_receipt_corrects_usage_once(chat):
    from app.chat.admission import enqueue, settle
    from app.chat import worker
    from app.chat.schema import usage_accounts, reservations
    client, factory = chat; cid = create(client)
    with factory() as db:
        row = enqueue(db,'alice',cid,'late','synthetic',settings.execution_limits())
        token = worker.claim(db,'worker')
        worker.record_event(db,token,'done','execution.state',{'status':'completed'},terminal='completed')
        assert settle(db,row['id'],10,0)
        db.commit()
        assert settle(db,row['id'],30,0,revised_receipt=True)
        db.commit()
        assert not settle(db,row['id'],30,0,revised_receipt=True)
        assert not settle(db,row['id'],20,0,revised_receipt=True)
        assert db.scalar(select(usage_accounts.c.used_tokens).where(usage_accounts.c.id.like('user:alice:%'))) == 30
        assert db.scalar(select(reservations.c.actual_tokens)) == 30


def test_v2_manifest_matches_independent_content_and_mode_scan(chat,tmp_path):
    import os
    import stat
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    root=tmp_path/'manifest';root.mkdir()
    for name in ('change','remove','mode','same'): (root/name).write_text('first')
    before=snapshot_store.capture(factory,cid,tid,root,'before')
    old=(root/'change').stat();(root/'change').write_text('other');os.utime(root/'change',ns=(old.st_atime_ns,old.st_mtime_ns))
    (root/'remove').unlink();(root/'mode').chmod(0o755);(root/'added').write_text('new')
    after=snapshot_store.capture(factory,cid,tid,root,'after')
    expected={p.name:(hashlib.sha256(p.read_bytes()).hexdigest(),stat.S_IMODE(p.stat().st_mode),p.stat().st_size) for p in root.iterdir()}
    with factory() as db:
        actual={r['path']:(r['digest'],r['mode'],r['byte_count']) for r in snapshot_store.page(db,after['version_id'])}
        assert actual==expected
        changed={r['path']:r['status'] for r in snapshot_store.diff_page(db,before['version_id'],after['version_id'])['files']}
        assert changed=={'change':'modified','remove':'deleted','mode':'modified','added':'added'}


def test_v2_drift_never_publishes_complete_snapshot(chat,tmp_path,monkeypatch):
    import pytest
    from app.chat.workspace import WorkspaceError
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    root=tmp_path/'drift';root.mkdir();target=root/'file';target.write_text('first')
    original=snapshot_store.read_file
    def changing(*args,**kwargs):
        value=original(*args,**kwargs)
        if kwargs.get('retain'):target.write_text('changed after capture')
        return value
    monkeypatch.setattr(snapshot_store,'read_file',changing)
    with pytest.raises(WorkspaceError):snapshot_store.capture(factory,cid,tid,root,'before')
    with factory() as db:
        assert db.scalar(select(versions.c.status))=='abandoned'


def test_v2_does_not_follow_symlinks_or_hardlinks(chat,tmp_path):
    import os
    import pytest
    from app.chat.workspace import WorkspaceError
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    root=tmp_path/'safe';root.mkdir();outside=tmp_path/'outside';outside.write_text('not captured')
    (root/'link').symlink_to(outside)
    snapshot=snapshot_store.capture(factory,cid,tid,root,'before')
    with factory() as db:
        item=snapshot_store.page(db,snapshot['version_id'])[0]
        assert item['kind']=='symlink' and item['object_id'] is None
    os.link(outside,root/'hardlink')
    with pytest.raises(WorkspaceError):snapshot_store.capture(factory,cid,tid,root,'after')


def test_result_pages_reauthorize_every_request(chat):
    from app.api.v1.admin_auth import require_session_user
    from app.main import app
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    with factory() as db:
        content_store.result(db,cid,tid,'output','s',0,b'private');db.commit()
    cursor=client.get(f'/api/v1/chat/turns/{tid}/results').json()['data']['resume_cursor']
    app.dependency_overrides[require_session_user]=lambda:{'id':'bob'}
    assert client.get(f'/api/v1/chat/turns/{tid}/results',params={'cursor':cursor}).status_code in (403,404)


def test_exact_block_diff_is_paged_and_scope_bound(chat,tmp_path):
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    root=tmp_path/'blocks';root.mkdir();(root/'file').write_bytes(b'a'*600000)
    before=snapshot_store.capture(factory,cid,tid,root,'before')
    (root/'file').write_bytes(b'a'*262144+b'b'*262144+b'a'*(600000-524288))
    after=snapshot_store.capture(factory,cid,tid,root,'after')
    key=hashlib.sha256(b'file').hexdigest()
    with factory() as db:
        from app.chat import service
        db.execute(insert(diffs).values(**service.identity(),turn_id=tid,before_hash=before['hash'],after_hash=after['hash'],
            payload=json.dumps({'format_version':2,'before_version':before['version_id'],'initial_version':before['version_id'],'after_version':after['version_id']})))
        db.commit()
    response=client.get(f'/api/v1/chat/turns/{tid}/files/{key}/blocks')
    assert response.status_code==200,response.text
    assert [item['block'] for item in response.json()['data']['items']]==[1]


def test_storage_observability_links_request_and_filters_content(chat,monkeypatch):
    from app.chat.schema import usage_events, task_trace_spans, task_traces
    from app.chat.observability import trace, storage_span
    from sqlalchemy import func
    client,factory=chat;cid=create(client);tid=queued(factory,cid)
    with factory() as db:
        trace(db,tid,'running',request_id='trusted-request')
        storage_span(db,tid,'result_commit',metadata={'storage_mode':'chunks_v2','text':'private','path':'private'})
        db.commit()
    response=client.get(f'/api/v1/chat/turns/{tid}/results',headers={'X-Chat-Client':'web'})
    assert response.status_code==200
    with factory() as db:
        event=db.execute(select(usage_events).where(usage_events.c.event_name=='chat.result_page')).mappings().one()
        assert event['parent_request_id']==response.headers['X-Request-ID']
        assert json.loads(event['properties'])=={'turn_id':tid}
        span=db.execute(select(task_trace_spans).where(task_trace_spans.c.span_name=='chat.result_commit')).mappings().one()
        assert json.loads(span['metadata'])=={'storage_mode':'chunks_v2'}
        count=db.scalar(select(func.count()).select_from(usage_events))
    assert client.get(f'/api/v1/chat/turns/{tid}/results').status_code==200
    with factory() as db:
        assert db.scalar(select(func.count()).select_from(usage_events))==count
        original=db.execute
        def failing(statement,*args,**kwargs):
            if 'task_trace_spans' in str(statement):raise RuntimeError('synthetic trace outage')
            return original(statement,*args,**kwargs)
        monkeypatch.setattr(db,'execute',failing)
        content_store.result(db,cid,tid,'output','s',0,b'preserved')
        storage_span(db,tid,'result_commit');db.commit()


def test_unknown_reconciliation_preserves_output_and_stores_authoritative_final(chat,tmp_path):
    from app.chat.admission import enqueue
    from app.chat import worker
    from app.chat.execution import run_claim,reconcile_unknown
    from test_chat_assistant_output import Peer
    client,factory=chat;cid=create(client);root=tmp_path/cid;root.mkdir()
    with factory() as db:
        row=enqueue(db,'alice',cid,'unknown','synthetic',settings.execution_limits());token=worker.claim(db,'worker')
    assert run_claim(factory,token,root,lambda _:Peer(True),usage_grace_seconds=0)=='unknown'
    final='final answer '*30000
    class FinalPeer(Peer):
        def read_turn(self,thread,turn):
            return {'id':turn,'status':'completed','items':[{'type':'agentMessage','phase':'final_answer','id':'final-one','text':final}]}
        def start_turn(self,*args):raise AssertionError('recovery must not start another execution')
    assert reconcile_unknown(factory,row['id'],root,lambda _:FinalPeer(True))
    assert not reconcile_unknown(factory,row['id'],root,lambda _:FinalPeer(True))
    cursor=None;parts=[]
    while True:
        response=client.get(f'/api/v1/chat/turns/{row["id"]}/results',params={'stream_id':'final',**({'cursor':cursor} if cursor else {})})
        assert response.status_code==200,response.text
        data=response.json()['data'];parts.extend(item['text'] for item in data['items']);cursor=data['next_cursor']
        if not cursor:break
    assert ''.join(parts)==final
    assert client.get(f'/api/v1/chat/turns/{row["id"]}/results').json()['data']['items'][0]['text']=='synthetic assistant output'
