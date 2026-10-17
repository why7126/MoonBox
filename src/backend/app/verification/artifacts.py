"""版本化 Node 依赖制品的不可变目录与完整性校验。"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat

from app.chat.workspace import trusted_directory
from app.verification.environment import EnvironmentIdentity


class ArtifactError(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if relative == "verified.json":
            continue
        info = path.lstat()
        digest.update(relative.encode() + b"\0")
        if stat.S_ISLNK(info.st_mode):
            target = os.readlink(path)
            resolved = (path.parent / target).resolve()
            if Path(target).is_absolute() or (resolved != root and root not in resolved.parents):
                raise ArtifactError("artifact_symlink_escape")
            digest.update(b"link\0" + target.encode() + b"\0")
        elif stat.S_ISDIR(info.st_mode):
            digest.update(b"dir\0")
        elif stat.S_ISREG(info.st_mode):
            if info.st_nlink != 1:
                raise ArtifactError("artifact_hardlink_rejected")
            digest.update(b"file\0")
            with path.open("rb") as stream:
                while block := stream.read(1024 * 1024):
                    digest.update(block)
        else:
            raise ArtifactError("artifact_special_file")
    return digest.hexdigest()


def _key(identity: EnvironmentIdentity) -> str:
    if not re.fullmatch(r"[0-9a-f]{64}", identity.key):
        raise ArtifactError("artifact_key_invalid")
    return identity.key


def _semantic_check(root: Path, identity: EnvironmentIdentity) -> None:
    package = root / "node_modules" / "@playwright" / "test" / "package.json"
    resolved = package.resolve()
    if root not in resolved.parents or not package.is_file():
        raise ArtifactError("artifact_playwright_missing")
    try:
        if json.loads(package.read_text(encoding="utf-8")).get("version") != identity.playwright_version:
            raise ArtifactError("artifact_playwright_mismatch")
    except (OSError, ValueError, AttributeError) as exc:
        raise ArtifactError("artifact_playwright_invalid") from exc


def publish_artifact(staging: Path, root: Path, identity: EnvironmentIdentity) -> Path:
    """Publish a prepared, credential-free tree after validating every entry."""
    root = trusted_directory(root)
    staging = trusted_directory(staging)
    if staging.parent != root or not staging.name.startswith("preparing-"):
        raise ArtifactError("artifact_staging_invalid")
    destination = root / _key(identity)
    if destination.exists() or destination.is_symlink():
        raise ArtifactError("artifact_already_exists")
    if (staging / "verified.json").exists() or (staging / "verified.json").is_symlink():
        raise ArtifactError("artifact_marker_conflict")
    _semantic_check(staging, identity)
    tree_sha = _tree_digest(staging)
    marker = staging / "verified.json"
    marker.write_text(json.dumps({"schema_version": 1, "environment_key": identity.key,
                                  "tree_sha256": tree_sha}, sort_keys=True), encoding="utf-8")
    for path in sorted(staging.rglob("*"), reverse=True):
        if path.is_symlink():
            continue
        path.chmod(0o555 if path.is_dir() else 0o444)
    staging.chmod(0o555)
    os.replace(staging, destination)
    return destination


def verified_artifact(root: Path, identity: EnvironmentIdentity) -> Path | None:
    """A marker alone never establishes readiness: verify the tree and its key."""
    root = trusted_directory(root)
    destination = root / _key(identity)
    marker = destination / "verified.json"
    if destination.is_symlink() or not destination.is_dir() or marker.is_symlink() or not marker.is_file():
        return None
    try:
        if marker.stat().st_size > 1024:
            return None
        payload = json.loads(marker.read_text(encoding="utf-8"))
        if payload.get("schema_version") != 1 or payload.get("environment_key") != identity.key:
            return None
        _semantic_check(destination, identity)
        if payload.get("tree_sha256") != _tree_digest(destination):
            return None
    except (OSError, ValueError, ArtifactError):
        return None
    return destination
