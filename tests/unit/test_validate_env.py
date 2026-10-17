from __future__ import annotations

import subprocess
from pathlib import Path


BASE_ENV = """\
MOONBOX_DEPLOY_ENV_ID=local-self-storage-sqlite
APP_ENV=local
APP_DEBUG=true
TZ=Asia/Shanghai
DATABASE_TIMEZONE=+08:00
HOST_PORT_BACKEND=39001
HOST_PORT_WEB=39002
HOST_PORT_MINIO_API=39003
HOST_PORT_MINIO_CONSOLE=39004
HOST_PORT_MINTLIFY_DOCS=39005
VITE_API_BASE_URL=http://localhost:39001
DATABASE_TYPE=sqlite
DATABASE_DEPLOYMENT_MODE=sqlite
DATABASE_URL=sqlite:////app/data/sqlite/moonbox.db
OBJECT_STORAGE_DEPLOYMENT_MODE=self-hosted-minio
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=change-me
MINIO_SECRET_KEY=change-me
MINIO_BUCKET=moonbox
"""


def _validate(tmp_path: Path, content: str) -> subprocess.CompletedProcess[str]:
    env_file = tmp_path / "local.env"
    env_file.write_text(content)
    return subprocess.run(
        [
            "python",
            "deploy/scripts/validate-env.py",
            "--domain",
            "local",
            "--environment",
            "self-storage-sqlite",
            "--env-file",
            str(env_file),
            "--profile",
            "self-hosted-storage",
        ],
        cwd=Path(__file__).resolve().parents[2],
        text=True,
        capture_output=True,
        check=False,
    )


def test_validate_env_accepts_moonbox_local_defaults(tmp_path: Path) -> None:
    result = _validate(tmp_path, BASE_ENV)

    assert result.returncode == 0, result.stdout + result.stderr


def test_validate_env_rejects_local_port_outside_moonbox_range(tmp_path: Path) -> None:
    result = _validate(tmp_path, BASE_ENV.replace("HOST_PORT_WEB=39002", "HOST_PORT_WEB=5173"))

    assert result.returncode == 1
    assert "HOST_PORT_WEB 必须位于 39001-39050" in result.stdout


def test_validate_env_rejects_port_above_new_upper_bound(tmp_path: Path) -> None:
    result = _validate(tmp_path, BASE_ENV.replace("HOST_PORT_WEB=39002", "HOST_PORT_WEB=39051"))

    assert result.returncode == 1
    assert "HOST_PORT_WEB 必须位于 39001-39050" in result.stdout


def test_validate_env_rejects_non_beijing_timezone(tmp_path: Path) -> None:
    result = _validate(tmp_path, BASE_ENV.replace("DATABASE_TIMEZONE=+08:00", "DATABASE_TIMEZONE=+00:00"))

    assert result.returncode == 1
    assert "DATABASE_TIMEZONE 默认必须是 +08:00" in result.stdout
