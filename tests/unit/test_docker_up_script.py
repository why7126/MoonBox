from __future__ import annotations

import os
import subprocess
from pathlib import Path


def _fake_docker(tmp_path: Path) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    docker = bin_dir / "docker"
    docker.write_text(
        "#!/usr/bin/env bash\n"
        "echo \"$*\" >> \"$DOCKER_UP_CAPTURE\"\n"
        "echo \"VITE_API_BASE_URL=${VITE_API_BASE_URL-}\" >> \"$DOCKER_UP_CAPTURE\"\n"
    )
    docker.chmod(0o755)
    return bin_dir


def _run_script(tmp_path: Path, env_file_content: str, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env_file = tmp_path / ".env"
    env_file.write_text(env_file_content)
    capture = tmp_path / "capture.txt"
    env = os.environ.copy()
    env.update(
        {
            "ENV_FILE": str(env_file),
            "DOCKER_UP_CAPTURE": str(capture),
            "PATH": f"{_fake_docker(tmp_path)}:{env['PATH']}",
        }
    )
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", "scripts/docker-up.sh", "self-storage-sqlite"],
        cwd=Path(__file__).resolve().parents[2],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_docker_up_does_not_require_vite_api_base_url(tmp_path: Path) -> None:
    result = _run_script(tmp_path, "HOST_PORT_BACKEND=18101\n")

    assert result.returncode == 0, result.stderr
    capture = (tmp_path / "capture.txt").read_text()
    assert "compose up -d --build backend web minio" in capture
    assert "VITE_API_BASE_URL=" in capture


def test_docker_up_ignores_runtime_vite_api_base_url_for_docker_web(tmp_path: Path) -> None:
    result = _run_script(tmp_path, "HOST_PORT_BACKEND=18101\nVITE_API_BASE_URL=http://localhost:8000\n")

    assert result.returncode == 0, result.stderr
    capture = (tmp_path / "capture.txt").read_text()
    assert "compose up -d --build backend web minio" in capture
    assert "VITE_API_BASE_URL=" in capture
