import json
from pathlib import Path

import pytest

from app.verification.environment import EnvironmentError, inspect_environment, preflight


def project(tmp_path: Path, *, version="1.62.1", lock_version="1.62.1") -> Path:
    (tmp_path / "package.json").write_text(json.dumps({
        "packageManager": "pnpm@11.2.2", "devDependencies": {"@playwright/test": f"^{version}"}
    }))
    (tmp_path / "pnpm-lock.yaml").write_text(
        f"lockfileVersion: '9.0'\nimporters:\n  .:\n    devDependencies:\n      '@playwright/test':\n        specifier: ^{version}\n        version: {lock_version}\n"
    )
    return tmp_path


def identity(path, **overrides):
    args = dict(node_version="22.15.0", os_name="linux", architecture="arm64", image_digest="sha256:" + "a" * 64)
    args.update(overrides)
    return inspect_environment(path, **args)


def test_identity_changes_with_lock_architecture_and_image(tmp_path):
    path = project(tmp_path)
    first = identity(path)
    assert first.playwright_version == "1.62.1"
    assert first.key != identity(path, architecture="amd64").key
    assert first.key != identity(path, os_name="darwin").key
    assert first.key != identity(path, node_version="24.18.1").key
    assert first.key != identity(path, image_digest="sha256:" + "b" * 64).key
    (path / "pnpm-lock.yaml").write_text((path / "pnpm-lock.yaml").read_text() + "\n# new resolution\n")
    assert first.key != identity(path).key
    project(path, version="1.62.2", lock_version="1.62.2")
    assert first.key != identity(path).key


def test_conflicting_or_unsafe_declaration_rejected(tmp_path):
    path = project(tmp_path, lock_version="1.61.0")
    with pytest.raises(EnvironmentError, match="playwright_lockfile_mismatch"):
        identity(path)
    project(path)
    with pytest.raises(EnvironmentError, match="runner_image_unpinned"):
        identity(path, image_digest="latest")
    (path / "package-lock.json").write_text("{}")
    with pytest.raises(EnvironmentError, match="multiple_lockfiles"):
        identity(path)


def test_preflight_distinguishes_preparation_environment_and_ready(tmp_path):
    item = identity(project(tmp_path))
    browsers = {"firefox": True, "chromium": True, "system_libraries": True}
    args = dict(artifact_exists=False, browser_probe=browsers, target_reachable=True, artifact_source_available=True)
    assert preflight(item, **args)["status"] == "preparable"
    assert preflight(item, **{**args, "artifact_source_available": False})["reason_code"] == "artifact_source_unavailable"
    assert preflight(item, **{**args, "browser_probe": {**browsers, "firefox": False}})["status"] == "unavailable"
    assert preflight(item, **{**args, "artifact_exists": True})["status"] == "ready"
