"""SQLite policy integration and adapter contract regressions (also runnable with unittest)."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from sqlalchemy import create_engine, insert, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from app.chat import policy, service
from app.chat.schema import migrate, relations, conversations
from app.chat.app_server import AppServer
from app.chat.execution import _retains_acknowledged_scope


def test_governance_turn_keeps_narrow_profile_when_change_becomes_implementation_ready():
    assert _retains_acknowledged_scope('governance_write', {
        'write_scope': 'implementation_write', 'reason_code': 'implementation_change_in_sprint'})
    assert not _retains_acknowledged_scope('implementation_write', {
        'write_scope': 'governance_write', 'reason_code': 'governance_object_writable'})
    assert not _retains_acknowledged_scope('governance_write', {
        'write_scope': 'read_only', 'reason_code': 'actor_not_writer'})
    assert not _retains_acknowledged_scope('governance_write', {
        'write_scope': 'archive_write', 'reason_code': 'archive_change_applied'})


class GovernancePermissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        database_url = os.environ.get('PERMISSION_TEST_DATABASE_URL', 'sqlite:///:memory:')
        if database_url != 'sqlite:///:memory:':
            url = make_url(database_url)
            if url.host not in ('127.0.0.1', 'localhost') or not (url.database or '').endswith('_test'):
                raise ValueError('permission integration tests require a disposable loopback *_test database')
        self.engine = create_engine(database_url)
        self.addCleanup(self.engine.dispose)
        if database_url != 'sqlite:///:memory:':
            from app.chat.schema import metadata
            def clean_database():
                metadata.drop_all(self.engine)
                with self.engine.begin() as db:
                    db.execute(text('DROP TABLE admin_space_members'))
            self.addCleanup(clean_database)
        with self.engine.begin() as db:
            db.execute(text("CREATE TABLE admin_users (id VARCHAR(64) PRIMARY KEY, status VARCHAR(32) NOT NULL DEFAULT '正常', deleted_at VARCHAR(64))"))
            db.execute(text('CREATE TABLE admin_spaces (id VARCHAR(64) PRIMARY KEY, owner_id VARCHAR(64), status VARCHAR(24), deleted_at VARCHAR(32), expires_at VARCHAR(32))'))
            db.execute(text('CREATE TABLE admin_space_members (id VARCHAR(64) PRIMARY KEY, space_id VARCHAR(64), user_id VARCHAR(64), role VARCHAR(32))'))
            db.execute(text("INSERT INTO admin_users (id) VALUES ('owner'),('reader')"))
            db.execute(text("INSERT INTO admin_spaces VALUES ('space','owner','ACTIVE',NULL,NULL)"))
            db.execute(text("INSERT INTO admin_space_members VALUES ('m','space','reader','查看者')"))
        migrate(self.engine)
        self.factory = sessionmaker(self.engine)
        self.env = patch.dict(os.environ, {'MOONBOX_CHAT_REPOSITORIES': json.dumps([{'id':'repo','space_id':'space'}]), 'MOONBOX_CHAT_REPOSITORY_BINDINGS': json.dumps([
            {'id':'repo','space_id':'space','governance_root':str(self.root)}])})
        self.env.start(); self.addCleanup(self.env.stop)
        self.parent = dict(service.identity(), owner_id='owner', space_id='space', repository_id='repo', title='synthetic', active_turn_id=None)
        with self.factory() as db:
            db.execute(insert(conversations).values(**self.parent));db.commit()
        self.configure('BUG')

    def write(self, path, value):
        p = self.root/path;p.parent.mkdir(parents=True, exist_ok=True);p.write_text(value)

    def configure(self, kind):
        self.oid = kind+'-9999-synthetic'
        folder = 'bugs' if kind=='BUG' else 'requirements'
        entry = {'id':self.oid,'title':'合成权限回归','status':'in_sprint','iteration':'sprint-999',
                 'related_change':'fix-synthetic','path':f'issues/{folder}/review/{self.oid}'}
        for f in ('bugs','requirements'):
            self.write(f'issues/{f}/_registry.yaml',yaml.safe_dump({'entries':[entry] if f==folder else []}))
        self.write(entry['path']+'/bug.md' if kind=='BUG' else entry['path']+'/requirement.md','合成权限回归')
        self.plan = {'changes':['fix-synthetic'],'bugs':[self.oid] if kind=='BUG' else [],'requirements':[self.oid] if kind=='REQ' else []}
        self.write('iterations/change/sprint-999/sprint.yaml',yaml.safe_dump(self.plan))
        with self.factory() as db:
            db.execute(relations.delete())
            db.execute(insert(relations).values(conversation_id=self.parent['id'], object_id=self.oid, role='primary', title='合成权限回归'));db.commit()
        self.kind = kind

    def decide(self, trace, actor='owner', evidence=None):
        self.write('openspec/changes/fix-synthetic/trace.md','---\n'+yaml.safe_dump(trace)+'---\n')
        with self.factory() as db:
            return policy.write_policy(db, actor, self.parent, evidence=evidence)

    def test_real_bug_alias_shape_and_version_hashes(self):
        facts={}
        result=self.decide({'bug_id':self.oid,'iteration':'sprint-999','status':'proposed'},evidence=facts)
        self.assertEqual(result,{'write_scope':'implementation_write','reason_code':'implementation_change_in_sprint'})
        self.assertEqual(len(facts['change_sha256']),64)
        self.assertEqual(len(facts['sprint_sha256']),64)
        self.assertNotIn(str(self.root),json.dumps(facts))

    def test_all_source_aliases_and_sprint_aliases(self):
        for kind,keys in [('BUG',('bug','bug_id','source_bug','related_bug')),('REQ',('requirement','requirement_id','req_id','source_requirement'))]:
            self.configure(kind)
            for key in keys:
                for sprint_key in ('sprint','iteration'):
                    with self.subTest(kind=kind,key=key,sprint_key=sprint_key):
                        self.assertEqual(self.decide({key:self.oid,sprint_key:'sprint-999','status':'in_progress'})['write_scope'],'implementation_write')

    def test_conflict_type_mismatch_fail_closed(self):
        base={'bug_id':self.oid,'iteration':'sprint-999','status':'proposed'}
        for patch_value in ({'bug':'BUG-9998-other'},{'sprint':'sprint-998'},{'bug_id':[]},{'iteration':42},{'bug_id':'REQ-9999-other'}):
            with self.subTest(value=patch_value):
                self.assertEqual(self.decide({**base,**patch_value})['write_scope'],'read_only')

    def test_missing_field_stage_and_member_do_not_grant_implementation(self):
        base={'bug_id':self.oid,'iteration':'sprint-999','status':'proposed'}
        for trace in ({'bug_id':self.oid,'status':'proposed'}, {**base,'status':'applied'}, {**base,'status':'archived'}):
            self.assertNotEqual(self.decide(trace)['write_scope'],'implementation_write')
        self.assertEqual(self.decide(base,actor='reader')['reason_code'],'actor_not_writer')
        self.plan['bugs']=[];self.write('iterations/change/sprint-999/sprint.yaml',yaml.safe_dump(self.plan))
        self.assertNotEqual(self.decide(base)['write_scope'],'implementation_write')

    def test_permission_event_persistence_deduplication_and_redaction(self):
        from app.chat.execution import _permission_event
        from app.chat import worker
        from app.chat.schema import turns, events
        from sqlalchemy import select, update
        tid = service.identity()
        with self.factory() as db:
            db.execute(insert(turns).values(**tid,conversation_id=self.parent['id'],client_request_id='once',
                status='queued',prompt='synthetic',generation=0))
            db.execute(update(conversations).where(conversations.c.id==self.parent['id']).values(active_turn_id=tid['id']))
            db.commit(); token=worker.claim(db,'synthetic-worker')
        evidence={'object_id':self.oid,'change_sha256':'a'*64,'prompt':'private sentinel','path':'/private/sentinel', 'entry_sha256':'invalid'}
        decision={'write_scope':'implementation_write','reason_code':'implementation_change_in_sprint'}
        self.assertTrue(_permission_event(self.factory,token,decision,evidence,'moonbox-write','selected'))
        with self.assertLogs('app.chat.execution',level='WARNING'):
            self.assertFalse(_permission_event(self.factory,token,decision,evidence,'moonbox-write','selected'))
        self.assertTrue(_permission_event(self.factory,token,decision,evidence,'moonbox-write','acknowledged','synthetic-turn'))
        with self.factory() as db:
            rows=list(db.scalars(select(events.c.payload).where(events.c.turn_id==tid['id'])))
        self.assertEqual(len(rows),2)
        self.assertNotIn('private sentinel', ''.join(rows))
        self.assertNotIn('/private/sentinel', ''.join(rows))
        data=next(item for item in (json.loads(row)['permission_decision'] for row in rows)
                  if item['phase']=='acknowledged')
        self.assertEqual(data['acknowledged_profile'],'moonbox-write')
        self.assertEqual(data['turn_id'],tid['id'])
        self.assertEqual(data['governance_versions']['change_sha256'],'a'*64)
        with patch('app.chat.worker.record_event',side_effect=RuntimeError('sensitive sentinel')):
            with self.assertLogs('app.chat.execution',level='WARNING') as logs:
                self.assertFalse(_permission_event(self.factory,token,decision,evidence,None,'unknown'))
            self.assertNotIn('sensitive sentinel',str(logs.output))

    def test_profile_mismatch_and_write_downgrade_are_blocked(self):
        from types import SimpleNamespace
        from app.chat.execution import _verify_permission_profile
        from app.chat.app_server import ExecutorError
        for profile, write in [('moonbox-governance',True),('moonbox-write',False)]:
            with self.assertRaises(ExecutorError):
                _verify_permission_profile(SimpleNamespace(permission_profile=profile,write=write),'implementation_write')
        self.assertEqual(_verify_permission_profile(SimpleNamespace(permission_profile='moonbox-write',write=True),'implementation_write'),'moonbox-write')

    def test_governance_candidate_does_not_gain_implementation(self):
        candidate={'actor_id':'owner','object_id':self.oid,'action':'bug-complete','state':'running','binding_revision':'rev'}
        from types import SimpleNamespace
        with patch('app.governance.preparation._current_workspace_candidate',return_value=candidate), \
             patch('app.governance.scope.authorize',return_value=SimpleNamespace(binding_revision='rev')), \
             patch('app.governance.scope.visible',return_value=True):
            self.assertEqual(self.decide({'bug_id':self.oid,'iteration':'sprint-999','status':'proposed'})['reason_code'],'governance_candidate_running')

    def test_request_profile_acknowledgment(self):
        server=AppServer.__new__(AppServer)
        server.workspace=self.root;server.effort=None;server.set_write_scope('implementation_write')
        calls=[]
        server.rpc=lambda method,params: (calls.append((method,params)) or {'turn':{'id':'synthetic-turn'}})
        self.assertEqual(server.start_turn('synthetic-thread','synthetic'),'synthetic-turn')
        self.assertEqual(calls[0][1]['permissions'],'moonbox-write')
        self.assertEqual(server.last_turn_permission_profile,'moonbox-write')
        server.set_write_scope('governance_write');server.start_turn('synthetic-thread','synthetic')
        self.assertEqual(calls[-1][1]['permissions'],'moonbox-governance')
        self.assertEqual(server.last_turn_permission_profile,'moonbox-governance')


if __name__=='__main__':
    unittest.main()
