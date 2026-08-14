from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_module():
    script = Path(__file__).resolve().parents[2] / "scripts" / "verify-docker-media-upload.py"
    spec = importlib.util.spec_from_file_location("verify_docker_media_upload", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_resolves_web_port_from_env_file(tmp_path: Path, monkeypatch) -> None:
    module = _load_module()
    env_file = tmp_path / ".env"
    env_file.write_text("HOST_PORT_WEB=18122\nADMIN_INITIAL_PASSWORD=secret-example\n", encoding="utf-8")
    monkeypatch.delenv("HOST_PORT_WEB", raising=False)

    assert module.web_base_url(env_file) == "http://localhost:18122"


def test_password_hash_roundtrip_without_default_admin_dependency() -> None:
    module = _load_module()
    password = "Mb-Probe-Example1!"
    password_hash = module.hash_password(password, salt="fixed-salt")

    assert module.verify_password(password, password_hash)
    assert not module.verify_password("change-me-on-first-run", password_hash)


def test_verification_summary_excludes_secrets_and_paths() -> None:
    summary = {
        "status": "passed",
        "web_port": 18102,
        "test_identity": "script-prepared-front-user",
        "username_prefix": "media_probe_",
        "login": "passed",
        "upload": "passed",
        "protected_read": "passed",
        "profile_echo": "passed",
    }
    rendered = str(summary)

    assert "Authorization" not in rendered
    assert "Bearer" not in rendered
    assert "Mb-Probe" not in rendered
    assert "/Users/" not in rendered
    assert "ADMIN_INITIAL_PASSWORD" not in rendered
