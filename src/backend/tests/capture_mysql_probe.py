"""Disposable MySQL check. Never connects to an existing application database."""
import json,os,secrets,subprocess,sys,tempfile,time
from pathlib import Path
import pymysql
name='moonbox-capture-mysql-'+secrets.token_hex(4)
with tempfile.TemporaryDirectory(prefix='capture-mysql-') as folder:
    root=Path(folder);secret=secrets.token_hex(24);envfile=root/'mysql.env'
    envfile.write_text('MYSQL_ROOT_PASSWORD='+secret+'\nMYSQL_ROOT_HOST=%\nMYSQL_DATABASE=capture_probe\n');envfile.chmod(0o600)
    try:
        subprocess.run(['docker','run','--rm','-d','--name',name,'--env-file',str(envfile),'-p','127.0.0.1::3306','--tmpfs','/var/lib/mysql:rw,size=512m','--memory','1g','mysql:8.2.0'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        port=int(subprocess.check_output(['docker','port',name,'3306/tcp'],text=True).strip().rsplit(':',1)[1])
        until=time.monotonic()+60
        while time.monotonic()<until:
            try:
                conn=pymysql.connect(host='127.0.0.1',port=port,user='root',password=secret,database='capture_probe');conn.close();break
            except pymysql.MySQLError:time.sleep(1)
        else:raise RuntimeError('isolated_mysql_not_ready')
        env={**os.environ,'CHAT_TEST_DATABASE_URL':f'mysql+pymysql://root:{secret}@127.0.0.1:{port}/capture_probe'}
        completed=subprocess.run([sys.executable,'-m','pytest','tests/test_capture_drafts.py','tests/test_capture_media.py','-q','--tb=short'],env=env,capture_output=True,text=True)
        safe=(completed.stdout+completed.stderr).replace(secret,'REDACTED').replace(str(Path.cwd()),'[BACKEND]').replace(str(root),'[TEST]')
        evidence=Path('../../openspec/changes/add-capture-multimodal-candidate-review/evidence/mysql-tests.txt')
        evidence.write_text(safe)
        print(json.dumps({'mysql':'8.2.0','exit_code':completed.returncode,'summary':safe.splitlines()[-1]}))
        sys.exit(completed.returncode)
    finally:subprocess.run(['docker','rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
