"""Disposable UI state matrix: synthetic rows, real routes/auth/transactions, no model."""
import json
import tempfile
from pathlib import Path
import pytest
import uvicorn
from fastapi import FastAPI
from sqlalchemy import insert, update, text
from test_chat import chat, create, queued
from app.main import app as original
from app.chat.api import router
from app.governance.scope import authorize
from app.verification.acceptance_state import AcceptanceState
from app.verification.acceptance_schema import operations, results


def main():
    with tempfile.TemporaryDirectory(prefix='moonbox-acceptance-ui-') as folder, pytest.MonkeyPatch.context() as patch:
        root=Path(folder).resolve()
        private=root/'private';private.mkdir(mode=0o700)
        patch.setenv('MOONBOX_GOVERNANCE_STATE_ROOT',str(private))
        change=root/'openspec/changes/synthetic-change';change.mkdir(parents=True)
        (change/'trace.md').write_text('---\nstatus: in_progress\n---\n')
        fixture=chat.__wrapped__(root,patch);client,factory=next(fixture)
        patch.setenv('MOONBOX_CHAT_REPOSITORY_BINDINGS',json.dumps([{'id':'repo','space_id':'space','governance_root':str(root)}]))
        with factory() as db:binding=authorize(db,'alice','space','repo').binding_revision
        state=AcceptanceState(factory);samples=[]
        for stage,status,cleanup in [('准备环境','preparing','active'),('环境就绪','ready','active'),
            ('执行验收','running','active'),('局部阻塞','blocked','released'),('回收资源','passed','releasing'),
            ('已释放','passed','released'),('回收失败','passed','cleanup_failed')]:
            cid=create(client);tid=queued(factory,cid,status='completed')
            item=state.create(actor='alice',space='space',repository='repo',conversation=cid,turn=tid,
                change='synthetic-change',request_key='sample',binding=binding,input_digest='a'*64,
                plan={'checks':[{'id':'AC-001','inputs':['src/app.py']},{'id':'AC-002','inputs':['src/db.py']}]})
            with factory.begin() as db:
                db.execute(update(operations).where(operations.c.id==item['id']).values(status=status,cleanup_state=cleanup,
                    reason_code='worker_interrupted' if status=='blocked' else None))
                if status=='passed':
                    db.execute(update(results).where(results.c.attempt_id==item['attempt_id']).values(
                        status='passed',evidence_json=json.dumps({'kind':'command','digest':'d'*64})))
            samples.append({'stage':stage,'conversation_id':cid,'operation_id':item['id']})
            if cleanup=='released' and status=='passed':
                from app.verification.acceptance_archive import publish
                publish(factory,item['id'])
                with factory.begin() as db:
                    db.execute(update(results).where(results.c.attempt_id==item['attempt_id']).values(updated_at='2000-01-01T00:00:00+00:00'))
        app=FastAPI();app.include_router(router);app.dependency_overrides.update(original.dependency_overrides)
        @app.get('/api/v1/acceptance-test/context')
        def context():return {'samples':samples,'sample':'synthetic-state-real-api-no-model'}
        try:uvicorn.run(app,host='127.0.0.1',port=39048,log_level='warning')
        finally:
            try:next(fixture)
            except StopIteration:pass


if __name__=='__main__':main()
