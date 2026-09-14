import os
from pathlib import Path
import subprocess
import sys
import pytest

ROOT=Path(__file__).resolve().parents[2]


def run(tmp_path,script,args,config='',docker_fail=False):
    envfile=tmp_path/'test.env';envfile.write_text(config)
    capture=tmp_path/'calls';binary=tmp_path/'bin';binary.mkdir()
    docker=binary/'docker'
    docker.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$CAPTURE"\nexit '+('7' if docker_fail else '0')+'\n');docker.chmod(0o755)
    env={**os.environ,'ENV_FILE':str(envfile),'CAPTURE':str(capture),'PATH':str(binary)+':'+os.environ['PATH'],'PYTHON_BIN':sys.executable}
    for key in ('DATABASE_TYPE','DATABASE_URL','COMPOSE_FILE','MOONBOX_ENV_FILE'):env.pop(key,None)
    result=subprocess.run(['bash',str(ROOT/'scripts'/script),*args],cwd=tmp_path,env=env,capture_output=True,text=True)
    return result,capture.read_text() if capture.exists() else ''


def test_down_selects_same_env_from_other_directory_and_keeps_data(tmp_path):
    result,calls=run(tmp_path,'docker-down.sh',['self-storage-sqlite'])
    assert result.returncode==0,result.stderr
    assert '--env-file '+str(tmp_path/'test.env') in calls
    assert str(ROOT/'docker-compose.yml') in calls
    assert calls.rstrip().endswith(' down')
    assert '--volumes' not in calls and ' -v' not in calls


@pytest.mark.parametrize('args',[['invalid'],['self-storage-sqlite','--unknown'],['self-storage-self-mysql','--chat-test']])
def test_invalid_arguments_fail_before_docker(tmp_path,args):
    result,calls=run(tmp_path,'docker-up.sh',args)
    assert result.returncode!=0
    assert not calls


def test_compose_failure_never_prints_started(tmp_path):
    result,_=run(tmp_path,'docker-up.sh',['self-storage-sqlite'],docker_fail=True)
    assert result.returncode==7
    assert '服务已按模式启动' not in result.stdout


def test_database_mode_mismatch_is_rejected(tmp_path):
    result,calls=run(tmp_path,'docker-up.sh',['self-storage-sqlite'],'DATABASE_TYPE=mysql\n')
    assert result.returncode!=0 and not calls


def test_mysql_mode_passes_profile_and_services(tmp_path):
    result,calls=run(tmp_path,'docker-up.sh',['self-storage-self-mysql'])
    assert result.returncode==0,result.stderr
    assert '--profile mysql' in calls and 'backend web minio mysql' in calls


def test_check_is_readonly(tmp_path):
    result,calls=run(tmp_path,'docker-up.sh',['self-storage-sqlite','--check'])
    assert result.returncode==0,result.stderr
    assert 'config --quiet' in calls and ' up ' not in calls and 'build' not in calls


def test_bad_database_config_does_not_block_down(tmp_path):
    result,calls=run(tmp_path,'docker-down.sh',['self-storage-sqlite'],'DATABASE_TYPE=mysql\n')
    assert result.returncode==0,result.stderr
    assert calls.rstrip().endswith(' down')
