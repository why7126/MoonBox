"""User-input business state. Never interpret answers as methods or new turns."""
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from sqlalchemy import insert, select, update
from app.chat import service
from app.chat.question_schema import questions
from app.chat.schema import turns, conversations

OPEN = ('pending', 'answer_received', 'delivering')


def normalize_questions(raw):
    if not isinstance(raw, list) or not 1 <= len(raw) <= 3:
        raise ValueError('invalid_question_count')
    result = []
    for q in raw:
        if not isinstance(q, dict) or q.get('isSecret', False):
            raise ValueError('secret_questions_unsupported')
        item = {}
        for key, limit in (('id', 80), ('header', 100), ('question', 2000)):
            value = q.get(key)
            if not isinstance(value, str) or not value.strip() or len(value) > limit:
                raise ValueError('invalid_question')
            item[key] = value
        if item['id'] in {v['id'] for v in result}:
            raise ValueError('duplicate_question')
        options = q.get('options') or []
        if not isinstance(options, list) or len(options) > 8:
            raise ValueError('invalid_options')
        item['options'] = []
        for index, option in enumerate(options):
            if not isinstance(option, dict): raise ValueError('invalid_option')
            label, desc = option.get('label'), option.get('description')
            if not isinstance(label, str) or not label.strip() or len(label) > 200 or not isinstance(desc, str) or len(desc) > 1000:
                raise ValueError('invalid_option')
            item['options'].append({'id': str(index), 'label': label, 'description': desc})
        # Supplemental input is a product feature; credentials are explicitly excluded.
        item['allow_text'] = True
        result.append(item)
    return result


def public(row):
    return {key: row[key] for key in ('id', 'turn_id', 'status', 'version', 'expires_at', 'created_at')} | {
        'questions': json.loads(row['questions_json'])}


def lock_turn(db, tid):
    # Same lock as stop/terminal transitions; avoids answer-vs-stop TOCTOU.
    db.execute(update(turns).where(turns.c.id == tid).values(updated_at=service.now()))


def authorize(db, actor, tid, *, write=False):
    row = service.turn(db, actor, tid)
    parent = service.conversation(db, actor, row['conversation_id'])
    if write:
        from app.chat.policy import write_policy
        policy = write_policy(db, actor, parent)
        if parent['archived'] or policy['reason_code'] in (
            'governance_object_read_only', 'governance_facts_invalid', 'space_forbidden',
            'actor_not_writer', 'governance_candidate_forbidden', 'governance_candidate_invalid'):
            raise service.ChatError(2501, '当前会话不可回答', 403)
    return row, parent


def refresh(db, turn):
    stamp = service.now()
    status = turn['status']
    if status not in ('connecting', 'running'):
        final = 'cancelled' if status in ('stopping', 'stopped') else 'unrecoverable'
        db.execute(update(questions).where(questions.c.turn_id == turn['id'], questions.c.status.in_(OPEN))
                   .values(status=final, updated_at=stamp))
    db.execute(update(questions).where(questions.c.turn_id == turn['id'],
        questions.c.status.in_(('pending', 'answer_received')), questions.c.expires_at <= stamp)
        .values(status='expired', updated_at=stamp))


def list_questions(db, actor, tid):
    turn, _ = authorize(db, actor, tid)
    refresh(db, turn)
    rows = list(db.execute(select(questions).where(questions.c.turn_id == tid)
                          .order_by(questions.c.created_at, questions.c.id)).mappings())
    db.commit()
    return {'items': [public(row) for row in rows], 'turn_status': turn['status']}


def encode_answer(row, answers):
    definitions = json.loads(row['questions_json'])
    if not isinstance(answers, dict) or set(answers) != {q['id'] for q in definitions}:
        raise service.ChatError(2520, '请完整回答当前问题', 422)
    wire = {}
    for q in definitions:
        value = answers[q['id']]
        if not isinstance(value, dict) or set(value) - {'option_id', 'text'}:
            raise service.ChatError(2520, '答案格式不正确', 422)
        selected, text = value.get('option_id'), value.get('text', '')
        if not isinstance(text, str) or len(text) > 4000:
            raise service.ChatError(2520, '补充说明不能超过4000字', 422)
        parts = []
        if selected is not None:
            option = next((o for o in q['options'] if o['id'] == selected), None)
            if option is None: raise service.ChatError(2520, '选项已变化', 422)
            parts.append(option['label'])
        if text.strip(): parts.append(text.strip())
        if not parts: raise service.ChatError(2520, '请选择选项或补充说明', 422)
        wire[q['id']] = {'answers': parts}
    return json.dumps({'answers': wire}, ensure_ascii=False, sort_keys=True)


