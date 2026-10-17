from pathlib import Path

import pytest

from app.verification.artifacts import ArtifactError, publish_artifact, verified_artifact
from test_verification_environment import identity, project


def test_publish_reuses_exact_immutable_tree_and_detects_tamper(tmp_path):
    item = identity(project(tmp_path))
    root = tmp_path / "cache"
    root.mkdir()
    stage = root / "preparing-one"
    stage.mkdir()
    (stage / "node_modules" / "@playwright" / "test").mkdir(parents=True)
    (stage / "node_modules" / "@playwright" / "test" / "package.json").write_text('{"version":"1.62.1"}')
    (stage / "node_modules" / "file.js").write_text("module.exports = 1")
    location = publish_artifact(stage, root, item)
    assert verified_artifact(root, item) == location
    (location / "node_modules" / "file.js").chmod(0o644)
    (location / "node_modules" / "file.js").write_text("module.exports = 2")
    assert verified_artifact(root, item) is None


def test_publish_rejects_external_symlink(tmp_path):
    item = identity(project(tmp_path))
    root = tmp_path / "cache"
    root.mkdir()
    stage = root / "preparing-two"
    stage.mkdir()
    (stage / "node_modules" / "@playwright" / "test").mkdir(parents=True)
    (stage / "node_modules" / "@playwright" / "test" / "package.json").write_text('{"version":"1.62.1"}')
    (stage / "escape").symlink_to(tmp_path)
    with pytest.raises(ArtifactError, match="artifact_symlink_escape"):
        publish_artifact(stage, root, item)
