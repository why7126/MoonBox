"""从授权工作副本识别 Node 验证环境；不执行项目提供的命令。"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


class EnvironmentError(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


_EXACT = re.compile(r"^[0-9]+(?:\.[0-9]+){1,2}$")
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
_SAFE_COMPONENT = re.compile(r"^[a-z0-9][a-z0-9._-]{0,79}$")
_PLAYWRIGHT_PNPM = re.compile(r"^\s{6}'@playwright/test':\s*\n(?:\s{8}[^\n]*\n)*?\s{8}version:\s*([^\s(]+)", re.MULTILINE)


@dataclass(frozen=True)
class EnvironmentIdentity:
    key: str
    lock_sha256: str
    manager: str
    manager_version: str
    node_version: str
    playwright_version: str
    os_name: str
    architecture: str
    image_digest: str


def _regular_file(path: Path, limit: int) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise EnvironmentError("project_file_unavailable")
    if path.stat().st_size > limit:
        raise EnvironmentError("project_file_too_large")
    return path.read_bytes()


def _exact_version(value: object, code: str) -> str:
    if not isinstance(value, str) or not _EXACT.fullmatch(value):
        raise EnvironmentError(code)
    return value


def inspect_environment(project: Path, *, node_version: str, os_name: str,
                        architecture: str, image_digest: str) -> EnvironmentIdentity:
    """Identify immutable inputs; caller supplies trusted runner image and target platform."""
    project = Path(project)
    if project.is_symlink() or not project.is_dir():
        raise EnvironmentError("project_directory_unavailable")
    try:
        package = json.loads(_regular_file(project / "package.json", 1024 * 1024))
    except (ValueError, UnicodeDecodeError) as exc:
        raise EnvironmentError("package_manifest_invalid") from exc
    if not isinstance(package, dict):
        raise EnvironmentError("package_manifest_invalid")
    manager = package.get("packageManager")
    if not isinstance(manager, str):
        raise EnvironmentError("package_manager_unpinned")
    match = re.fullmatch(r"(pnpm|npm)@([0-9]+(?:\.[0-9]+){1,2})(?:\+sha512\.[A-Za-z0-9]+)?", manager)
    if not match:
        raise EnvironmentError("package_manager_unpinned")
    manager_name, manager_version = match.groups()
    lock_name = "pnpm-lock.yaml" if manager_name == "pnpm" else "package-lock.json"
    other_lock = "package-lock.json" if manager_name == "pnpm" else "pnpm-lock.yaml"
    if (project / other_lock).exists():
        raise EnvironmentError("multiple_lockfiles")
    lock = _regular_file(project / lock_name, 32 * 1024 * 1024)
    try:
        if manager_name == "pnpm":
            lock_text = lock.decode("utf-8")
            if not re.search(r"^lockfileVersion:\s*['\"]?9(?:\.0)?['\"]?\s*$", lock_text, re.MULTILINE):
                raise EnvironmentError("lockfile_version_unsupported")
            found = _PLAYWRIGHT_PNPM.search(lock_text)
            playwright = found.group(1) if found else None
        else:
            lock_json = json.loads(lock)
            if lock_json.get("lockfileVersion") not in (2, 3):
                raise EnvironmentError("lockfile_version_unsupported")
            playwright = (lock_json.get("packages") or {}).get("node_modules/@playwright/test", {}).get("version")
    except (UnicodeDecodeError, ValueError, AttributeError) as exc:
        if isinstance(exc, EnvironmentError):
            raise
        raise EnvironmentError("lockfile_invalid") from exc
    declared = (package.get("devDependencies") or {}).get("@playwright/test") or (package.get("dependencies") or {}).get("@playwright/test")
    if not playwright or not isinstance(declared, str):
        raise EnvironmentError("playwright_dependency_missing")
    playwright = _exact_version(playwright, "playwright_version_unpinned")
    if declared.lstrip("^~") != playwright:
        raise EnvironmentError("playwright_lockfile_mismatch")
    node_version = _exact_version(node_version, "node_version_unpinned")
    if not isinstance(image_digest, str) or not _DIGEST.fullmatch(image_digest):
        raise EnvironmentError("runner_image_unpinned")
    for value in (os_name, architecture):
        if not isinstance(value, str) or not _SAFE_COMPONENT.fullmatch(value):
            raise EnvironmentError("target_platform_invalid")
    lock_sha = hashlib.sha256(lock).hexdigest()
    fields = dict(lock_sha256=lock_sha, manager=manager_name, manager_version=manager_version,
                  node_version=node_version, playwright_version=playwright, os_name=os_name,
                  architecture=architecture, image_digest=image_digest)
    key = hashlib.sha256(json.dumps(fields, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return EnvironmentIdentity(key=key, **fields)


def preflight(identity: EnvironmentIdentity, *, artifact_exists: bool, browser_probe: dict[str, bool],
              target_reachable: bool, artifact_source_available: bool) -> dict:
    """Return stable readiness, without treating browser/system failures as test failures."""
    checks = {"dependencies": artifact_exists, "firefox": browser_probe.get("firefox") is True,
              "chromium": browser_probe.get("chromium") is True,
              "system_libraries": browser_probe.get("system_libraries") is True,
              "target": target_reachable}
    if not checks["firefox"] or not checks["chromium"] or not checks["system_libraries"]:
        missing = next(name for name in ("firefox", "chromium", "system_libraries") if not checks[name])
        return {"status": "unavailable", "reason_code": f"browser_{missing}_unavailable", "environment_key": identity.key, "checks": checks}
    if not target_reachable:
        return {"status": "unavailable", "reason_code": "target_unreachable", "environment_key": identity.key, "checks": checks}
    if not artifact_exists:
        return {"status": "preparable" if artifact_source_available else "unavailable",
                "reason_code": "artifact_missing" if artifact_source_available else "artifact_source_unavailable",
                "environment_key": identity.key, "checks": checks}
    return {"status": "ready", "reason_code": None, "environment_key": identity.key, "checks": checks}
