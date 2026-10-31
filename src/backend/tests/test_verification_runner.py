import json
from types import SimpleNamespace
from pathlib import Path
from uuid import uuid4

import pytest

from app.verification.runner import RunnerUnavailable, probe_browser_image, run_browser_acceptance


def test_probe_uses_immutable_image_and_restricted_container(monkeypatch):
    seen = []
    monkeypatch.setattr("app.verification.runner.shutil.which", lambda _: "/usr/bin/docker")

    def run(command, **kwargs):
        seen.extend(command)
        return SimpleNamespace(returncode=0, stdout=json.dumps({"status": "ready", "browsers": {"chromium": "1", "firefox": "2"},
            "node_version": "24.18.1", "pnpm_version": "11.2.2"}))

    monkeypatch.setattr("app.verification.runner.subprocess.run", run)
    assert probe_browser_image("sha256:" + "a" * 64)["firefox"] is True
    assert "none" in seen and "--read-only" in seen and "--cap-drop" in seen
    assert "sha256:" + "a" * 64 in seen
    assert not any("/var/run/docker.sock" in value for value in seen)


def test_probe_rejects_unpinned_or_failed_image(monkeypatch):
    with pytest.raises(RunnerUnavailable, match="runner_image_unpinned"):
        probe_browser_image("latest")
    monkeypatch.setattr("app.verification.runner.shutil.which", lambda _: "/usr/bin/docker")
    monkeypatch.setattr("app.verification.runner.subprocess.run", lambda argv, **k: SimpleNamespace(returncode=0 if argv[1]=="rm" else 1, stdout=""))
    with pytest.raises(RunnerUnavailable, match="browser_probe_failed"):
        probe_browser_image("sha256:" + "a" * 64)


def test_acceptance_isolated_evidence_and_rejects_client_target(monkeypatch, tmp_path):
    monkeypatch.setattr("app.verification.runner.shutil.which", lambda _: "/usr/bin/docker")
    commands = []

    def run(command, **kwargs):
        commands.append(command)
        mount = command[command.index("--mount") + 1]
        evidence = Path(mount.removeprefix("type=bind,src=").removesuffix(",dst=/evidence"))
        (evidence / "chromium-1440x900.png").write_bytes(b"\x89PNGtest")
        return SimpleNamespace(returncode=0, stdout=json.dumps({"category": "real_browser", "browser": "chromium",
            "browser_version": "151", "viewports": [{"width": 1440, "height": 900,
            "screenshot": "chromium-1440x900.png", "styles": {}, "assertion_count": 1}]}), stderr="")

    monkeypatch.setattr("app.verification.runner.subprocess.run", run)
    task = str(uuid4())
    params = dict(network="preview-only", target_url="http://preview/", browser="chromium",
                  viewports=[{"width": 1440, "height": 900}], selectors=[], evidence_root=tmp_path,
                  repository_id="repo", task_id=task)
    first = run_browser_acceptance("sha256:" + "a" * 64, space_id="space-a", **params)
    second = run_browser_acceptance("sha256:" + "a" * 64, space_id="space-b", **{**params, "task_id": str(uuid4())})
    assert first["category"] == "real_browser" and second["category"] == "real_browser"
    assert commands[0][commands[0].index("--mount") + 1] != commands[1][commands[1].index("--mount") + 1]
    assert "--read-only" in commands[0] and "--interactive" in commands[0]
    assert commands[0][commands[0].index('--ulimit') + 1] == 'fsize=134217728:134217728'
    assert commands[0][commands[0].index("--pids-limit") + 1] == "256"
    with pytest.raises(RunnerUnavailable, match="target_invalid"):
        run_browser_acceptance("sha256:" + "a" * 64, space_id="space-a", **{**params, "target_url": "file:///etc/passwd"})
    with pytest.raises(RunnerUnavailable, match="browser_network_invalid"):
        run_browser_acceptance("sha256:" + "a" * 64, space_id="space-a", **{**params, "network": "../../host"})
    with pytest.raises(RunnerUnavailable, match="browser_plan_invalid"):
        run_browser_acceptance("sha256:" + "a" * 64, space_id="space-a", **{**params, "viewports": [{"width": 1, "height": 1}]})
    with pytest.raises(RunnerUnavailable, match="browser_plan_invalid"):
        run_browser_acceptance("sha256:" + "a" * 64, space_id="space-a", **{**params, "steps": [{"action": "evaluate", "selector": "body"}]})
    with pytest.raises(RunnerUnavailable, match="browser_plan_invalid"):
        run_browser_acceptance("sha256:" + "a" * 64, space_id="space-a", **{**params, "steps": [{"action": "click", "selector": "body", "host_path": "/etc"}]})


