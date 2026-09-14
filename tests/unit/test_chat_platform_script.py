import json
import os
from pathlib import Path
import subprocess
from test_docker_up_script import _fake_docker

PROJECT=Path(__file__).resolve().parents[2]


def test_platform_missing_mapping_fails_before_docker(tmp_path):
    capture=tmp_path/'capture';envfile=tmp_path/'local.env';envfile.write_text('')
    env={**os.environ,'ENV_FILE':str(envfile),'PATH':str(_fake_docker(tmp_path))+':'+os.environ['PATH'],'DOCKER_UP_CAPTURE':str(capture)}
    for key in ('MOONBOX_CHAT_SPACE_ID','MOONBOX_CHAT_REPOSITORY_ID','MOONBOX_CHAT_SOURCE_ROOT'):env[key]=''
    result=subprocess.run(['bash','scripts/docker-up.sh','self-storage-sqlite','--chat-platform','--check'],cwd=PROJECT,env=env,capture_output=True)
    assert result.returncode != 0 and not capture.exists()


def test_platform_check_is_readonly_and_start_uses_matching_override(tmp_path):
    root=tmp_path.resolve();source=root/'source';source.mkdir();(source/'file').write_text('seed')
    for args in (['init','-q',str(source)],['-C',str(source),'add','file'],['-C',str(source),'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','seed']):
        subprocess.run(['git',*args],check=True,capture_output=True)
    auth=root/'auth.json';auth.write_text('{"OPENAI_API_KEY":"synthetic"}');auth.chmod(0o600)
    data=root/'private';envfile=root/'local.env';capture=root/'capture'
    values={'MOONBOX_CHAT_SOURCE_ROOT':str(source),'MOONBOX_CHAT_HOST_ROOT':str(data),
        'MOONBOX_CHAT_REPOSITORY_ID':'repo','MOONBOX_CHAT_SPACE_ID':'space','MOONBOX_CHAT_AUTH_SOURCE':str(auth),'MOONBOX_CHAT_EXECUTION_MODE':'local-codex'}
    envfile.write_text('\n'.join(key+'='+value for key,value in values.items()))
    env={**os.environ,'ENV_FILE':str(envfile),'PATH':str(_fake_docker(root))+':'+os.environ['PATH'],'DOCKER_UP_CAPTURE':str(capture)}
    command=['bash','scripts/docker-up.sh','self-storage-sqlite']
    result=subprocess.run([*command,'--check'],cwd=PROJECT,env=env,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert not data.exists()
    result=subprocess.run(command,cwd=PROJECT,env=env,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert (data/'backups/deletions.sqlite').exists()
    text=capture.read_text()
    assert 'docker-compose.chat-platform.yml' in text
    assert 'up -d --wait --wait-timeout 180 backend web minio chat-worker' in text
    assert not (data/'auth.json').exists()
