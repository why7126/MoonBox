"""独立MySQL容器矩阵；不连接既有业务数据库，不输出随机测试凭证。"""
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time
import pymysql

name='moonbox-chat-mysql-probe-'+secrets.token_hex(4)
with tempfile.TemporaryDirectory(prefix='moonbox-mysql-',dir='/private/tmp') as folder:
    root=Path(folder);secret=secrets.token_hex(24);envfile=root/'mysql.env'
    envfile.write_text('MYSQL_ROOT_PASSWORD='+secret+'\nMYSQL_ROOT_HOST=%\nMYSQL_DATABASE=chat_probe\n');envfile.chmod(0o600)
    try:
        subprocess.run(['docker','run','--rm','-d','--name',name,'--env-file',str(envfile),'-p','127.0.0.1:18126:3306','--tmpfs','/var/lib/mysql:rw,size=512m','--memory','1g','mysql:8.2.0'],check=True,stdout=subprocess.DEVNULL)
        end=time.monotonic()+60
        while time.monotonic()<end:
            try:
                connection=pymysql.connect(host='127.0.0.1',port=18126,user='root',password=secret,database='chat_probe');connection.close();break
            except pymysql.MySQLError:time.sleep(1)
        else:raise RuntimeError('isolated MySQL readiness timeout')
        env={**os.environ,'CHAT_TEST_DATABASE_URL':f'mysql+pymysql://root:{secret}@127.0.0.1:18126/chat_probe'}
        with (root/'pytest.log').open('w') as log:
            result=subprocess.run([sys.executable,'-m','pytest','src/backend/tests/test_chat.py','src/backend/tests/test_chat_accounting.py','src/backend/tests/test_chat_unlimited.py','src/backend/tests/test_chat_cleanup_copies.py','-q','--tb=short'],env=env,stdout=log,stderr=subprocess.STDOUT)
        # Redact before persisting even failure logs; never return the raw DSN.
        safe=(root/'pytest.log').read_text().replace(secret,'REDACTED').replace(str(Path.cwd()),'[PROJECT]').replace(str(root),'[TEST]')
        Path('/tmp/moonbox-mysql-matrix.log').write_text(safe)
        print(json.dumps({'mysql':'8.2.0','exit_code':result.returncode,'summary':safe.splitlines()[-1]}))
    finally:
        subprocess.run(['docker','rm','-f',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
