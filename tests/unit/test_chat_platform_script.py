import json
import os
from pathlib import Path
import subprocess
from test_docker_up_script import _fake_docker
import yaml

PROJECT=Path(__file__).resolve().parents[2]


def _service(path, name):
    document = yaml.safe_load((PROJECT / path).read_text(encoding="utf-8"))
    return document["services"][name]


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


def test_chat_overlay_services_have_stable_container_names():
    cases = [
        (
            "deploy/docker-compose.chat-platform.yml",
            "chat-worker",
            "${CHAT_WORKER_CONTAINER_NAME:-moonbox-chat-worker}",
        ),
        (
            "deploy/docker-compose.governance.yml",
            "governance-controller",
            "${GOVERNANCE_CONTROLLER_CONTAINER_NAME:-moonbox-governance-controller}",
        ),
        (
            "deploy/local/compose.chat-recovery.yml",
            "chat-recovery",
            "${CHAT_RECOVERY_CONTAINER_NAME:-moonbox-chat-recovery}",
        ),
    ]
    for path, service_name, expected in cases:
        assert _service(path, service_name)["container_name"] == expected


def test_chat_overlay_container_name_defaults_do_not_use_compose_suffixes():
    for variable in (
        "CHAT_WORKER_CONTAINER_NAME",
        "GOVERNANCE_CONTROLLER_CONTAINER_NAME",
        "CHAT_RECOVERY_CONTAINER_NAME",
    ):
        assert variable in (PROJECT / ".env.example").read_text(encoding="utf-8")
    defaults = {
        "chat-worker": "moonbox-chat-worker",
        "governance-controller": "moonbox-governance-controller",
        "chat-recovery": "moonbox-chat-recovery",
    }
    for service_name, default in defaults.items():
        assert not default.endswith("-1")


def test_chat_and_governance_overlays_mount_agent_skills_readonly():
    chat_backend = _service("deploy/docker-compose.chat-platform.yml", "backend")
    chat_worker = _service("deploy/docker-compose.chat-platform.yml", "chat-worker")
    governance_backend = _service("deploy/docker-compose.governance.yml", "backend")
    governance_controller = _service("deploy/docker-compose.governance.yml", "governance-controller")
    expected = "./.agents:/app/governance/.agents:ro"
    for service in (chat_backend, chat_worker, governance_backend, governance_controller):
        assert expected in service["volumes"]
