from pathlib import Path
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor
import time

import pytest

from app.verification.preparation import PreparationError, prepare_node_artifact
from test_verification_environment import identity, project


def test_preparation_runs_only_fixed_install_in_isolated_container(tmp_path, monkeypatch):
    source = project(tmp_path)
    item = identity(source)
    root = tmp_path / "artifacts"
    root.mkdir()
    monkeypatch.setattr("app.verification.preparation.shutil.which", lambda _: "/usr/bin/docker")
    commands = []

    def run(command, **kwargs):
        commands.append(command)
        mount = command[command.index("--mount") + 1]
        staging = Path(mount.removeprefix("type=bind,src=").removesuffix(",dst=/work"))
        (staging / "node_modules" / "@playwright" / "test").mkdir(parents=True)
        (staging / "node_modules" / "@playwright" / "test" / "package.json").write_text('{"version":"1.62.1"}')
        (staging / "node_modules" / "index.js").write_text("safe")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr("app.verification.preparation.subprocess.run", run)
    first = prepare_node_artifact(source, root, item, registry_url="https://registry.example.invalid/", network="fetch-only")
    assert first.is_dir()
    assert prepare_node_artifact(source, root, item, registry_url="https://registry.example.invalid/", network="fetch-only") == first
    assert len(commands) == 1
    assert commands[0][-6:] == ["pnpm", "install", "--frozen-lockfile", "--ignore-scripts", "--package-import-method=copy", "--store-dir=/work/.pnpm-store"]
    assert "--read-only" in commands[0]
    assert "--cap-drop" in commands[0]


def test_preparation_rejects_external_tarball_before_docker(tmp_path):
    source = project(tmp_path)
    item = identity(source)
    (source / "pnpm-lock.yaml").write_text((source / "pnpm-lock.yaml").read_text() + "\n  tarball: https://evil.invalid/x.tgz\n")
    root = tmp_path / "artifacts"
    root.mkdir()
    with pytest.raises(PreparationError, match="lockfile_external_source"):
        prepare_node_artifact(source, root, item, registry_url="https://registry.example.invalid/", network="fetch-only")


def test_preparation_blocks_when_artifact_disk_capacity_is_low(tmp_path, monkeypatch):
    source = project(tmp_path)
    item = identity(source)
    root = tmp_path / "artifacts"
    root.mkdir()
    monkeypatch.setattr("app.verification.preparation.shutil.disk_usage",
                        lambda _: SimpleNamespace(free=100 * 1024 * 1024))
    with pytest.raises(PreparationError, match="artifact_capacity_insufficient"):
        prepare_node_artifact(source, root, item, registry_url="https://registry.example.invalid/", network="fetch-only")


def test_parallel_preparation_publishes_one_shared_artifact(tmp_path, monkeypatch):
    source = project(tmp_path)
    item = identity(source)
    root = tmp_path / "artifacts"
    root.mkdir()
    monkeypatch.setattr("app.verification.preparation.shutil.which", lambda _: "/usr/bin/docker")
    commands = []

    def run(command, **kwargs):
        commands.append(command)
        time.sleep(0.05)
        mount = command[command.index("--mount") + 1]
        staging = Path(mount.removeprefix("type=bind,src=").removesuffix(",dst=/work"))
        package = staging / "node_modules" / "@playwright" / "test" / "package.json"
        package.parent.mkdir(parents=True)
        package.write_text('{"version":"1.62.1"}')
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr("app.verification.preparation.subprocess.run", run)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(prepare_node_artifact, source, root, item,
            registry_url="https://registry.example.invalid/", network="fetch-only") for _ in range(2)]
        locations = [future.result() for future in futures]
    assert locations[0] == locations[1]
    assert len(commands) == 1
