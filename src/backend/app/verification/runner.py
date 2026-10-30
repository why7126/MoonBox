"""受信任控制器的浏览器启动探针；请求端不能指定 Docker 参数。"""
from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
from urllib.parse import urlsplit
from uuid import UUID

from app.chat.workspace import trusted_directory


class RunnerUnavailable(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def probe_browser_image(image_digest: str, *, timeout: int = 45) -> dict:
    """Validate both browser launch paths inside the exact immutable runner image."""
    if not isinstance(image_digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", image_digest):
        raise RunnerUnavailable("runner_image_unpinned")
    docker = shutil.which("docker")
    if not docker:
        raise RunnerUnavailable("container_runtime_unavailable")
    seccomp = Path(__file__).parents[2] / "container" / "seccomp-codex.json"
    command = [docker, "run", "--rm", "--init", "--network", "none", "--read-only",
               "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true",
               "--security-opt", f"seccomp={seccomp}",
               "--pids-limit", "128", "--memory", "1g", "--cpus", "1",
               "--tmpfs", "/tmp:rw,nosuid,size=128m", "--user", "10001:10001",
               "--env", "HOME=/tmp", "--env", "XDG_CACHE_HOME=/tmp",
               image_digest, "node", "/opt/moonbox-verification/probe.cjs"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RunnerUnavailable("browser_probe_failed") from exc
    if result.returncode:
        raise RunnerUnavailable("browser_probe_failed")
    try:
        payload = json.loads(result.stdout)
        versions = payload["browsers"]
        if payload.get("status") != "ready" or any(
            not isinstance(versions.get(browser), str) or not versions[browser]
            for browser in ("firefox", "chromium")
        ):
            raise ValueError("invalid probe result")
    except (ValueError, KeyError, TypeError) as exc:
        raise RunnerUnavailable("browser_probe_invalid") from exc
    if not isinstance(payload.get("node_version"), str) or not isinstance(payload.get("pnpm_version"), str):
        raise RunnerUnavailable("runner_toolchain_invalid")
    return {"firefox": True, "chromium": True, "system_libraries": True,
            "node_version": payload["node_version"], "pnpm_version": payload["pnpm_version"],
            "versions": {name: versions[name] for name in ("firefox", "chromium")}}


def run_browser_acceptance(image_digest: str, *, network: str, target_url: str,
                           browser: str, viewports: list[dict], selectors: list[str],
                           steps: list[dict] | None = None,
                           artifact_path: Path | None = None,
                           evidence_root: Path, space_id: str, repository_id: str,
                           task_id: str, timeout: int = 120, lifecycle_labels: dict | None = None,
                           identity_file: Path | None = None, login: dict | None = None) -> dict:
    """Run trusted browser checks; neither project source nor client commands execute here."""
    if not isinstance(image_digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", image_digest):
        raise RunnerUnavailable("runner_image_unpinned")
    if not isinstance(network, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", network):
        raise RunnerUnavailable("browser_network_invalid")
    if not isinstance(target_url, str) or len(target_url) > 300:
        raise RunnerUnavailable("target_invalid")
    parsed = urlsplit(target_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise RunnerUnavailable("target_invalid")
    if browser not in ("firefox", "chromium") or not isinstance(viewports, list) or not 1 <= len(viewports) <= 4:
        raise RunnerUnavailable("browser_plan_invalid")
    if not isinstance(selectors, list) or len(selectors) > 20 or any(not isinstance(s, str) or len(s) > 160 for s in selectors):
        raise RunnerUnavailable("browser_plan_invalid")
    steps = [] if steps is None else steps
    if not isinstance(steps, list) or len(steps) > 20:
        raise RunnerUnavailable("browser_plan_invalid")
    for step in steps:
        if not isinstance(step, dict) or step.get("action") not in ("click", "fill", "reload", "expect_visible", "expect_text"):
            raise RunnerUnavailable("browser_plan_invalid")
        action = step["action"]
        required = {"action"} if action == "reload" else {"action", "selector"}
        if action in ("fill", "expect_text"):
            required.add("value")
        if set(step) != required:
            raise RunnerUnavailable("browser_plan_invalid")
        if action != "reload" and (not isinstance(step["selector"], str) or not 1 <= len(step["selector"]) <= 160):
            raise RunnerUnavailable("browser_plan_invalid")
        if "value" in step and (not isinstance(step["value"], str) or not 1 <= len(step["value"]) <= 500):
            raise RunnerUnavailable("browser_plan_invalid")
    for viewport in viewports:
        if not isinstance(viewport, dict) or type(viewport.get("width")) is not int or type(viewport.get("height")) is not int:
            raise RunnerUnavailable("browser_plan_invalid")
        if not 320 <= viewport["width"] <= 3840 or not 320 <= viewport["height"] <= 2160:
            raise RunnerUnavailable("browser_plan_invalid")
    for value in (space_id, repository_id):
        if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value):
            raise RunnerUnavailable("project_identity_invalid")
    try:
        task_id = str(UUID(task_id))
    except (TypeError, ValueError, AttributeError) as exc:
        raise RunnerUnavailable("task_identity_invalid") from exc
    docker = shutil.which("docker")
    if not docker:
        raise RunnerUnavailable("container_runtime_unavailable")
    root = trusted_directory(evidence_root)
    if shutil.disk_usage(root).free < 128 * 1024 * 1024:
        raise RunnerUnavailable("evidence_capacity_insufficient")
    project_key = hashlib.sha256(f"{space_id}\0{repository_id}".encode()).hexdigest()
    project_root = root / project_key
    project_root.mkdir(mode=0o700, exist_ok=True)
    trusted_directory(project_root)
    target = project_root / task_id
    target.mkdir(mode=0o700)
    seccomp = Path(__file__).parents[2] / "container" / "seccomp-codex.json"
    container_name = "moonbox-verification-" + task_id
    command = [docker, "run", "--log-driver", "none", "--rm", "--init", "--interactive", "--name", container_name,
               "--network", network, "--read-only",
               "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true",
               "--security-opt", f"seccomp={seccomp}", "--pids-limit", "256", "--memory", "1g", "--cpus", "1",
               "--tmpfs", "/tmp:rw,nosuid,size=128m", "--ulimit", "fsize=10485760:10485760", "--user", f"{os.getuid()}:{os.getgid()}",
               "--env", "HOME=/tmp", "--env", "XDG_CACHE_HOME=/tmp",
               "--mount", f"type=bind,src={target},dst=/evidence"]
    for key, value in (lifecycle_labels or {}).items():
        if not re.fullmatch(r'moonbox\.(candidate|temp)\.[a-z]+', key) or not re.fullmatch(r'[a-zA-Z0-9-]{1,64}', value):
            raise RunnerUnavailable('resource_label_invalid')
        command.extend(['--label', key + '=' + value])
    if artifact_path is not None:
        artifact = trusted_directory(artifact_path)
        if not (artifact / "verified.json").is_file():
            raise RunnerUnavailable("artifact_unverified")
        command.extend(["--mount", f"type=bind,src={artifact},dst=/dependencies,readonly",
                        "--env", "MOONBOX_VERIFICATION_PROJECT_ARTIFACT=/dependencies"])
    if identity_file is not None:
        private = Path(identity_file)
        info = private.lstat()
        if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_mode & 0o077
                or info.st_size > 16384 or info.st_uid != os.getuid()):
            raise RunnerUnavailable('identity_media_invalid')
        trusted_directory(private.parent)
        if (not isinstance(login, dict) or set(login) not in ({'path','username_field','password_field'}, {'path','username_field','password_field','mode'})
                or login.get('mode','cookie') not in {'cookie','moonbox-session'}
                or login.get('mode') == 'moonbox-session' and login.get('path') != '/api/v1/auth/login'
                or not re.fullmatch(r'/[a-zA-Z0-9/_-]+',str(login['path']))
                or any(not re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]{0,63}',str(login[key])) for key in ('username_field','password_field'))):
            raise RunnerUnavailable('identity_login_invalid')
        command.extend(['--mount',f'type=bind,src={private},dst=/identity/credentials.json,readonly'])
    elif login is not None:
        raise RunnerUnavailable('identity_media_missing')
    command.extend([image_digest, "node", "/opt/moonbox-verification/acceptance.cjs"])
    plan = {"url": target_url, "browser": browser, "viewports": viewports, "selectors": selectors, "steps": steps}
    if identity_file is not None: plan['login'] = login
    try:
        completed = subprocess.run(command, input=json.dumps(plan), text=True, capture_output=True,
                                   timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        try:
            subprocess.run([docker, "rm", "--force", container_name], capture_output=True, timeout=15, check=False)
        except (OSError, subprocess.TimeoutExpired):
            pass
        raise RunnerUnavailable("browser_acceptance_timed_out") from exc
    if completed.returncode:
        code = completed.stderr.strip().splitlines()[-1:] or []
        allowed = {"plan_too_large", "browser_invalid", "viewports_invalid", "target_invalid",
                   "selectors_invalid", "steps_invalid", "viewport_invalid", "target_response_failed", "selector_missing", "step_failed",
                   "identity_login_invalid", "identity_expired", "identity_login_failed"}
        raise RunnerUnavailable(code[0] if code and code[0] in allowed else "browser_acceptance_failed")
    try:
        result = json.loads(completed.stdout)
        if result.get("category") != "real_browser" or result.get("browser") != browser:
            raise ValueError()
        if not isinstance(result.get("browser_version"), str) or len(result["viewports"]) != len(viewports):
            raise ValueError()
        for row in result["viewports"]:
            filename = row["screenshot"]
            if not re.fullmatch(r"(firefox|chromium)-[0-9]{3,4}x[0-9]{3,4}\.png", filename):
                raise ValueError()
            screenshot = target / filename
            if screenshot.is_symlink() or not screenshot.is_file() or not 0 < screenshot.stat().st_size <= 10 * 1024 * 1024:
                raise ValueError()
    except (ValueError, KeyError, TypeError) as exc:
        raise RunnerUnavailable("browser_evidence_invalid") from exc
    return {"task_id": task_id, "environment_image": image_digest, "category": "real_browser",
            "browser": browser, "browser_version": result["browser_version"],
            "viewports": result["viewports"]}
