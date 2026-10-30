"""Opt-in registered disposable MySQL state tests; never uses application DATABASE_URL."""
import json
import os
from pathlib import Path
import secrets
import subprocess
import tempfile
import time


def main():
    run=os.environ['MOONBOX_TEMP_RUN'];expires=os.environ['MOONBOX_TEMP_EXPIRES']
    if len(run)!=32 or any(c not in '0123456789abcdef' for c in run) or not expires.isdigit():
        raise ValueError('registration_required')
    labels=['--label','moonbox.temp.managed=true','--label','moonbox.temp.run='+run,'--label','moonbox.temp.expires='+expires]
    prefix='moonbox-ac-'+run[:12]; network=prefix+'-net';database=prefix+'-mysql';runner=prefix+'-test'
    password=secrets.token_hex(24)
    root=Path(__file__).resolve().parents[1]
    mysql=os.environ['CANDIDATE_MYSQL_IMAGE']; image=os.environ['CANDIDATE_PYTHON_IMAGE']
    def command(args,timeout=60,required=True):
        result=subprocess.run(['docker',*args],capture_output=True,text=True,timeout=timeout)
        if required and result.returncode:
            raise RuntimeError('docker_step_failed:'+result.stderr.replace(password,'[redacted]')[-1000:])
        return result
    report={'category':'real_mysql_synthetic_state','status':'blocked','cleanup':False}
    try:
        with tempfile.TemporaryDirectory(prefix='moonbox-ac-secrets-') as directory:
            env=Path(directory)/'db.env';env.write_text('MYSQL_ROOT_PASSWORD='+secrets.token_hex(24)+'\nMYSQL_DATABASE=acceptance_test_state\nMYSQL_USER=acceptance\nMYSQL_PASSWORD='+password+'\n');env.chmod(0o600)
            testenv=Path(directory)/'test.env';testenv.write_text('ACCEPTANCE_TEST_DATABASE_URL=mysql+pymysql://acceptance:'+password+'@'+database+'/acceptance_test_state\nPYTHONPATH=/source\n');testenv.chmod(0o600)
            subnet=os.environ.get('MOONBOX_ACCEPTANCE_TEST_SUBNET')
            network_options=[]
            if subnet:
                from ipaddress import ip_network
                parsed=ip_network(subnet,strict=True)
                if parsed.version!=4 or not parsed.is_private or parsed.prefixlen<24:
                    raise ValueError('private_test_subnet_required')
                network_options=['--subnet',str(parsed)]
            command(['network','create','--internal',*network_options,*labels,network])
            command(['run','-d','--name',database,'--network',network,*labels,'--read-only','--cap-drop','ALL',
                '--security-opt','no-new-privileges:true','--user','999:999','--cpus','1','--memory','2g','--pids-limit','256',
                '--tmpfs','/var/lib/mysql:rw,nosuid,uid=999,gid=999,size=1g','--tmpfs','/var/run/mysqld:rw,nosuid,uid=999,gid=999,size=64m',
                '--tmpfs','/tmp:rw,nosuid,size=64m','--env-file',str(env),mysql])
            for _ in range(60):
                if command(['exec',database,'mysqladmin','--protocol=tcp','--host=127.0.0.1','ping','--silent'],required=False).returncode==0:break
                time.sleep(1)
            else:raise RuntimeError('mysql_health_timeout')
            result=command(['run','--rm','--name',runner,'--network',network,*labels,'--read-only','--cap-drop','ALL',
                '--security-opt','no-new-privileges:true','--user','10001:10001','--cpus','1','--memory','2g','--pids-limit','256',
                '--tmpfs','/tmp:rw,nosuid,size=256m','--env','PYTHONDONTWRITEBYTECODE=1','--env-file',str(testenv),
                '--mount','type=bind,src='+str(root)+',dst=/source,readonly','--workdir','/source',image,
                'python','tests/acceptance_mysql_probe.py'],timeout=180,required=False)
            report.update(status='passed' if result.returncode==0 else 'failed',exit_code=result.returncode,
                          output=(result.stdout+result.stderr).replace(password,'[redacted]')[-8000:])
    finally:
        command(['rm','-f',runner,database],required=False)
        command(['network','rm',network],required=False)
        left=command(['container','ls','-aq','--filter','label=moonbox.temp.run='+run]).stdout.strip()
        nets=command(['network','ls','-q','--filter','name=^'+network+'$']).stdout.strip()
        report['cleanup']=not left and not nets
        Path(os.environ.get('MOONBOX_ACCEPTANCE_MYSQL_REPORT','/tmp/req0048-mysql-report.json')).write_text(json.dumps(report,indent=2))
    print(json.dumps({'status':report['status'],'cleanup':report['cleanup']}))
    return 0 if report['status']=='passed' and report['cleanup'] else 1


if __name__=='__main__':raise SystemExit(main())
