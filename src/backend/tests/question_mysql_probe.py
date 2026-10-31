"""Registered disposable MySQL probe; no credentials leave the temp directory."""
import os, secrets, subprocess, sys, tempfile, time
from pathlib import Path
import pymysql
name = 'moonbox-question-mysql-' + secrets.token_hex(4)
run = os.environ['QUESTION_DOCKER_RUN']; expires = os.environ['QUESTION_DOCKER_EXPIRES']
with tempfile.TemporaryDirectory(prefix='question-mysql-', dir='/private/tmp') as folder:
    root = Path(folder); secret = secrets.token_hex(24)
    envfile = root/'mysql.env';envfile.write_text('MYSQL_ROOT_PASSWORD='+secret+'\nMYSQL_DATABASE=chat_probe\n');envfile.chmod(0o600)
    try:
        subprocess.run(['docker','run','--rm','-d','--name',name,'--label','moonbox.temp.managed=true',
            '--label','moonbox.temp.run='+run,'--label','moonbox.temp.expires='+expires,
            '--env-file',str(envfile),'-p','127.0.0.1:39051:3306','--tmpfs','/var/lib/mysql:rw,size=512m',
            '--memory','1g','mysql:8.2.0'],check=True,stdout=subprocess.DEVNULL)
        for attempt in range(60):
            try:
                conn = pymysql.connect(host='127.0.0.1',port=39051,user='root',password=secret,database='chat_probe');conn.close();break
            except pymysql.MySQLError:time.sleep(1)
        env = {**os.environ, 'CHAT_TEST_DATABASE_URL':f'mysql+pymysql://root:{secret}@127.0.0.1:39051/chat_probe'}
        with (root/'result.log').open('w') as log:
            result = subprocess.run([sys.executable,'-m','pytest','src/backend/tests/test_chat_questions.py','-q','--tb=short'],env=env,stdout=log,stderr=subprocess.STDOUT)
        # Redact even synthetic credentials before printing failure details.
        output=(root/'result.log').read_text().replace(secret,'REDACTED')
        import json, hashlib, re
        evidence = Path('openspec/changes/fix-chat-midrun-question-response/evidence/acceptance/manual')
        evidence.mkdir(parents=True, exist_ok=True)
        files = ['src/backend/app/chat/question_schema.py','src/backend/app/chat/questions.py','src/backend/app/chat/question_bridge.py','src/backend/tests/test_chat_questions.py']
        summary = {'engine':'MySQL 8.2.0','exit_code':result.returncode,'passed':int(re.search(r'(\d+) passed',output).group(1)) if re.search(r'(\d+) passed',output) else 0,
                   'inputs':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in files},'synthetic_data':True,'credentials_retained':False}
        (evidence/'mysql.json').write_text(json.dumps(summary,indent=2)+'\n')
        print(output[-5000:]);sys.exit(result.returncode)
    finally:subprocess.run(['docker','rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
