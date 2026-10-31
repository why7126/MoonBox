"""Loopback-only synthetic API + real components, optional pinned model execution."""
import json
import os
from pathlib import Path
import queue
import subprocess
import tempfile
import threading
from collections import deque
import pytest
import uvicorn
from sqlalchemy import select, update
from fastapi import Request
from fastapi.responses import JSONResponse
from app.main import app
from app.chat import service
from app.chat.schema import turns, conversations
from app.chat.question_schema import questions
from app.chat.question_bridge import QuestionBridge
from test_chat import chat, create, queued, governance, allow_governed_write
from test_chat_questions import RAW


def main():
    with tempfile.TemporaryDirectory(prefix='moonbox-question-', dir='/private/tmp') as folder:
        root = Path(folder); mp = pytest.MonkeyPatch()
        fixture = chat.__wrapped__(root, mp); client, factory = next(fixture)
        scenes = []; errors = []; jobs = []
        for state in ('pending', 'delivered', 'expired', 'cancelled', 'unrecoverable'):
            cid = create(client); tid = queued(factory, cid, 'running')
            token = {'turn_id': tid, 'conversation_id': cid, 'worker_id': 'browser-question', 'generation': 0}
            with factory() as db:
                db.execute(update(turns).where(turns.c.id == tid).values(worker_id=token['worker_id'], executor_turn_id='executor-turn'))
                db.execute(update(conversations).where(conversations.c.id == cid).values(thread_id='thread')); db.commit()
                from app.chat.questions import create as create_q
                record = create_q(db, token, {'threadId': 'thread', 'turnId': 'executor-turn', 'questions': RAW}, state)
                if state != 'pending':
                    db.execute(update(questions).where(questions.c.id == record['id']).values(status=state));db.commit()
            scenes.append({'state': state, 'turn_id': tid, 'id': record['id']})
        live = {'state': 'not_started'}
        def run_live():
            try:
                from app.chat.container_server import ContainerAppServer, persistent_container_server
                from app.chat.admission import enqueue
                from app.chat import worker
                from app.chat.execution import run_claim
                from test_chat_local_execution import LIMITS
                run = os.environ['QUESTION_DOCKER_RUN']; expires = os.environ['QUESTION_DOCKER_EXPIRES']
                original = ContainerAppServer.recovery_labels
                # Only this disposable harness adds the already registered test labels.
                mp.setattr(ContainerAppServer, 'recovery_labels', lambda self: original(self) + [
                    '--label', 'moonbox.temp.managed=true', '--label', 'moonbox.temp.run='+run,
                    '--label', 'moonbox.temp.expires='+expires])
                facts = governance.__wrapped__(root, mp)
                cid = create(client); allow_governed_write(client, cid, facts)
                work = root/cid; work.mkdir(mode=0o700); subprocess.run(['git','init','-q',str(work)],check=True)
                runtime = root/'runtime'; runtime.mkdir(mode=0o700)
                prompt = ('Bounded integration test. Ask exactly one structured non-secret question using request_user_input or moonbox_question: '
                          'choose ALPHA or BETA, with id choice. Wait for the actual user answer. Then write only choice.txt containing the chosen word '
                          'and newline. Do not guess, do not inspect files, do not commit. Reply with the chosen word.')
                with factory() as db:
                    row = enqueue(db, 'alice', cid, 'live-question', prompt, LIMITS, question_capable=True)
                    token = worker.claim(db, 'live-question-worker')
                live.update(state='running', turn_id=row['id'], conversation_id=cid)
                def server(path): return persistent_container_server(path, runtime, Path.home()/'.codex/auth.json')
                result = run_claim(factory, token, work, server, max_seconds=180)
                with factory() as db:
                    status = list(db.scalars(select(questions.c.status).where(questions.c.turn_id == row['id'])))
                    code = db.scalar(select(turns.c.error_code).where(turns.c.id == row['id']))
                output = (work/'choice.txt').read_text().strip() if (work/'choice.txt').exists() else None
                live.update(state=result, question_states=status, answer_matches=output == 'BETA', error_code=code)
            except Exception as exc:
                live.update(state='failed', error_type=type(exc).__name__)
        app.middleware_stack = None  # Disposable fixture app only.
        @app.middleware('http')
        async def scenes_route(request: Request, call_next):
            if request.url.path == '/api/fixture/questions': return JSONResponse({'scenes': scenes, 'live': live})
            if request.url.path == '/api/fixture/questions/live' and request.method == 'POST':
                if live['state'] == 'not_started':
                    job = threading.Thread(target=run_live); jobs.append(job); job.start();live['state']='starting'
                return JSONResponse(live)
            return await call_next(request)
        try: uvicorn.run(app, host='127.0.0.1', port=39050, lifespan='off', log_level='error')
        finally:
            for job in jobs: job.join(200)
            try: next(fixture)
            except StopIteration: pass
            mp.undo()

if __name__ == '__main__': main()