def submit(db, actor, tid, qid, version, key, answers, request_id=None):
    lock_turn(db, tid)
    turn, parent = authorize(db, actor, tid, write=True)
    refresh(db, turn)
    row = db.execute(select(questions).where(questions.c.id == qid, questions.c.turn_id == tid)).mappings().first()
    if not row: raise service.ChatError(2502, '问题不存在或无权访问', 404)
    encoded = encode_answer(row, answers)
    if version != row['version']: raise service.ChatError(2521, '问题已变化，请刷新', 409)
    if row['idempotency_key'] is not None:
        if row['idempotency_key'] == key and row['answer_json'] == encoded:
            db.commit()
            return public(row)
        raise service.ChatError(2521, '问题已经收到其他答案', 409)
    if (row['status'] != 'pending' or turn['status'] not in ('connecting', 'running') or
            parent['active_turn_id'] != tid or row['generation'] != turn['generation'] or row['worker_id'] != turn['worker_id']):
        db.commit()
        raise service.ChatError(2521, '问题已结束，答案未发送', 409)
    changed = db.execute(update(questions).where(questions.c.id == qid, questions.c.status == 'pending')
        .values(status='answer_received', answer_json=encoded, idempotency_key=key, updated_at=service.now())).rowcount
    if not changed: raise service.ChatError(2521, '问题状态已变化', 409)
    observe(db, tid, qid, 'answer_received', request_id)
    db.commit()
    return public(db.execute(select(questions).where(questions.c.id == qid)).mappings().one())


def observe(db, tid, qid, stage, request_id=None):
    from app.chat.observability import storage_span
    storage_span(db, tid, 'question', result=stage,
                 metadata={'turn_id': tid, 'question_id': qid, 'request_id': request_id})


def create(db, token, params, request_id):
    from app.chat.execution import owned
    row, parent = owned(db, token)
    if row['status'] not in ('connecting', 'running') or parent['archived']:
        raise service.ChatError(2521, '原轮次已停止', 409)
    if params.get('threadId') != parent['thread_id']:
        raise ValueError('question_thread_mismatch')
    executor_turn = params.get('turnId')
    if not isinstance(executor_turn, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,96}', executor_turn):
        raise ValueError('question_turn_invalid')
    if row['executor_turn_id'] and row['executor_turn_id'] != executor_turn:
        raise ValueError('question_turn_mismatch')
    payload = normalize_questions(params.get('questions'))
    request_key = hashlib.sha256(json.dumps(request_id).encode()).hexdigest()
    previous = db.execute(select(questions).where(questions.c.turn_id == row['id'],
        questions.c.generation == token['generation'], questions.c.request_key == request_key)).mappings().first()
    if previous:
        if previous['questions_json'] != json.dumps(payload, ensure_ascii=False) or previous['executor_turn_id'] != executor_turn:
            raise ValueError('question_request_conflict')
        return dict(previous)
    from app.chat.settings import question_timeout
    identity = service.identity()
    record = dict(**identity, turn_id=row['id'], worker_id=token['worker_id'], generation=token['generation'],
        request_key=request_key, executor_turn_id=executor_turn, status='pending', version=1,
        questions_json=json.dumps(payload, ensure_ascii=False),
        expires_at=(datetime.now(timezone.utc)+timedelta(seconds=question_timeout())).isoformat(timespec='seconds'))
    db.execute(insert(questions).values(**record))
    observe(db, row['id'], identity['id'], 'pending')
    db.commit()
    return record


def close_open(db, tid, status='unrecoverable', token=None):
    statement = update(questions).where(questions.c.turn_id == tid, questions.c.status.in_(OPEN))
    if token:
        statement = statement.where(questions.c.generation == token['generation'], questions.c.worker_id == token['worker_id'])
    db.execute(statement.values(status=status, updated_at=service.now()))
