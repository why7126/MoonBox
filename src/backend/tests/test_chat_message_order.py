"""SQL and real ASGI pipeline regressions; also runnable without pytest/httpx."""
import asyncio
import json
import os
import unittest
from unittest.mock import patch
from urllib.parse import urlencode
from sqlalchemy import create_engine, insert, select, update, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.api.v1.admin_auth import require_session_user
from app.db.session import get_db
from app.chat import assistant_output as output
from app.chat.schema import migrate, conversations, turns, messages, events

class MessageOrderTests(unittest.TestCase):
    def setUp(self):
        database = os.environ.get('CHAT_TEST_DATABASE_URL')
        self.engine = (create_engine(database) if database else
                       create_engine('sqlite://', poolclass=StaticPool, connect_args={'check_same_thread': False}))
        with self.engine.begin() as db:
            for sql in [
                "CREATE TABLE admin_users (id VARCHAR(64) PRIMARY KEY, status VARCHAR(32) NOT NULL DEFAULT '正常', deleted_at VARCHAR(64))",
                'CREATE TABLE admin_spaces (id VARCHAR(64) PRIMARY KEY, owner_id VARCHAR(64), status VARCHAR(24), deleted_at VARCHAR(32), expires_at VARCHAR(32))',
                'CREATE TABLE admin_space_members (id VARCHAR(64) PRIMARY KEY, space_id VARCHAR(64), user_id VARCHAR(64), role VARCHAR(32))',
                "INSERT INTO admin_users (id) VALUES ('alice'), ('bob')",
                "INSERT INTO admin_spaces (id,owner_id,status) VALUES ('space','alice','ACTIVE')"]:
                db.execute(text(sql))
        migrate(self.engine); self.factory = sessionmaker(self.engine)
        self.audit_factory = patch("app.chat.api.get_session_factory", return_value=self.factory)
        self.audit_factory.start()
        self.env = patch.dict('os.environ', {'MOONBOX_CHAT_REPOSITORIES': '[{"id":"repo","space_id":"space"}]'})
        self.env.start(); self.stamp = '2026-10-21T00:00:00+00:00'
        with self.factory() as db:
            for cid in ('conversation', 'other'):
                db.execute(insert(conversations).values(id=cid, created_at=self.stamp, updated_at=self.stamp,
                    owner_id='alice', space_id='space', repository_id='repo', title='Synthetic'))
            db.commit()
        def dependency():
            with self.factory() as db: yield db
        app.dependency_overrides[get_db] = dependency
        app.dependency_overrides[require_session_user] = lambda: {'id': 'alice'}

    def tearDown(self):
        app.dependency_overrides.clear(); self.audit_factory.stop(); self.env.stop()
        from app.chat.schema import CHAT_TABLES
        for table in reversed(CHAT_TABLES):
            table.drop(self.engine)
        with self.engine.begin() as db:
            for name in ('admin_space_members', 'admin_spaces', 'admin_users'):
                db.execute(text('DROP TABLE ' + name))
        self.engine.dispose()

    def turn(self, tid, delay=1):
        with self.factory() as db:
            db.execute(insert(turns).values(id=tid, created_at=self.stamp, updated_at=self.stamp,
                conversation_id='conversation', client_request_id=tid, status='stopped', prompt='synthetic'))
            db.execute(insert(messages).values(id='user-' + tid, turn_id=tid, role='user', content='synthetic question',
                created_at=f'2026-10-21T00:00:{delay:02d}+00:00', updated_at=self.stamp))
            db.commit()

    def event(self, tid, seq=1, final=False):
        with self.factory() as db:
            db.execute(insert(events).values(id=f'event-{tid}-{seq}', turn_id=tid, sequence=seq,
                source_id=f'assistant:final:{seq}' if final else str(seq), event_type='execution.output',
                payload=json.dumps({'text': 'synthetic answer', 'item_id': 'answer'}),
                created_at='2026-10-21T00:00:30+00:00', updated_at=self.stamp)); db.commit()

    def api(self, params=None, cid='conversation'):
        async def request():
            sent = []
            received = False
            async def receive():
                nonlocal received
                if received: await asyncio.Event().wait()
                received = True
                return {'type': 'http.request', 'body': b'', 'more_body': False}
            async def send(value): sent.append(value)
            task = asyncio.create_task(app({'type': 'http', 'asgi': {'version': '3.0'}, 'http_version': '1.1', 'method': 'GET',
                'scheme': 'http', 'path': f'/api/v1/chat/conversations/{cid}/messages',
                'query_string': urlencode(params or {}).encode(), 'root_path': '', 'headers': [],
                'client': ('127.0.0.1', 1), 'server': ('test', 80)}, receive, send))
            # Bound the transport runner and keep its loop responsive to worker callbacks.
            for _ in range(500):
                if task.done(): break
                await asyncio.sleep(0.01)
            await asyncio.wait_for(task, timeout=1)
            return next(x['status'] for x in sent if x['type'] == 'http.response.start'), json.loads(
                b''.join(x.get('body', b'') for x in sent if x['type'] == 'http.response.body'))
        return asyncio.run(request())

    def data(self, params=None):
        status, body = self.api(params); self.assertEqual(status, 200, body); return body['data']

    def test_same_and_cross_second_order_and_time(self):
        for delay in (0, 1, 8): self.turn(f'turn-{delay}', delay); self.event(f'turn-{delay}')
        items = self.data()['items']
        for delay in (0, 1, 8):
            pair = [x for x in reversed(items) if x['turn_id'] == f'turn-{delay}']
            self.assertEqual([x['role'] for x in pair], ['user', 'assistant'])
            self.assertEqual(pair[1]['time_source'], 'output_event')
            self.assertEqual(pair[1]['display_time'], '2026-10-21T00:00:30+00:00')

    def test_cursor_pages_total_order_and_materialization(self):
        for tid in ('turn-a', 'turn-Z', 'turn-b'): self.turn(tid); self.event(tid)
        expected = self.data()['items']; cursor = None; found = []
        for _ in range(10):
            params = {'page_size': 1}
            if cursor: params['before'] = cursor
            data = self.data(params); self.assertEqual(data, self.data(params)); found.extend(data['items'])
            if not data['has_more']: break
            cursor = data['next_cursor']
        self.assertEqual([r['id'] for r in found], [r['id'] for r in expected])
        self.assertEqual(len({r['id'] for r in found}), 6)
        with self.factory() as db:
            for tid in ('turn-a', 'turn-Z', 'turn-b'): output.persist_output(db, tid)
            db.commit()
        self.assertEqual([r['order_key'] for r in self.data()['items']], [r['order_key'] for r in expected])
        self.assertEqual([r['id'] for r in self.data({'page': 2, 'page_size': 2})['items']], [r['id'] for r in expected[2:4]])

    def test_legacy_unknown_and_first_save_survive_recovery(self):
        self.turn('legacy')
        with self.factory() as db:
            db.execute(insert(messages).values(id='old-answer', turn_id='legacy', role='assistant', content='old',
                created_at=self.stamp, updated_at=self.stamp)); db.commit()
        legacy = self.data()['items'][0]
        self.assertIsNone(legacy['display_time']); self.assertEqual(legacy['time_source'], 'legacy_unknown')
        self.assertEqual(legacy['created_at'], self.stamp)
        self.turn('new'); self.event('new')
        with self.factory() as db:
            with patch('app.chat.service.now', return_value='2026-10-21T00:00:31+00:00'): output.persist_output(db, 'new')
            with patch('app.chat.service.now', return_value='2026-10-21T00:00:40+00:00'): output.persist_output(db, 'new', 'recovered')
            db.commit()
            saved = db.execute(select(messages).where(messages.c.id == output.message_id('new'))).mappings().one()
            self.assertEqual(saved['created_at'], '2026-10-21T00:00:31+00:00')
            self.assertEqual(saved['updated_at'], '2026-10-21T00:00:40+00:00'); self.assertEqual(saved['content'], 'recovered')

    def test_late_output_rescan(self):
        for tid in ('turn-a', 'turn-b', 'turn-c'): self.turn(tid)
        first = self.data({'page_size': 1}); self.event('turn-c')
        older = self.data({'page_size': 10, 'before': first['next_cursor']})
        self.assertFalse(any(r['role'] == 'assistant' for r in older['items']))
        self.assertTrue(any(r['role'] == 'assistant' for r in self.data()['items']))

    def test_cursor_validation_and_authorization(self):
        self.turn('turn-a'); self.event('turn-a'); cursor = self.data({'page_size': 1})['next_cursor']
        for value in ('!', 'x' * 1025, '', 'WzJd'): self.assertEqual(self.api({'before': value})[0], 422)
        self.assertEqual(self.api({'before': cursor}, cid='other')[0], 422)
        app.dependency_overrides[require_session_user] = lambda: {'id': 'bob'}
        self.assertEqual(self.api({'before': cursor})[0], 404)

    def test_state_and_partial_output_preserved(self):
        self.turn('turn-a'); self.event('turn-a'); original = [x['order_key'] for x in self.data()['items']]
        for status in ('unknown', 'stopped', 'completed'):
            with self.factory() as db:
                db.execute(update(turns).values(status=status).where(turns.c.id == 'turn-a'))
                output.persist_output(db, 'turn-a'); db.commit()
            self.assertEqual([x['order_key'] for x in self.data()['items']], original)
            self.assertTrue(self.data()['items'][0]['output_partial'])
        self.event('turn-a', 2, final=True); self.assertFalse(self.data()['items'][0]['output_partial'])

    def test_mysql_query_compilation(self):
        from unittest.mock import Mock
        from sqlalchemy.dialects import mysql
        db = Mock(); db.get_bind.return_value.dialect.name = 'mysql'
        db.execute.return_value.mappings.return_value = []
        self.assertEqual(output.message_page(db, 'conversation', 1, 20), [])
        query = db.execute.call_args.args[0]
        sql = str(query.compile(dialect=mysql.dialect()))
        self.assertIn('sha2(', sql); self.assertIn('concat(', sql); self.assertIn('COLLATE utf8mb4_bin DESC', sql)

    def test_conversation_object_types_share_ordering(self):
        from app.chat.schema import snapshots
        self.turn('generic'); self.event('generic')
        expected = [row['order_key'] for row in self.data()['items']]
        for object_id in ('REQ-9000-synthetic', 'BUG-9000-synthetic', 'fix-synthetic-order'):
            with self.subTest(object_type=object_id.split('-')[0]):
                with self.factory() as db:
                    db.execute(snapshots.delete())
                    db.execute(insert(snapshots).values(id='snapshot', created_at=self.stamp, updated_at=self.stamp,
                        turn_id='generic', object_id=object_id, version='synthetic', content='synthetic'))
                    db.commit()
                # Object authority is tested separately; replace only its external
                # repository resolver, not message filtering, authorization or SQL.
                with patch('app.chat.relations.resolve_object', return_value={'id': object_id}) as resolver:
                    self.assertEqual([row['order_key'] for row in self.data()['items']], expected)
                    resolver.assert_called()

    def test_legacy_multiple_messages_are_not_collapsed(self):
        self.turn('legacy')
        with self.factory() as db:
            for mid in ('legacy-Z', 'legacy-a'):
                db.execute(insert(messages).values(id=mid, turn_id='legacy', role='assistant', content=mid,
                    created_at=self.stamp, updated_at=self.stamp))
            db.commit()
        self.assertEqual([row['id'] for row in self.data()['items']], ['legacy-a', 'legacy-Z', 'user-legacy'])

if __name__ == '__main__': unittest.main()
