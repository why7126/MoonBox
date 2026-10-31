import json
import pytest
from sqlalchemy import insert, text
from test_chat import chat, create, queued
from app.chat import service
from app.chat.schema import events
from app.main import app
from app.api.v1.admin_auth import require_session_user


def test_summary_reads_last_usage_beyond_replay_page_and_checks_owner(chat):
    client, factory = chat
    tid = queued(factory, create(client), 'completed')
    with factory() as db:
        for i in range(1, 405):
            kind = 'execution.usage' if i in (1, 404) else 'execution.tool'
            payload = {'total_tokens': i, 'private_text': 'not returned'} if kind.endswith('usage') else {}
            db.execute(insert(events).values(**service.identity(), turn_id=tid, sequence=i,
                source_id=str(i), event_type=kind, payload=json.dumps(payload)))
        db.commit()
    response = client.get(f'/api/v1/chat/turns/{tid}/summary')
    assert response.status_code == 200
    data = response.json()['data']
    assert data['event_sequence'] == 404
    assert data['tool_count'] == 402
    assert data['usage'] == {'total_tokens': 404}
    app.dependency_overrides[require_session_user] = lambda: {'id': 'bob'}
    assert client.get(f'/api/v1/chat/turns/{tid}/summary').status_code == 404


@pytest.mark.parametrize('payload', [None, '{}', '[]', '{"total_tokens":null}', '{"total_tokens":-1,"input_tokens":true,"duration_ms":1e999}'])
def test_missing_or_invalid_usage_is_not_zero(chat, payload):
    client, factory = chat
    tid = queued(factory, create(client), 'unknown')
    if payload is not None:
        with factory() as db:
            db.execute(insert(events).values(**service.identity(), turn_id=tid, sequence=1,
                source_id='usage', event_type='execution.usage', payload=payload))
            db.commit()
    data = client.get(f'/api/v1/chat/turns/{tid}/summary').json()['data']
    assert data['status'] == 'unknown'
    assert data['usage'] == {}
    with factory() as db:
        db.execute(text("UPDATE admin_spaces SET status='FROZEN'")); db.commit()
    assert client.get(f'/api/v1/chat/turns/{tid}/summary').status_code == 403
