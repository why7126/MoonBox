"""Opt-in local MoonBox product matrix. Real immutable export and product runtime.

The controller operation is a test request; this is not a Chat/model round proof.
No production configuration, user data, or repository credentials are copied.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from app.chat.schema import metadata, conversations, turns, usage_accounts
from app.chat.content_schema import TABLES as CONTENT
from app.moonbox_core.schema import TABLES as CORE, session_bindings
from app.moonbox_core.workspaces import register_main, stamp
from app.moonbox_rollout.schema import TABLES as ROLLOUT
from app.moonbox_rollout.catalog import publish
from app.chat.snapshot_store import capture
from app.verification.acceptance_schema import TABLES as ACCEPTANCE
from app.verification.acceptance_template import AcceptanceTemplate
from app.verification.acceptance_state import AcceptanceState
from app.verification.acceptance_runtime import DockerRuntime
from app.verification.acceptance_controller import Controller


def main():
    if os.environ.get('MOONBOX_PRODUCT_ACCEPTANCE_LIVE') != '1':
        raise SystemExit('explicit opt-in required')
    if not os.environ.get('MOONBOX_TEMP_RUN') or not os.environ.get('MOONBOX_TEMP_EXPIRES'):
        raise SystemExit('registered temporary run required')
    project = Path(__file__).resolve().parents[3]
    root = Path(tempfile.mkdtemp(prefix='moonbox-product-acceptance-', dir='/private/tmp'))
    root.chmod(0o700)
    # Private diagnostics only; never include subprocess stderr (which may carry
    # temporary identities) in the public evidence report.
    original_popen = subprocess.Popen
    class DiagnosticProcess(original_popen):
        def __init__(self, *args, **kwargs):
            self.diagnostic_stream = kwargs.get('stderr')
            self.diagnostic_saved = False
            super().__init__(*args, **kwargs)
        def poll(self):
            code = super().poll()
            stream = self.diagnostic_stream
            if code and not self.diagnostic_saved and hasattr(stream, 'seek') and not stream.closed:
                self.diagnostic_saved = True
                position = stream.tell(); stream.seek(0)
                data = stream.read(32768); stream.seek(position)
                path = root / ('diagnostic-' + str(self.pid) + '.log')
                path.write_bytes(data if isinstance(data, bytes) else data.encode())
                path.chmod(0o600)
            return code
    subprocess.Popen = DiagnosticProcess
    original_run = subprocess.run
    def diagnostic_run(*args, **kwargs):
        result = original_run(*args, **kwargs)
        if result.returncode and result.stderr:
            path = root / ('diagnostic-run-' + str(time.time_ns()) + '.log')
            path.write_bytes(result.stderr if isinstance(result.stderr, bytes) else result.stderr.encode())
            path.chmod(0o600)
        return result
    import time
    subprocess.run = diagnostic_run
    from app.verification import acceptance_runtime
    from app.verification.candidate import DockerEnvironment
    acceptance_runtime._SERVER = "import sys\nsys.stdout=open('/state/server.log','w',buffering=1)\nsys.stderr=sys.stdout\n" + acceptance_runtime._SERVER
    original_cleanup = DockerEnvironment.cleanup
    def diagnostic_cleanup(environment):
        result=original_run(['docker','exec',environment.name+'-app','cat','/state/server.log'],capture_output=True,timeout=10)
        if result.returncode == 0:
            path=root/('server-'+environment.row['id']+'.log');path.write_bytes(result.stdout);path.chmod(0o600)
        return original_cleanup(environment)
    DockerEnvironment.cleanup=diagnostic_cleanup
    source = root / 'source'
    source.mkdir()
    files = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z', 'src/backend/app'], cwd=project).decode().split('\0')
    files += ['src/backend/pyproject.toml', 'src/backend/tests/acceptance_product_adapter.py',
              'src/backend/tests/acceptance_product_server.py','src/backend/app/db/time_values.py']
    manifest = {}
    for relative in sorted(set(filter(None, files))):
        original = project / relative
        if original.is_symlink() or not original.is_file():
            raise RuntimeError('unsafe_product_source')
        target = source / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original, target)
        manifest[relative] = hashlib.sha256(target.read_bytes()).hexdigest()
    shutil.copytree(project / 'src/web/dist', source / 'src/web/dist')
    subprocess.run(['git','init','-q',str(source)], check=True)
    subprocess.run(['git','-C',str(source),'add','.'], check=True)
    subprocess.run(['git','-C',str(source),'-c','user.name=Local Acceptance','-c','user.email=acceptance@example.invalid','commit','-qm','Isolated MoonBox product snapshot'], check=True)
    head = subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'], text=True).strip()
    images = {}
    for key, tag in {'python':'moonbox-backend:req0048-product','mysql':'mysql:8.4','browser':'moonbox-verification:req0048-product','node':'node:24-trixie-slim'}.items():
        images[key] = subprocess.check_output(['docker','image','inspect','--format','{{.Id}}',tag], text=True).strip()
    argv = lambda action: ['python','tests/acceptance_product_adapter.py',action]
    base = dict(schema_version=1,template='moonbox-web-python-v1',platform='linux/arm64',
        python_image=images['python'],mysql_image=images['mysql'],browser_image=images['browser'],
        source_subdir='src/backend',app_module='tests.acceptance_product_server:app',health_path='/chat',
        lock_path='src/backend/pyproject.toml',lock_digest=manifest['src/backend/pyproject.toml'],
        migration=argv('migrate'),seed=argv('seed'),checks=[argv('check')],browser='chromium',
        viewports=[dict(width=1440,height=900),dict(width=390,height=844)],selectors=['[data-testid="chat-shell"]'],
        steps=[{'action':'expect_visible','selector':'[data-testid="chat-shell"]'}])
    template = AcceptanceTemplate.parse(dict(schema_version=1,template='moonbox-chat-acceptance-v1',base=base,
        node_image=images['node'],runtime_versions=dict(python='3.12.15',node='24.22.0',mysql='8.4.13',chromium='156.0.8078.73',firefox='153.0'),
        roles=['member','reader'],checks={
            'AC-LOCAL-MEMBER':dict(argv=argv('check'),database='sqlite',role='member'),
            'AC-LOCAL-READER':dict(argv=argv('check'),database='mysql',role='reader')},
        disk_strategy='bounded-tmpfs',deployment_digest=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest(),
        identity_adapter=dict(issue=argv('issue'),revoke=argv('revoke'),login=dict(path='/api/v1/auth/login',username_field='username',password_field='password',mode='moonbox-session'))))
    template_path = root / 'template.json'
    selected_database=os.environ.get('MOONBOX_PRODUCT_DATABASE')
    if selected_database:
        if selected_database not in {'sqlite','mysql'}:raise ValueError('invalid_database')
        template.data['checks']={key:value for key,value in template.data['checks'].items() if value['database']==selected_database}
    template_path.write_text(json.dumps(template.data,indent=2))
    template_path.chmod(0o600)
    (root/'activate.sh').write_text('export MOONBOX_ACCEPTANCE_TEMPLATE='+str(template_path)+'\nexport MOONBOX_ACCEPTANCE_ROOT='+str(root/'environments')+'\nexport MOONBOX_ACCEPTANCE_SUBNET=10.248.48.0/28\n')
    (root/'activate.sh').chmod(0o600)
    engine = create_engine('sqlite:///'+str(root/'controller.db'))
    metadata.create_all(engine,tables=list(dict.fromkeys([conversations,turns,usage_accounts,*CONTENT,*CORE,*ROLLOUT,*ACCEPTANCE])))
    factory = sessionmaker(engine)
    with factory.begin() as db:
        workspace = register_main(db,'local-space','local-product',source)
        db.execute(insert(conversations).values(id='local-chat',created_at=stamp(),updated_at=stamp(),owner_id='local-user',space_id='local-space',repository_id='local-product',title='Local product matrix'))
        db.execute(insert(turns).values(id='local-turn',created_at=stamp(),updated_at=stamp(),conversation_id='local-chat',client_request_id='local-request',status='completed',prompt='Local product matrix'))
        db.execute(insert(session_bindings).values(conversation_id='local-chat',workspace_id=workspace['id']))
    snapshot = capture(factory,'local-chat','local-turn',source,'after',policy_roots=['src/backend/tests'])
    with factory.begin() as db:
        point = publish(db,workspace['id'],snapshot['version_id'],policy_version='local-product',head_commit=head,changed=True,scope=['src/backend/tests'])
    reference = dict(point_id=point['id'],workspace_id=workspace['id'],head_commit=head,manifest_hash=point['manifest_hash'])
    state = AcceptanceState(factory)
    operation = state.create(actor='local-user',space='local-space',repository='local-product',conversation='local-chat',turn='local-turn',
        change='local-product-check',request_key='local-product',binding='b'*64,input_digest='a'*64,
        plan={'checks':[{'id':ac,'inputs':['src/backend/pyproject.toml']} for ac in template.data['checks']]},source_ref=reference)
    print(json.dumps({'root':str(root),'operation':operation['id']}),flush=True)
    runtime = DockerRuntime(state,template,root/'environments')
    result = Controller(state,runtime,lambda _:None).run(operation['id'],'local-product-worker')
    report = {key:result[key] for key in ('status','cleanup_state','reason_code','checks')}
    report.update(category='real_moonbox_product_runtime',chat_round='not_exercised',source_hashes=manifest,template_digest=template.key)
    (root/'report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'root':str(root),'status':result['status'],'cleanup':result['cleanup_state'],'reason':result['reason_code'],
        'checks':[{k:c[k] for k in ('ac_id','status','reason_code')} for c in result['checks']]}),flush=True)
    if result['status'] != 'passed' or result['cleanup_state'] != 'released':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