def test_acceptance_mounts_only_verified_artifact_readonly(monkeypatch, tmp_path):
    monkeypatch.setattr("app.verification.runner.shutil.which", lambda _: "/usr/bin/docker")
    artifact = tmp_path / "artifact"
    artifact.mkdir()
    (artifact / "verified.json").write_text("{}")
    (tmp_path / "evidence").mkdir()
    seen = []

    def run(command, **kwargs):
        seen.extend(command)
        evidence = Path(next(value for value in command if value.endswith(",dst=/evidence")).split("src=", 1)[1].split(",dst=", 1)[0])
        (evidence / "firefox-390x844.png").write_bytes(b"\x89PNGtest")
        return SimpleNamespace(returncode=0, stdout=json.dumps({"category": "real_browser", "browser": "firefox",
            "browser_version": "153", "viewports": [{"width": 390, "height": 844,
            "screenshot": "firefox-390x844.png", "styles": {}, "assertion_count": 1}]}), stderr="")

    monkeypatch.setattr("app.verification.runner.subprocess.run", run)
    run_browser_acceptance("sha256:" + "a" * 64, network="preview", target_url="http://web/",
        browser="firefox", viewports=[{"width": 390, "height": 844}], selectors=[],
        artifact_path=artifact, evidence_root=tmp_path / "evidence", space_id="space",
        repository_id="repo", task_id=str(uuid4()))
    assert f"type=bind,src={artifact},dst=/dependencies,readonly" in seen
    assert "MOONBOX_VERIFICATION_PROJECT_ARTIFACT=/dependencies" in seen


def test_acceptance_blocks_when_evidence_disk_capacity_is_low(monkeypatch, tmp_path):
    monkeypatch.setattr("app.verification.runner.shutil.which", lambda _: "/usr/bin/docker")
    monkeypatch.setattr("app.verification.runner.shutil.disk_usage",
                        lambda _: SimpleNamespace(free=1024))
    with pytest.raises(RunnerUnavailable, match="evidence_capacity_insufficient"):
        run_browser_acceptance("sha256:" + "a" * 64, network="preview", target_url="http://web/",
            browser="firefox", viewports=[{"width": 390, "height": 844}], selectors=[],
            evidence_root=tmp_path, space_id="space", repository_id="repo", task_id=str(uuid4()))


@pytest.mark.parametrize('mode,path,allowed',[
    ('moonbox-session','/api/v1/auth/login',True),
    ('moonbox-session','/other',False),('arbitrary-script','/api/v1/auth/login',False),
    ('cookie','/login',True)])
def test_product_login_is_explicit_and_never_embeds_credentials(monkeypatch,tmp_path,mode,path,allowed):
    private=tmp_path/'identity';private.write_text('{"password":"private-test-value"}');private.chmod(0o600)
    monkeypatch.setattr('app.verification.runner.shutil.which',lambda _: '/usr/bin/docker')
    def run(command,**kwargs):
        assert 'private-test-value' not in json.dumps([command,kwargs])
        assert json.loads(kwargs['input'])['login']['mode']==mode
        raise RuntimeError('validated_plan_reached_runner')
    monkeypatch.setattr('app.verification.runner.subprocess.run',run)
    params=dict(network='owned',target_url='http://owned/chat',browser='chromium',
        viewports=[dict(width=390,height=844)],selectors=[],evidence_root=tmp_path,
        space_id='space',repository_id='repo',task_id=str(uuid4()),identity_file=private,
        login=dict(mode=mode,path=path,username_field='username',password_field='password'))
    with pytest.raises(RuntimeError,match='validated_plan_reached_runner' if allowed else 'identity_login_invalid'):
        run_browser_acceptance('sha256:'+'a'*64,**params)


def test_probe_timeout_removes_exact_container(monkeypatch):
    import subprocess
    calls=[]
    monkeypatch.setattr('app.verification.runner.shutil.which',lambda _: '/usr/bin/docker')
    def run(argv,**kwargs):
        calls.append(argv)
        if argv[1]=='run':raise subprocess.TimeoutExpired(argv,45)
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr('app.verification.runner.subprocess.run',run)
    with pytest.raises(RunnerUnavailable,match='browser_probe_failed'):
        probe_browser_image('sha256:'+'a'*64)
    assert calls[1][-1]==calls[0][calls[0].index('--name')+1]
