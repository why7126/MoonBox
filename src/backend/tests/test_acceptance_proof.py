"""Proof negatives are synthetic fixtures, never product acceptance samples."""
import sqlite3
import pytest
from app.verification.acceptance_proof import read_proof


@pytest.fixture
def proof_db(tmp_path):
    path=tmp_path/'proof.db'
    with sqlite3.connect(path) as db:
        db.executescript('''
        CREATE TABLE verification_operations(id,source_turn_id,conversation_id,attempt_id,input_digest,status,cleanup_state,resume_count,cancel_requested);
        CREATE TABLE chat_turns(id,conversation_id,status,generation);
        CREATE TABLE moonbox_execution_receipts(turn_id,executor_closed,files_collected);
        CREATE TABLE verification_ac_results(attempt_id,status);
        CREATE TABLE verification_tool_waits(operation_id,source_turn_id,state,generation);
        CREATE TABLE verification_result_deliveries(operation_id,state,attempt_id,input_digest,target_turn_id);
        CREATE TABLE chat_usage_reservations(turn_id,tokens,actual_tokens);
        INSERT INTO chat_usage_reservations VALUES('turn',100,20);
        INSERT INTO verification_operations VALUES('op','turn','chat','attempt','digest','passed','released',0,0);
        INSERT INTO chat_turns VALUES('turn','chat','completed',1);
        INSERT INTO moonbox_execution_receipts VALUES('turn',1,1);
        INSERT INTO verification_ac_results VALUES('attempt','passed');
        INSERT INTO verification_tool_waits VALUES('op','turn','delivered',1);
        ''')
    return path


def test_live_native_proof_needs_ack_and_collection(proof_db):
    before=proof_db.read_bytes()
    assert read_proof(proof_db,'turn','op','live')['verified']
    assert proof_db.read_bytes()==before
    with sqlite3.connect(proof_db) as db:db.execute("UPDATE verification_tool_waits SET state='dispatching'")
    assert not read_proof(proof_db,'turn','op','live')['verified']


@pytest.mark.parametrize('mutation',[
    "UPDATE moonbox_execution_receipts SET files_collected=0",
    "UPDATE verification_operations SET cleanup_state='cleanup_failed'",
    "UPDATE verification_operations SET conversation_id='other'",
    "UPDATE verification_tool_waits SET generation=0",
    "UPDATE verification_ac_results SET status='pending'",
])
def test_native_proof_rejects_incomplete_or_wrong_owner(proof_db,mutation):
    with sqlite3.connect(proof_db) as db:db.execute(mutation)
    assert not read_proof(proof_db,'turn','op','live')['verified']


def test_continuation_requires_same_attempt_and_original_failure(proof_db):
    with sqlite3.connect(proof_db) as db:
        db.executescript('''UPDATE verification_operations SET resume_count=1;
        UPDATE chat_turns SET status='failed';
        INSERT INTO chat_turns VALUES('next','chat','completed',1);
        INSERT INTO moonbox_execution_receipts VALUES('next',1,1);
        INSERT INTO verification_result_deliveries VALUES('op','consumed','attempt','digest','next');''')
    assert read_proof(proof_db,'turn','op','continuation')['verified']
    with sqlite3.connect(proof_db) as db:db.execute("UPDATE chat_usage_reservations SET actual_tokens=NULL")
    assert not read_proof(proof_db,'turn','op','continuation')['verified']
    with sqlite3.connect(proof_db) as db:db.execute("UPDATE chat_usage_reservations SET actual_tokens=20")
    with sqlite3.connect(proof_db) as db:db.execute("UPDATE verification_result_deliveries SET attempt_id='old'")
    assert not read_proof(proof_db,'turn','op','continuation')['verified']


def test_stop_does_not_count_as_recovered_or_continued(proof_db):
    with sqlite3.connect(proof_db) as db:
        db.execute("UPDATE chat_turns SET status='stopped'")
        db.execute("UPDATE verification_operations SET status='cancelled',cancel_requested=1")
    assert read_proof(proof_db,'turn','op','stopped','cancelled')['verified']
    assert not read_proof(proof_db,'turn','op','recovered','cancelled')['verified']
    assert not read_proof(proof_db,'turn','op','continuation','cancelled')['verified']
