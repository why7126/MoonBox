"""授权项目的只读环境预检；路径和镜像只从服务端配置读取。"""
from __future__ import annotations

import os
from pathlib import Path, PurePosixPath
import json
import time
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPHandler, HTTPSHandler, HTTPRedirectHandler
from urllib.error import URLError

from app.chat import service as chat_service
from app.chat.settings import repository_binding
from app.chat.workspace import trusted_directory, WorkspaceError
from app.verification.environment import EnvironmentError, inspect_environment, preflight
from app.verification.artifacts import verified_artifact
from app.verification.preparation import _registry, PreparationError


def _project_root(binding: dict) -> Path:
    source = trusted_directory(binding["source_root"])
    relative = binding.get("verification_project_subdir", ".")
    if not isinstance(relative, str) or len(relative) > 160:
        raise EnvironmentError("project_subdirectory_invalid")
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or any(part.startswith(".") and part != "." for part in path.parts):
        raise EnvironmentError("project_subdirectory_invalid")
    project = trusted_directory(source.joinpath(*path.parts))
    if project != source and source not in project.parents:
        raise EnvironmentError("project_subdirectory_invalid")
    return project


def _target_ready(binding: dict) -> bool:
    target = binding.get("verification_target_url")
    if not isinstance(target, str) or len(target) > 300:
        return False
    parsed = urlsplit(target)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        return False
    try:
        # The binding is administrator-owned. Redirects are not followed.
        class NoRedirect(HTTPRedirectHandler):
            def redirect_request(self, request, fp, code, message, headers, new_url):
                return None
        opener = build_opener(HTTPHandler, HTTPSHandler, NoRedirect)
        request = Request(target, method="HEAD")
        with opener.open(request, timeout=3) as response:
            return 200 <= response.status < 400 and response.url == target
    except (OSError, URLError, ValueError):
        return False


def _worker_browsers(image_digest: str) -> dict | None:
    state = os.environ.get("MOONBOX_VERIFICATION_STATE_ROOT", "")
    if not state:
        return None
    try:
        root = trusted_directory(state)
        marker = root / "worker-ready.json"
        if marker.is_symlink() or not marker.is_file() or marker.stat().st_size > 2048:
            return None
        payload = json.loads(marker.read_text())
        if payload.get("image_digest") != image_digest or not 0 <= time.time() - payload["time"] < 5:
            return None
        if payload.get("node_version") != os.environ.get("MOONBOX_VERIFICATION_NODE_VERSION"):
            return None
        if payload.get("pnpm_version") != os.environ.get("MOONBOX_VERIFICATION_PNPM_VERSION"):
            return None
        if payload.get("architecture") != os.environ.get("MOONBOX_VERIFICATION_ARCH"):
            return None
        versions = payload["browsers"]
        if not all(isinstance(versions.get(name), str) and versions[name] for name in ("firefox", "chromium")):
            return None
        return {"firefox": True, "chromium": True, "system_libraries": True,
                "pnpm_version": payload["pnpm_version"], "versions": versions}
    except (OSError, WorkspaceError, KeyError, TypeError, ValueError):
        return None


def inspect_authorized(db, actor: str, space_id: str, repository_id: str) -> dict:
    chat_service.authorize_space(db, actor, space_id)
    binding = repository_binding(repository_id, space_id)
    if not binding:
        raise chat_service.ChatError(2503, "项目未绑定或不可访问", 403)
    try:
        project = _project_root(binding)
        item = inspect_environment(
            project,
            node_version=os.environ.get("MOONBOX_VERIFICATION_NODE_VERSION", ""),
            os_name=os.environ.get("MOONBOX_VERIFICATION_OS", "linux"),
            architecture=os.environ.get("MOONBOX_VERIFICATION_ARCH", ""),
            image_digest=os.environ.get("MOONBOX_VERIFICATION_IMAGE_ID", ""),
        )
    except (EnvironmentError, WorkspaceError, KeyError) as exc:
        code = exc.code if isinstance(exc, EnvironmentError) else "project_directory_unavailable"
        return {"status": "unavailable", "reason_code": code, "environment_key": None, "checks": {}}
    artifact_root = os.environ.get("MOONBOX_VERIFICATION_ARTIFACT_ROOT", "")
    artifact_exists = False
    if artifact_root:
        try:
            root = trusted_directory(artifact_root)
            artifact_exists = verified_artifact(root, item) is not None
        except WorkspaceError:
            artifact_exists = False
    browsers = _worker_browsers(item.image_digest)
    if browsers is None:
        return {"status": "unavailable", "reason_code": "verification_worker_unavailable", "environment_key": item.key,
                "checks": {"dependencies": artifact_exists, "firefox": False, "chromium": False,
                           "system_libraries": False, "target": False}}
    if item.manager != "pnpm" or item.manager_version != browsers["pnpm_version"]:
        return {"status": "unavailable", "reason_code": "package_manager_image_mismatch",
                "environment_key": item.key, "checks": {"dependencies": artifact_exists,
                "firefox": True, "chromium": True, "system_libraries": True, "target": False}}
    target_reachable = _target_ready(binding)
    network = os.environ.get("MOONBOX_VERIFICATION_PREPARE_NETWORK", "")
    registry = os.environ.get("MOONBOX_VERIFICATION_REGISTRY_URL", "")
    try:
        _registry(registry)
        source_available = bool(network and network != "none")
    except PreparationError:
        source_available = False
    result = preflight(item, artifact_exists=artifact_exists, browser_probe=browsers,
                       target_reachable=target_reachable, artifact_source_available=source_available)
    return result
