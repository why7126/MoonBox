"""Single protocol-reader bridge. No automatic replay across lost process handles."""
import json
import queue
import time
from sqlalchemy import select, update
from app.chat import questions as store
from app.chat.question_schema import questions
from app.chat.app_server import ExecutorError

METHOD = 'item/tool/requestUserInput'
TOOL_NAME = 'moonbox_question'
SPEC = {'name': TOOL_NAME, 'description': 'Ask the user one to three non-secret questions and wait for their answers in this same turn. Use for decisions instead of asking in plain text. Never ask for passwords or tokens.',
    'inputSchema': {'type': 'object', 'properties': {'questions': {'type': 'array', 'minItems': 1, 'maxItems': 3,
        'items': {'type': 'object', 'properties': {'id': {'type': 'string'}, 'header': {'type': 'string'},
            'question': {'type': 'string'}, 'options': {'type': 'array', 'items': {'type': 'object',
                'properties': {'label': {'type': 'string'}, 'description': {'type': 'string'}},
                'required': ['label', 'description'], 'additionalProperties': False}}},
            'required': ['id', 'header', 'question', 'options'], 'additionalProperties': False}}},
        'required': ['questions'], 'additionalProperties': False}}


class QuestionBridge:
    def __init__(self, factory, token, server):
        self.factory, self.token, self.server = factory, token, server
        self.handled = set()

    def __call__(self, event):
        params = event.get('params', {})
        dynamic = event.get('method') == 'item/tool/call' and params.get('tool') == TOOL_NAME
        if event.get('method') != METHOD and not dynamic:
            return False
        request_id = event.get('id')
        if type(request_id) not in (str, int): raise ExecutorError('question_request_invalid')
        request_key = json.dumps(request_id)
        if request_key in self.handled:
            # Same live handle already responded. Never deliver twice.
            return True
        if dynamic:
            args = params.get('arguments')
            if not isinstance(args, dict) or params.get('namespace') is not None:
                raise ExecutorError('question_request_invalid')
            params = {**params, 'questions': args.get('questions')}
        try:
            with self.factory() as db:
                record = store.create(db, self.token, params, request_id)
        except ValueError:
            raise ExecutorError('question_request_invalid') from None
        try:
            while True:
                self._check_incoming(params, request_id, record['id'])
                deadline = getattr(self.server, 'question_deadline', None)
                if deadline is not None and time.monotonic() >= deadline:
                    self.server.interrupt(params['threadId'], params['turnId'])
                    raise ExecutorError('question_deadline_unknown')
                from app.chat.execution import owned
                with self.factory() as db:
                    turn, parent = owned(db, self.token)
                    store.authorize(db, parent['owner_id'], turn['id'], write=True)
                    scope = getattr(self.server, 'write_scope', 'read_only')
                    if scope != 'read_only':
                        from app.chat.policy import write_policy
                        from app.chat.execution import _retains_acknowledged_scope
                        if not _retains_acknowledged_scope(scope, write_policy(db, parent['owner_id'], parent)):
                            raise ExecutorError('write_permission_revoked')
                    store.refresh(db, turn)
                    row = db.execute(select(questions).where(questions.c.id == record['id'])).mappings().one()
                    state = row['status']
                    if state == 'answer_received':
                        count = db.execute(update(questions).where(questions.c.id == row['id'],
                            questions.c.status == 'answer_received', questions.c.worker_id == self.token['worker_id'])
                            .values(status='delivering', updated_at=store.service.now())).rowcount
                        answer = row['answer_json']
                        db.commit()
                        if not count: continue
                        # Persist uncertainty before the write. A crash never replays this handle.
                        result = json.loads(answer)
                        if dynamic: result = {'success': True, 'contentItems': [{'type': 'inputText', 'text': answer}]}
                        self.server.respond_tool(request_id, result)
                        with self.factory() as ack:
                            owned(ack, self.token)
                            ack.execute(update(questions).where(questions.c.id == row['id'], questions.c.status == 'delivering')
                                .values(status='delivered', updated_at=store.service.now()))
                            store.observe(ack, turn['id'], row['id'], 'delivered')
                            ack.commit()
                        self.handled.add(request_key)
                        return True
                    db.commit()
                if state != 'pending':
                    self.server.interrupt(params['threadId'], params['turnId'])
                    raise ExecutorError('question_' + state)
                # Leave protocol reads to AppServer; bounded queue failure stops this wait.
                if self.server.failure: raise ExecutorError(self.server.failure)
                time.sleep(.25)
        finally:
            with self.factory() as db:
                db.execute(update(questions).where(questions.c.id == record['id'], questions.c.status.in_(store.OPEN))
                    .values(status='unrecoverable', updated_at=store.service.now()))
                db.commit()

    def _check_incoming(self, params, request_id, question_id):
        # This is the same owning reader, not a second consumer thread. Preserve
        # interleaved ACKs/notifications while noticing a terminal during a wait.
        while True:
            try: event = self.server.incoming.get(timeout=0)
            except queue.Empty: break
            from app.chat.protocol_buffer import QUEUE_BYTES
            if len(self.server.pending) >= 128 or sum(len(json.dumps(v).encode()) for v in self.server.pending) + len(json.dumps(event).encode()) > QUEUE_BYTES:
                raise ExecutorError('executor_buffer_limit')
            self.server.pending.append(event)
        for event in self.server.pending:
            data = event.get('params', {})
            if data.get('threadId') != params['threadId']: continue
            if event.get('method') == 'serverRequest/resolved' and data.get('requestId') == request_id:
                with self.factory() as db:
                    db.execute(update(questions).where(questions.c.id == question_id, questions.c.status == 'pending').values(status='expired', updated_at=store.service.now()))
                    db.commit()
                raise ExecutorError('question_expired')
            if event.get('method') == 'turn/completed' and data.get('turn', {}).get('id') == params['turnId']:
                raise ExecutorError('question_turn_ended')
