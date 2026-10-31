"""Controlled Docker runtime for immutable acceptance snapshots.

Project-specific identity installation/revocation is an explicit trusted adapter.
Missing adapters block affected checks rather than inventing successful role tests.
"""
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import threading
import time
from types import SimpleNamespace
from uuid import uuid4

from sqlalchemy import update
from app.verification.acceptance_schema import attempts
from app.verification.acceptance_resources import reserve, release
from app.verification.acceptance_source import export_checkpoint
from app.verification.acceptance_state import Conflict
from app.verification.candidate import DockerEnvironment, CandidateError, _DB_PROBE, _SERVER
from app.verification.runner import run_browser_acceptance, RunnerUnavailable
from app.chat.workspace import trusted_directory


class DockerRuntime:
    def __init__(self, state, template, root, *, identity_adapter=None):
        self.state, self.template = state, template
        self.root = Path(root); self.root.mkdir(mode=0o700,parents=True,exist_ok=True)
        trusted_directory(self.root)
        if self.root.stat().st_mode & 0o022:raise Conflict('runtime_storage_untrusted')
        self.identity_adapter=identity_adapter
        if self.identity_adapter is None:
            from app.verification.acceptance_identity import CommandIdentityAdapter
            self.identity_adapter=CommandIdentityAdapter(state,template,self.root/'identities')
        self.engine=None;self.token=None;self.database=None;self.stopped=threading.Event()
        self.busy=threading.Lock();self.running=False
        self.failed_databases={}
        self.deadline=time.time()+1200

    def command(self,args,timeout=60,input=None):
        if self.stopped.is_set():raise Conflict('cancelled')
        if args and args[0]=='run':
            args=[args[0],'--log-driver','none',*args[1:]]
        remaining=self.deadline-time.time()
        if remaining<=0:raise Conflict('stage_budget_expired')
        try:return self.engine.command(args,timeout=min(timeout,remaining),input=input)
        except CandidateError as error:raise Conflict(str(error)) from None

    def prepare(self,token):
        self.token=token
        self.state.bind_template(token,self.template.key)
        self.deadline=min(time.time()+1200,token['expires_at'])
        base=self.template.data['base']
        source=json.loads(token['source_ref_json'])
        if not source:raise Conflict('source_checkpoint_missing')
        info=subprocess.run(['docker','info','--format','{{json .}}'],capture_output=True,text=True,timeout=15,check=True)
        host=json.loads(info.stdout)
        # Keep platform headroom outside the two acceptance slots.
        reserve(self.state.factory,token,available_cpu=max(0,host['NCPU']-2),
                available_memory=max(0,host['MemTotal']-2*1024**3),
                available_disk=max(0,shutil.disk_usage(self.root).free-2*1024**3),hard_disk_limit=True)
        row={'id':token['attempt_id'],'expires_at':token['expires_at'],'daemon_id':host['ID'],
             'space_id':token['space_id'],'repository_id':token['repository_id'],
             'candidate_commit':source['head_commit']}
        self.engine=DockerEnvironment(self.root,row,SimpleNamespace(data=base))
        # Ownership is persisted before creating the first resource.
        with self.state.factory.begin() as db:
            current,_=self.state._fenced(db,token);self.state._cas(db,current,cleanup_state='active')
            db.execute(update(attempts).where(attempts.c.id==token['attempt_id']).values(
                environment_id=row['id'],template_digest=self.template.key))
        self.engine.root.mkdir(mode=0o700)
        (self.engine.root/'ownership.json').write_text(json.dumps(row))
        export_checkpoint(self.state.factory,source,self.engine.root/'source',base)
        control=self.engine.root/'control';control.mkdir()
        (control/'server.py').write_text(_SERVER)
        (control/'plan.json').write_text(json.dumps({'app':base['app_module'],'commit':source['head_commit']}))
        for image in [base[key] for key in ('python_image','mysql_image','browser_image')]+[self.template.data['node_image']]:
            actual=json.loads(self.command(['image','inspect',image]))[0]
            if actual['Id']!=image or actual['Os']+'/'+actual['Architecture']!=base['platform']:
                raise Conflict('runtime_image_mismatch')
        self.create_network()
        node=self.engine.name+'-node'
        try:
            version=self.command(['run','--rm','--name',node,'--network','none',*self.engine.label_args(),
                '--read-only','--cap-drop','ALL','--security-opt','no-new-privileges:true','--cpus','0.5','--memory','512m',
                '--pids-limit','128','--user','10001:10001','--tmpfs','/tmp:rw,nosuid,size=128m',
                self.template.data['node_image'],'node','--version'])
            if version.lstrip('v')!=self.template.data['runtime_versions']['node']:raise Conflict('node_version_mismatch')
        finally:
            pass
        self.prepare_databases()

    def prepare_databases(self):
        for backend in dict.fromkeys(check['database'] for check in self.template.data['checks'].values()):
            try:
                self.start_database(backend)
                break
            except Conflict as error:
                self.failed_databases[backend]=str(error)
                self.reset_database()

    def create_network(self):
        # Deployment-only override for hosts whose default address pools are full.
        # Docker rejects overlaps; never remove or reuse another task's network.
        args = []
        subnet = os.getenv('MOONBOX_ACCEPTANCE_SUBNET')
        if subnet:
            try:
                network = ipaddress.ip_network(subnet, strict=True)
                private = [ipaddress.ip_network(value) for value in ('10.0.0.0/8','172.16.0.0/12','192.168.0.0/16')]
                if (network.version != 4 or not any(network.subnet_of(block) for block in private)
                        or network.prefixlen < 24 or network.prefixlen > 28):
                    raise ValueError()
            except ValueError:
                raise Conflict('acceptance_subnet_invalid') from None
            args = ['--subnet', str(network)]
        self.command(['network','create','--internal',*args,*self.engine.label_args(),self.engine.network])

    def reset_database(self):
        """Unknown initialization is discarded, never replayed into its old DB."""
        try:self.identity_adapter.revoke_all()
        except Exception:pass
        if not self.engine.cleanup():raise Conflict('database_cleanup_unconfirmed')
        self.database=None
        self.create_network()

    def start_database(self,backend):
        if self.database==backend:return
        base=self.template.data['base'];engine=self.engine
        if self.database:
            if self.identity_adapter:self.identity_adapter.revoke_all()
            self.command(['rm','-f',engine.name+'-app'])
            if self.database=='mysql':self.command(['rm','-f',engine.name+'-db'])
        url='sqlite:////state/acceptance.db'
        if backend=='mysql':
            password=secrets.token_hex(24);root_password=secrets.token_hex(24)
            private=engine.root/'mysql.env'
            private.write_text('MYSQL_DATABASE=candidate\nMYSQL_USER=candidate\nMYSQL_PASSWORD='+password+'\nMYSQL_ROOT_PASSWORD='+root_password+'\n')
            private.chmod(0o600)
            try:
                # Disposable database has no replication or recovery consumers.
                # Disabling binlog permits normal schema-owned trigger migrations
                # without granting the application SUPER privileges.
                self.command(engine.run_args(engine.name+'-db',base['mysql_image'],True)+['--env-file',str(private),base['mysql_image'],'--skip-log-bin'])
            finally:private.unlink(missing_ok=True)
            url='mysql+pymysql://candidate:'+password+'@'+engine.name+'-db/candidate'
        appenv=engine.root/'app.env'
        appenv.write_text('DATABASE_TYPE='+backend+'\nDATABASE_URL='+url+'\nAPP_ENV=test\n'+('SQLITE_DATABASE_URL=' if backend=='sqlite' else 'MYSQL_DATABASE_URL=')+url+'\n')
        appenv.chmod(0o600)
        try:
            self.command(engine.run_args(engine.name+'-app',base['python_image'])+['--env-file',str(appenv),
                base['python_image'],'python','-c','import time;time.sleep(7200)'])
        finally:appenv.unlink(missing_ok=True)
        self.database=backend
        app=engine.name+'-app';deadline=time.monotonic()+120
        while True:
            try:
                version=self.command(['exec',app,'python','-c',_DB_PROBE],timeout=10)
                if backend=='mysql' and version!=self.template.data['runtime_versions']['mysql']:
                    raise Conflict('mysql_version_mismatch')
                break
            except Conflict as error:
                if str(error)=='mysql_version_mismatch' or time.monotonic()>=deadline:raise
                if self.stopped.wait(1):raise Conflict('cancelled')
        python=self.command(['exec',app,'python','-c','import platform;print(platform.python_version())'])
        if python!=self.template.data['runtime_versions']['python']:raise Conflict('python_version_mismatch')
        # Test dependencies and the real thread pool must work in the target image.
        from app.verification.python_probe import PYTHON_PROBE
        try:
            self.command(['exec',app,'python','-c',PYTHON_PROBE],timeout=10)
        except Conflict as error:
            if str(error) in {'cancelled','stage_budget_expired'}:raise
            raise Conflict('python_test_runtime_unavailable') from None
        for step in ('migration','seed'):
            # A failed or interrupted migration is not replayed in an existing database.
            self.command(['exec',app,*base[step]],timeout=300)
        self.command(['exec','-d',app,'python','/control/server.py'])
        deadline=time.monotonic()+120
        probe='import urllib.request,json; assert json.load(urllib.request.urlopen("http://127.0.0.1:8000/__moonbox_candidate",timeout=5))["commit"]=='+repr(engine.row['candidate_commit'])+';assert urllib.request.urlopen("http://127.0.0.1:8000'+base['health_path']+'",timeout=5).status==200'
        while True:
            try:self.command(['exec',app,'python','-c',probe],timeout=10);break
            except Conflict:
                if time.monotonic()>=deadline:raise
                if self.stopped.wait(1):raise Conflict('cancelled')

    def execute(self,ac):
        check=self.template.data['checks'].get(ac)
        if not check:raise Conflict('ac_not_in_approved_template')
        if check['database'] in self.failed_databases:raise Conflict(self.failed_databases[check['database']])
        if self.identity_adapter is None:raise Conflict('identity_adapter_unavailable')
        with self.busy:
            self.running=True
            current=self.state.get(self.token['id'])
            self.deadline=min(time.time()+600,current['checks_deadline'] or current['expires_at'])
            try:
                try:self.start_database(check['database'])
                except Conflict as error:
                    self.failed_databases[check['database']]=str(error)
                    self.reset_database()
                    raise
                self.identity_adapter.activate(self.token,check['role'],self.engine)
                if check['argv'][0]=='node':
                    self.command(['run','--rm','-i','--name',self.engine.name+'-check',
                        '--network',self.engine.network,*self.engine.label_args(),'--read-only',
                        '--cap-drop','ALL','--security-opt','no-new-privileges:true','--cpus','1','--memory','2g',
                        '--pids-limit','256','--user','10001:10001','--tmpfs','/tmp:rw,nosuid,size=256m',
                        '--mount',f'type=bind,src={self.engine.root / "source"},dst=/source,readonly',
                        '--workdir','/source/'+self.template.data['base']['source_subdir'],
                        '--env','APP_URL=http://'+self.engine.name+'-app:8000',self.template.data['node_image'],
                        *check['argv']],timeout=600,input=self.identity_adapter.private_payload())
                else:
                    self.command(['exec','-i',self.engine.name+'-app',*check['argv']],timeout=600,
                                 input=self.identity_adapter.private_payload())
                browsers=[];base=self.template.data['base']
                evidence_bytes=sum(path.stat().st_size for path in self.engine.root.rglob('*.png') if path.is_file())
                if evidence_bytes+2*len(base['viewports'])*10*1024**2>2*1024**3:
                    raise Conflict('evidence_quota_exhausted')
                for browser in ('chromium','firefox'):
                    remaining=int(self.deadline-time.time())
                    if remaining<=0:raise Conflict('ac_budget_expired')
                    try:
                        result=run_browser_acceptance(base['browser_image'],network=self.engine.network,
                            target_url='http://'+self.engine.name+'-app:8000'+base['health_path'],browser=browser,
                            viewports=base['viewports'],selectors=base['selectors'],steps=base['steps'],
                            evidence_root=self.engine.root,space_id=self.token['space_id'],repository_id=self.token['repository_id'],
                            task_id=str(uuid4()),timeout=min(120,remaining),lifecycle_labels=self.engine.labels,
                            identity_file=self.identity_adapter.leases.root/self.identity_adapter.current['identity_ref'],
                            login=self.template.data['identity_adapter']['login'])
                    except RunnerUnavailable as error:
                        if error.code in {'selector_missing','step_failed','target_response_failed'}:
                            return {'status':'failed','reason':error.code,'evidence':{}}
                        raise Conflict(error.code) from None
                    if result['browser_version']!=self.template.data['runtime_versions'][browser]:raise Conflict('browser_version_mismatch')
                    browsers.append(result)
                digest=hashlib.sha256(json.dumps([ac,self.token['input_digest'],self.template.key,check,browsers],sort_keys=True).encode()).hexdigest()
                (self.engine.root/('evidence-'+ac+'.json')).write_text(json.dumps(browsers))
                return {'status':'passed','evidence':{'kind':'browser','digest':digest,'artifact_id':ac,
                    'environment_id':self.token['attempt_id'],'deployment_digest':self.template.data['deployment_digest']}}
            finally:self.running=False

    def interrupt(self):
        self.stopped.set()
        # Terminate only resources owned by this exact environment and daemon.
        if self.engine:self.engine.cleanup()

    def cleanup(self):
        if self.identity_adapter:
            try:self.identity_adapter.revoke_all()
            except Exception:pass  # Exact resource removal remains mandatory.
        clean=self.engine.cleanup() if self.engine else True
        if clean and self.token:
            from app.verification.acceptance_schema import identities
            with self.state.factory.begin() as db:
                db.execute(update(identities).where(identities.c.attempt_id==self.token['attempt_id'])
                           .values(revocation_state='revoked'))
            release(self.state.factory,self.token['id'],resources_confirmed_absent=True)
        return clean

    def terminated(self):
        return not self.running
