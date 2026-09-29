import json
from sqlalchemy import select,update
from app.chat.schema import usage_events,task_traces,task_trace_spans
from app.governance.capture_observability import trace
from app.chat.observability import prune
from test_chat import chat
from test_governance_writer import writing


def test_capture_behavior_only_on_explicit_web_action(chat,writing):
    client,factory=chat
    query={'space_id':'space','repository_id':'repo'}
    draft=client.post('/api/v1/requirement-center/capture-drafts',params=query).json()['data']
    url='/api/v1/requirement-center/capture-drafts/'+draft['id']
    first=client.patch(url,params=query,json={'expected_revision':1,'text':'private description'})
    assert first.status_code==200
    with factory() as db:
        assert not db.execute(select(usage_events).where(usage_events.c.event_name=='capture.review_save')).all()
    headers={'X-Chat-Client':'web','X-Behavior-Event-ID':'capture-action-1','X-Behavior-Trace-ID':'capture-chain-1'}
    response=client.patch(url,params=query,headers=headers,json={'expected_revision':2,'text':'private description'})
    assert response.status_code==200
    with factory() as db:
        row=db.execute(select(usage_events).where(usage_events.c.event_name=='capture.review_save')).mappings().one()
        assert row['behavior_event_id']=='capture-action-1'
        assert json.loads(row['properties'])=={'behavior_trace_id':'capture-chain-1'}
        assert 'private description' not in str(row)
        assert not db.execute(select(task_traces)).all()


def test_capture_trace_retention_is_independent_of_business_sources(writing):
    from app.governance import capture_drafts
    from app.governance.capture_schema import drafts
    factory,project,*_=writing
    with factory() as db:
        draft=capture_drafts.create(db,'alice',project)
        trace(db,'opaque-task','queued',actor='alice',request_id='opaque-request')
        trace(db,'opaque-task','ready',actor='alice')
        trace(db,'invalid/task','ready')
        assert len(db.execute(select(task_traces)).all())==1
        db.execute(update(task_traces).values(finished_at='2000-01-01T00:00:00+00:00'));db.commit()
        prune(db)
        assert not db.execute(select(task_traces)).all()
        assert not db.execute(select(task_trace_spans)).all()
        assert db.scalar(select(drafts.c.id))==draft['id']


def test_trace_storage_failure_does_not_lose_accepted_organization(writing,caplog):
    from sqlalchemy import event
    from sqlalchemy.exc import OperationalError
    from app.governance import capture_drafts,capture_organizer
    factory,project,*_=writing
    with factory() as db:
        draft=capture_drafts.create(db,'alice',project)
        capture_drafts.save(db,'alice',project,draft['id'],1,{'text':'合成私有反馈','media_ids':[],'candidates':[]})
        engine=db.get_bind()
        def fail_trace(conn,cursor,statement,parameters,context,executemany):
            if statement.lstrip().lower().startswith('insert into task_traces'):
                raise OperationalError('synthetic observation failure',{},Exception('synthetic'))
        event.listen(engine,'before_cursor_execute',fail_trace)
        try:task=capture_organizer.start(db,'alice',project,draft['id'],2)
        finally:event.remove(engine,'before_cursor_execute',fail_trace)
        assert task['state']=='pending'
        assert capture_organizer.status(db,'alice',project,draft['id'],task['id'])['state']=='pending'
        assert 'capture.trace_unavailable' in caplog.text
        assert '合成私有反馈' not in caplog.text
