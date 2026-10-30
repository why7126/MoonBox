"""Fixed-revision environment supplier. All commands originate in approved deployment plans."""
from contextlib import contextmanager
import fcntl
import hashlib
import io
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import tarfile
import tempfile
import time
from uuid import uuid4
from sqlalchemy import insert, select, update

from app.chat.workspace import trusted_directory
from app.verification.candidate_schema import environments
from app.verification.candidate_template import CandidateError, approved_template, digest
from app.verification.runner import run_browser_acceptance, RunnerUnavailable

_ACTIVE = ('reserved', 'provisioning', 'database_ready', 'checking', 'cleaning')


@contextmanager
def locked(root, name, nonblocking=False):
    fd = os.open(root / (name + '.lock'), os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'r+b') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | (fcntl.LOCK_NB if nonblocking else 0))
        except BlockingIOError as exc:
            raise CandidateError('candidate_environment_busy') from exc
        yield


def export_candidate(workspace, commit, destination, lock_path, expected_lock):
    """Read blobs from the pinned Git tree, never mutable worktree contents or symlinks."""
    if not re.fullmatch(r'[a-f0-9]{40}(?:[a-f0-9]{24})?', commit):
        raise CandidateError('candidate_commit_invalid')
    head = subprocess.run(['git', '-C', str(workspace), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
    if head != commit:
        raise CandidateError('candidate_commit_changed')
    # A bounded tar stream avoids accepting Git submodules or unsafe extraction paths.
    with tempfile.TemporaryFile() as archive:
        proc = subprocess.Popen(['git', '-C', str(workspace), 'archive', '--format=tar', commit], stdout=archive, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 60
        try:
            while proc.poll() is None:
                if time.monotonic() > deadline or os.fstat(archive.fileno()).st_size > 512 * 1024 * 1024:
                    raise CandidateError('candidate_source_too_large')
                time.sleep(.05)
            if proc.returncode or archive.tell() > 512 * 1024 * 1024:
                raise CandidateError('candidate_source_too_large')
        finally:
            if proc.poll() is None:
                proc.kill(); proc.wait()
        archive.seek(0)
        size = 0
        with tarfile.open(fileobj=archive) as source:
            for index, member in enumerate(source):
                if index > 100000:
                    raise CandidateError('candidate_source_too_large')
                path = Path(member.name)
                parts = path.parts
                if path.is_absolute() or '..' in parts or not (member.isfile() or member.isdir()):
                    raise CandidateError('candidate_source_unsafe')
                if any(p in {'.git', '.codex', '.aws', '.ssh', 'node_modules', '__pycache__'} for p in parts):
                    raise CandidateError('candidate_source_unsafe')
                if any((p == '.env' or p.startswith('.env.') and p not in {'.env.example', '.env.template'}) for p in parts):
                    raise CandidateError('candidate_source_credentials')
                size += member.size
                if size > 512 * 1024 * 1024 or member.size > 64 * 1024 * 1024:
                    raise CandidateError('candidate_source_too_large')
                target = destination / path
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with source.extractfile(member) as stream, target.open('wb') as out:
                        shutil.copyfileobj(stream, out)
                    target.chmod(0o755 if member.mode & 0o111 else 0o644)
    lock = destination / lock_path
    if not lock.is_file() or hashlib.sha256(lock.read_bytes()).hexdigest() != expected_lock:
        raise CandidateError('candidate_dependency_mismatch')


class CandidateSupplier:
    def __init__(self, template=None, root=None):
        self.template = template
        self.root = Path(root or os.getenv('MOONBOX_CANDIDATE_ROOT', '/tmp/moonbox-candidate-environments'))

    def capability(self):
        try:
            template = self.template or approved_template()
            if not shutil.which('docker'):
                raise CandidateError('container_runtime_unavailable')
            images = [template.data[key] for key in ('python_image', 'mysql_image', 'browser_image')]
            inspected = subprocess.run(['docker', 'image', 'inspect', *images, '--format', '{{.Id}} {{.Os}}/{{.Architecture}}'],
                capture_output=True, text=True, timeout=5, check=False)
            expected = [value + ' ' + template.data['platform'] for value in images]
            if inspected.returncode or inspected.stdout.splitlines() != expected:
                raise CandidateError('candidate_images_unavailable')
            return {'available': True, 'template_digest': template.key, 'platform': template.data['platform']}
        except (OSError, subprocess.SubprocessError):
            return {'available': False, 'reason_code': 'candidate_images_unavailable', 'dependency': 'REQ-0048-chat-isolated-acceptance-orchestration'}
        except CandidateError as exc:
            return {'available': False, 'reason_code': str(exc), 'dependency': 'REQ-0048-chat-isolated-acceptance-orchestration'}

    def reconcile(self, factory, limit=10):
        """A local process lock proves controller liveness; never infer it from age alone."""
        if not self.root.exists():
            return 0
        root = trusted_directory(self.root)
        with factory() as db:
            rows = list(db.execute(select(environments).where(environments.c.cleanup_state != 'clean')
                .order_by(environments.c.updated_at, environments.c.id).limit(limit)).mappings())
        count = 0
        for row in rows:
            try:
                with locked(root, 'candidate-' + row['candidate_id'], True):
                    # Cleanup depends only on durable ownership, even if the approved template changed.
                    from types import SimpleNamespace
                    clean = DockerEnvironment(root, dict(row), SimpleNamespace(data={})).cleanup()
                    with factory.begin() as db:
                        if clean:
                            from app.verification.acceptance_resources import release_in_transaction
                            release_in_transaction(db,row['id'])
                        db.execute(update(environments).where(environments.c.id == row['id']).values(
                            state='interrupted', cleanup_state='clean' if clean else 'pending',
                            error_code='candidate_interrupted' if clean else 'candidate_cleanup_pending',
                            updated_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())))
                    count += int(clean)
            except (CandidateError, OSError):
                continue
        return count

    def validate(self, *, candidate_id, candidate_commit, workspace, change_id,
                 factory=None, space_id=None, repository_id=None):
        try:
            return self._validate(candidate_id, candidate_commit, Path(workspace), factory, space_id, repository_id)
        except (CandidateError, OSError, subprocess.SubprocessError) as exc:
            return {'status': 'blocked', 'reason_code': str(exc) if isinstance(exc, CandidateError) else 'candidate_environment_unavailable'}

    def _validate(self, candidate_id, commit, workspace, factory, space, repository):
        template = self.template or approved_template()
        if factory is None or not space or not repository:
            raise CandidateError('candidate_scope_required')
        if not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', candidate_id):
            raise CandidateError('candidate_identity_invalid')
        config = os.getenv('MOONBOX_CANDIDATE_TEMPLATE')
        if config and Path(config).resolve().is_relative_to(workspace.resolve()):
            raise CandidateError('template_not_trusted')
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        root = trusted_directory(self.root)
        if root.is_relative_to(workspace.resolve()) or root.stat().st_mode & 0o022:
            raise CandidateError('candidate_storage_untrusted')
        with locked(root, 'candidate-' + candidate_id, True):
            with locked(root, 'capacity'):
                with factory() as db:
                    row = db.execute(select(environments).where(environments.c.candidate_id == candidate_id)).mappings().first()
                    if row and (row['space_id'], row['repository_id'], row['candidate_commit'], row['template_digest']) != (space, repository, commit, template.key):
                        raise CandidateError('candidate_environment_stale')
                    if row and row['state'] == 'passed' and row['cleanup_state'] == 'clean':
                        return json.loads(row['result_json'])
                    if row and row['state'] in _ACTIVE:
                        # An acquired process lock proves no live local controller. Reconcile only.
                        engine = DockerEnvironment(root, dict(row), template)
                        clean = engine.cleanup()
                        db.execute(update(environments).where(environments.c.id == row['id']).values(
                            state='interrupted', cleanup_state='clean' if clean else 'pending', error_code='candidate_interrupted'))
                        if clean:
                            from app.verification.acceptance_resources import release_in_transaction
                            release_in_transaction(db,row['id'])
                        db.commit()
                        raise CandidateError('candidate_interrupted')
                    active = list(db.execute(select(environments).where(environments.c.cleanup_state != 'clean')).mappings())
                    other = [x for x in active if not row or x['id'] != row['id']]
                    if len(other) >= 2 or any(x['space_id'] == space for x in other):
                        raise CandidateError('candidate_capacity_unavailable')
                    if row and row['cleanup_state'] != 'clean':
                        clean = DockerEnvironment(root, dict(row), template).cleanup()
                        if not clean:
                            raise CandidateError('candidate_cleanup_pending')
                    stamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                    if not row:
                        daemon_id = DockerEnvironment.daemon_id()
                        row = dict(id=str(uuid4()), candidate_id=candidate_id, space_id=space, repository_id=repository,
                            candidate_commit=commit, template_digest=template.key, state='reserved', expires_at=int(time.time())+7200,
                            daemon_id=daemon_id,
                            error_code=None, result_json='{}', cleanup_state='pending', created_at=stamp, updated_at=stamp)
                        db.execute(insert(environments).values(**row))
                    else:
                        row = dict(row)
                        if row['expires_at'] <= time.time():
                            raise CandidateError('candidate_environment_expired')
                        db.execute(update(environments).where(environments.c.id == row['id']).values(state='reserved', cleanup_state='pending', error_code=None))
                    from app.verification.acceptance_resources import reserve_in_transaction,capacity
                    from app.verification.acceptance_state import Conflict
                    try:
                        reserve_in_transaction(db,row,capacity(**DockerEnvironment.capacity_limits(root)))
                    except Conflict:
                        raise CandidateError('candidate_capacity_unavailable') from None
                    db.commit()
            engine = DockerEnvironment(root, row, template)
            result = {'status': 'blocked', 'reason_code': 'candidate_environment_unavailable'}
            current_stage = 'reserved'
            def stage(value):
                nonlocal current_stage
                current_stage = value
                with factory.begin() as db:
                    db.execute(update(environments).where(environments.c.id == row['id']).values(state=value))
            try:
                stage('provisioning')
                evidence = engine.run(workspace, stage)
                result = {'status': 'passed', 'candidate_id': candidate_id, 'candidate_commit': commit,
                          'environment_key': row['id'], 'runtime_digest': template.data['python_image'],
                          'evidence_digest': digest(evidence), 'template_digest': template.key,
                          'checks': [{'database': item['database'], 'version': item['version'],
                              'checks_passed': item['checks_passed'], 'browser': item['browser']['browser'],
                              'browser_version': item['browser']['browser_version']} for item in evidence['matrices']]}
                engine.save_evidence(evidence)
            except Exception as exc:
                # Candidate output and raw container errors must never become API messages.
                result = {'status': 'failed', 'reason_code': str(exc) if isinstance(exc, (CandidateError, RunnerUnavailable)) else 'candidate_checks_failed'}
                try:
                    engine.save_evidence({'candidate_commit': commit, 'template_digest': template.key,
                        'status': 'failed', 'stage': current_stage, 'reason_code': result['reason_code']})
                except OSError:
                    pass
            finally:
                stage('cleaning')
                clean = engine.cleanup()
                if not clean:
                    result = {'status': 'blocked', 'reason_code': 'candidate_cleanup_pending'}
                with factory.begin() as db:
                    if clean:
                        from app.verification.acceptance_resources import release_in_transaction
                        release_in_transaction(db,row['id'])
                    db.execute(update(environments).where(environments.c.id == row['id']).values(
                        state=result['status'], cleanup_state='clean' if clean else 'pending',
                        result_json=json.dumps(result), error_code=result.get('reason_code')))
            return result


class DockerEnvironment:
    def __init__(self, root, row, template):
        self.row, self.plan = row, template.data
        self.root = root / row['id']
        self.name = 'moonbox-candidate-' + row['id']
        self.network = self.name + '-net'
        self.labels = {'moonbox.candidate.environment': row['id'], 'moonbox.candidate.expires': str(row['expires_at'])}
        # Test harness supplies registered lifecycle labels; never HTTP input.
        self.labels.update(self.test_labels())

    @staticmethod
    def capacity_limits(root):
        info=json.loads(subprocess.run(['docker','info','--format','{{json .}}'],
            capture_output=True,text=True,timeout=15,check=True).stdout)
        gib=1024**3
        return dict(available_cpu=max(0,info['NCPU']-2),available_memory=max(0,info['MemTotal']-2*gib),
                    available_disk=max(0,shutil.disk_usage(root).free-2*gib),hard_disk_limit=True)

    @staticmethod
    def daemon_id():
        result = subprocess.run(['docker', 'info', '--format', '{{.ID}}'], capture_output=True, text=True, timeout=15, check=True)
        value = result.stdout.strip()
        if not value or len(value) > 128:
            raise CandidateError('candidate_daemon_unknown')
        return value

    @staticmethod
    def test_labels():
        run, expires = os.getenv('MOONBOX_TEMP_RUN'), os.getenv('MOONBOX_TEMP_EXPIRES')
        if run and expires and re.fullmatch(r'[a-f0-9]{32}', run) and expires.isdigit():
            return {'moonbox.temp.managed': 'true', 'moonbox.temp.run': run, 'moonbox.temp.expires': expires}
        return {}

    def command(self, args, timeout=60, input=None):
        remaining = self.row['expires_at'] - time.time()
        if remaining <= 0:
            raise CandidateError('candidate_environment_expired')
        # Output is bounded and discarded unless a trusted probe explicitly parses it.
        with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
            proc = subprocess.Popen(['docker', *args], stdin=subprocess.PIPE if input else subprocess.DEVNULL, stdout=out, stderr=err)
            if input:
                proc.stdin.write(input.encode()); proc.stdin.close()
            end = time.monotonic() + min(timeout, remaining)
            try:
                while proc.poll() is None:
                    if time.monotonic() >= end or os.fstat(out.fileno()).st_size + os.fstat(err.fileno()).st_size > 2*1024*1024:
                        raise CandidateError('candidate_command_budget_exceeded')
                    time.sleep(.1)
                if proc.returncode:
                    raise CandidateError('candidate_command_failed')
                out.seek(0)
                return out.read(2*1024*1024).decode(errors='replace').strip()
            finally:
                if proc.poll() is None:
                    proc.kill(); proc.wait()

    def label_args(self):
        return [part for key, value in self.labels.items() for part in ('--label', key + '=' + value)]

    def run_args(self, name, image, db=False):
        args = ['run', '-d', '--name', name, '--network', self.network, *self.label_args(),
                '--platform', self.plan['platform'], '--read-only', '--cap-drop', 'ALL',
                '--security-opt', 'no-new-privileges:true', '--pids-limit', '256', '--cpus', '1', '--memory', '2g',
                '--tmpfs', '/tmp:rw,nosuid,size=256m', '--tmpfs', '/run:rw,nosuid,size=64m']
        if db:
            args += ['--user', '999:999', '--tmpfs', '/var/lib/mysql:rw,nosuid,uid=999,gid=999,size=1g',
                     '--tmpfs', '/var/run/mysqld:rw,nosuid,uid=999,gid=999,size=64m']
        else:
            args += ['--user', '10001:10001', '--tmpfs', '/state:rw,nosuid,uid=10001,gid=10001,size=512m',
                     '--env', 'HOME=/tmp', '--env', 'PYTHONDONTWRITEBYTECODE=1',
                     '--mount', f'type=bind,src={self.root / "source"},dst=/source,readonly',
                     '--mount', f'type=bind,src={self.root / "control"},dst=/control,readonly',
                     '--workdir', '/source/' + self.plan['source_subdir'],
                     '--env', 'PYTHONPATH=/source/' + self.plan['source_subdir']]
        return args

    def run(self, workspace, stage):
        if self.daemon_id() != self.row['daemon_id']:
            raise CandidateError('candidate_daemon_changed')
        if shutil.disk_usage(self.root.parent).free < 2*1024**3:
            raise CandidateError('candidate_storage_insufficient')
        self.root.mkdir(mode=0o700, exist_ok=True)
        source = self.root / 'source'
        if source.exists(): shutil.rmtree(source)
        source.mkdir()
        export_candidate(workspace, self.row['candidate_commit'], source, self.plan['lock_path'], self.plan['lock_digest'])
        control = self.root / 'control'; control.mkdir(exist_ok=True)
        (control / 'server.py').write_text(_SERVER)
        (control / 'plan.json').write_text(json.dumps({'app': self.plan['app_module'], 'commit': self.row['candidate_commit']}))
        self.command(['network', 'create', '--internal', *self.label_args(), self.network])
        for key in ('python_image', 'mysql_image', 'browser_image'):
            actual = json.loads(self.command(['image', 'inspect', self.plan[key]]))[0]
            if actual['Id'] != self.plan[key] or actual['Os'] + '/' + actual['Architecture'] != self.plan['platform']:
                raise CandidateError('candidate_image_platform_mismatch')
        evidence = {'candidate_commit': self.row['candidate_commit'], 'template_digest': self.row['template_digest'], 'matrices': []}
        for backend in ('sqlite', 'mysql'):
            stage('provisioning')
            database_url = 'sqlite:////state/candidate.db'
            if backend == 'mysql':
                password, root_password = secrets.token_hex(24), secrets.token_hex(24)
                db_name = self.name + '-db'
                self.command(self.run_args(db_name, self.plan['mysql_image'], True) + [
                    '--env', 'MYSQL_DATABASE=candidate', '--env', 'MYSQL_USER=candidate',
                    '--env', 'MYSQL_PASSWORD=' + password, '--env', 'MYSQL_ROOT_PASSWORD=' + root_password,
                    self.plan['mysql_image']])
                database_url = 'mysql+pymysql://candidate:' + password + '@' + db_name + '/candidate'
            app = self.name + '-app'
            self.command(self.run_args(app, self.plan['python_image']) + [
                '--env', 'DATABASE_TYPE=' + backend, '--env', 'DATABASE_URL=' + database_url,
                '--env', 'SQLITE_DATABASE_URL=' + database_url if backend == 'sqlite' else 'MYSQL_DATABASE_URL=' + database_url,
                '--env', 'APP_ENV=test', self.plan['python_image'], 'python', '-c', 'import time; time.sleep(7200)'])
            # Database identity is probed by a trusted fixed command, not a candidate test report.
            version = None
            for attempt in range(60):
                try:
                    version = self.command(['exec', app, 'python', '-c', _DB_PROBE], timeout=10)
                    if backend == 'mysql' and not version.startswith('8.4.'):
                        raise CandidateError('candidate_mysql_version_unsupported')
                    break
                except CandidateError as exc:
                    if str(exc) == 'candidate_mysql_version_unsupported' or attempt == 59: raise
                    time.sleep(1)
            stage('database_ready')
            completed = []
            for kind in ('migration', 'seed'):
                self.command(['exec', app, *self.plan[kind]], timeout=600)
                completed.append(kind)
            self.command(['exec', '-d', app, 'python', '/control/server.py'])
            health = self.plan['health_path']
            probe = 'import urllib.request,json; r=json.load(urllib.request.urlopen("http://127.0.0.1:8000/__moonbox_candidate",timeout=5)); assert r["commit"]==' + repr(self.row['candidate_commit']) + '; assert urllib.request.urlopen("http://127.0.0.1:8000' + health + '",timeout=5).status==200'
            for attempt in range(30):
                try:
                    self.command(['exec', app, 'python', '-c', probe], timeout=10); break
                except CandidateError:
                    if attempt == 29: raise
                    time.sleep(1)
            stage('checking')
            for command in self.plan['checks']:
                self.command(['exec', app, *command], timeout=600)
            browser = run_browser_acceptance(self.plan['browser_image'], network=self.network,
                target_url='http://' + app + ':8000' + health, browser=self.plan['browser'],
                viewports=self.plan['viewports'], selectors=self.plan['selectors'], steps=self.plan['steps'],
                evidence_root=self.root, space_id=self.row['space_id'], repository_id=self.row['repository_id'],
                task_id=str(uuid4()), timeout=max(1, min(120, self.row['expires_at']-int(time.time()))), lifecycle_labels=self.labels)
            evidence['matrices'].append({'database': backend, 'version': version, 'steps': completed,
                'app_version': self.row['candidate_commit'], 'checks_passed': len(self.plan['checks']), 'browser': browser})
            self.remove_container(app)
            if backend == 'mysql': self.remove_container(db_name)
        return evidence

    def save_evidence(self, evidence):
        path = self.root / 'evidence.json'
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(evidence, ensure_ascii=False, indent=2))
        temporary.replace(path)

    def remove_container(self, name):
        self.command(['rm', '-f', name])

    def cleanup(self):
        # Cleanup ignores elapsed task deadline, but each daemon operation stays bounded.
        try:
            if self.daemon_id() != self.row['daemon_id']:
                return False
            for kind in ('container', 'network'):
                listed = subprocess.run(['docker', kind, 'ls', *(['-a'] if kind == 'container' else []), '-q', '--filter', 'label=moonbox.candidate.environment=' + self.row['id']], capture_output=True, text=True, timeout=20, check=True).stdout.split()
                for resource in listed:
                    info = json.loads(subprocess.run(['docker', kind, 'inspect', resource], capture_output=True, text=True, timeout=15, check=True).stdout)[0]
                    labels = info.get('Config', {}).get('Labels', {}) if kind == 'container' else info.get('Labels', {})
                    if (labels.get('moonbox.candidate.environment') != self.row['id']
                            or labels.get('moonbox.candidate.expires') != str(self.row['expires_at'])):
                        return False
                    subprocess.run(['docker', kind, 'rm', *(['-f'] if kind == 'container' else []), resource], capture_output=True, timeout=20, check=True)
                remaining = subprocess.run(['docker', kind, 'ls', *(['-a'] if kind == 'container' else []), '-q', '--filter', 'label=moonbox.candidate.environment=' + self.row['id']], capture_output=True, text=True, timeout=20, check=True)
                if remaining.stdout.strip(): return False
            return True
        except (OSError, subprocess.SubprocessError, ValueError, KeyError):
            return False


_DB_PROBE = '''import os
from sqlalchemy import create_engine,text
engine=create_engine(os.environ['DATABASE_URL'])
with engine.connect() as db:
 print(db.scalar(text('SELECT VERSION()' if engine.dialect.name=='mysql' else 'SELECT sqlite_version()')))
'''
_SERVER = '''import json,importlib,uvicorn,sys,os
# The controller directory must never shadow candidate application modules.
sys.path=[p for p in sys.path if os.path.realpath(p)!=os.path.dirname(os.path.realpath(__file__))]
plan=json.load(open('/control/plan.json'))
module,name=plan['app'].split(':')
application=getattr(importlib.import_module(module),name)
async def served(scope,receive,send):
 if scope['type']=='http' and scope['path']=='/__moonbox_candidate':
  body=json.dumps({'commit':plan['commit']}).encode()
  await send({'type':'http.response.start','status':200,'headers':[(b'content-type',b'application/json')]})
  await send({'type':'http.response.body','body':body})
 else: await application(scope,receive,send)
uvicorn.run(served,host='0.0.0.0',port=8000,log_level='warning')
'''
