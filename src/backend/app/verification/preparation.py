"""在无凭证、无项目脚本的容器中按锁文件准备可复用 Node 制品。"""
from __future__ import annotations

import fcntl
import os
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import urlsplit
from uuid import uuid4

from app.chat.workspace import trusted_directory
from app.verification.artifacts import publish_artifact, verified_artifact
from app.verification.environment import EnvironmentError, EnvironmentIdentity


class PreparationError(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _registry(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment or parsed.query:
        raise PreparationError("registry_invalid")
    return value


def prepare_node_artifact(project: Path, root: Path, identity: EnvironmentIdentity,
                          *, registry_url: str, network: str, timeout: int = 600) -> Path:
    """Install only lockfile dependencies; a precreated Docker network controls fetch egress."""
    project, root = trusted_directory(project), trusted_directory(root)
    existing = verified_artifact(root, identity)
    if existing is not None:
        return existing
    if not re.fullmatch(r"[0-9a-f]{64}", identity.key):
        raise PreparationError("artifact_key_invalid")
    lock_path = root / (".prepare-" + identity.key + ".lock")
    if lock_path.is_symlink():
        raise PreparationError("artifact_lock_invalid")
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "r+b") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        existing = verified_artifact(root, identity)
        if existing is not None:
            return existing
        return _prepare_node_artifact_unlocked(project, root, identity,
            registry_url=registry_url, network=network, timeout=timeout)


def _prepare_node_artifact_unlocked(project: Path, root: Path, identity: EnvironmentIdentity,
                                    *, registry_url: str, network: str, timeout: int) -> Path:
    project, root = trusted_directory(project), trusted_directory(root)
    existing = verified_artifact(root, identity)
    if existing is not None:
        return existing
    if shutil.disk_usage(root).free < 2 * 1024 * 1024 * 1024:
        raise PreparationError("artifact_capacity_insufficient")
    if identity.manager != "pnpm":
        raise PreparationError("package_manager_unsupported")
    if not isinstance(network, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", network):
        raise PreparationError("prepare_network_invalid")
    registry_url = _registry(registry_url)
    docker = shutil.which("docker")
    if not docker:
        raise PreparationError("container_runtime_unavailable")
    lock = project / "pnpm-lock.yaml"
    package = project / "package.json"
    if any(path.is_symlink() or not path.is_file() for path in (lock, package)):
        raise PreparationError("project_manifest_unavailable")
    lock_bytes = lock.read_bytes()
    if re.search(rb"\b(?:tarball:|git\+|https?://|file:|link:)", lock_bytes, re.IGNORECASE):
        raise PreparationError("lockfile_external_source")
    staging = root / ("preparing-" + uuid4().hex)
    staging.mkdir(mode=0o700)
    try:
        (staging / "pnpm-lock.yaml").write_bytes(lock_bytes)
        (staging / "package.json").write_bytes(package.read_bytes())
        command = [docker, "run", "--rm", "--init", "--network", network,
                   "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges:true",
                   "--pids-limit", "128", "--memory", "2g", "--cpus", "2",
                   "--tmpfs", "/tmp:rw,nosuid,size=256m", "--user", f"{os.getuid()}:{os.getgid()}",
                   "--env", "HOME=/tmp", "--env", "XDG_CACHE_HOME=/tmp",
                   "--env", f"npm_config_registry={registry_url}",
                   "--mount", f"type=bind,src={staging},dst=/work", "--workdir", "/work",
                   identity.image_digest, "pnpm", "install", "--frozen-lockfile", "--ignore-scripts",
                   "--package-import-method=copy", "--store-dir=/work/.pnpm-store"]
        try:
            result = subprocess.run(command, capture_output=True, timeout=timeout, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise PreparationError("artifact_install_failed") from exc
        if result.returncode:
            raise PreparationError("artifact_install_failed")
        if not (staging / "node_modules").is_dir() or (staging / "node_modules").is_symlink():
            raise PreparationError("artifact_install_incomplete")
        shutil.rmtree(staging / ".pnpm-store", ignore_errors=True)
        (staging / "package.json").unlink()
        (staging / "pnpm-lock.yaml").unlink()
        return publish_artifact(staging, root, identity)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
