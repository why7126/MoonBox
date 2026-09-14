import json
from pathlib import Path
from app.chat.tool_record import tool_payload


def test_tool_pair_preserves_facts_and_redacts_credentials():
    started = {}; root = Path('/synthetic/workspace')
    item = dict(id='tool-1', type='commandExecution', command='echo "hello"', cwd=str(root), status='inProgress')
    first = tool_payload(item, 'started', 'turn', root, started, clock=lambda: 10)
    last = tool_payload(dict(item, status='failed', exitCode=7, aggregatedOutput='password="private value"\nAuthorization: Bearer private-token\n/Users/private/project\n'+str(root)), 'completed', 'turn', root, started, clock=lambda: 10.5)
    assert first['arguments']['cwd'] == '[工作区]'
    assert last['duration_ms'] == 500 and last['exit_code'] == 7
    assert last['status'] == 'failed' and not started
    assert 'private' not in last['result'] and '[工作区]' in last['result']


def test_record_bounds_unknown_fields_and_missing_start():
    record = tool_payload(dict(id='t', type='commandExecution', command='汉'*10000, aggregatedOutput='汉'*10000, auth='never capture', durationMs=-1), 'completed', 'turn', '/work', {})
    assert record['truncated'] and 'duration_ms' not in record and 'auth' not in record
    assert len(json.dumps(record,ensure_ascii=False).encode()) < 65536
    files = tool_payload(dict(id='t',type='fileChange',changes=[{'path':'汉'*8000}]*50), 'completed','turn','/work',{})
    assert files['truncated'] and len(json.dumps(files,ensure_ascii=False).encode()) < 65536


def test_executor_duration_and_empty_result_are_not_inferred():
    record = tool_payload(dict(id='t',type='commandExecution',aggregatedOutput='',durationMs=0,exitCode=0), 'completed','turn','/work',{})
    assert record['result'] == '' and record['duration_ms'] == 0 and record['timing_source'] == 'executor'
