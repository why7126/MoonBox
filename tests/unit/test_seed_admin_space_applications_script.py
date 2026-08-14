from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_script_module():
    script = Path(__file__).resolve().parents[2] / "scripts" / "seed-admin-space-applications.py"
    spec = importlib.util.spec_from_file_location("seed_admin_space_applications", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_seed_script_maps_docker_sqlite_url_to_host_runtime_path(tmp_path, monkeypatch) -> None:
    module = _load_script_module()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SQLITE_DATABASE_URL", raising=False)
    (tmp_path / ".env").write_text("DATABASE_URL=sqlite:////app/data/sqlite/moonbox.db\n", encoding="utf-8")

    resolved = module.resolve_seed_database_url()

    expected_path = tmp_path / "data" / "runtime" / "backend" / "sqlite" / "moonbox.db"
    assert resolved == f"sqlite:///{expected_path.resolve()}"
    assert resolved == module.os.environ["DATABASE_URL"]
    assert resolved == module.os.environ["SQLITE_DATABASE_URL"]


def test_seed_script_keeps_explicit_host_sqlite_url(tmp_path, monkeypatch) -> None:
    module = _load_script_module()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    explicit_path = tmp_path / "custom.db"
    explicit_url = f"sqlite:///{explicit_path}"
    monkeypatch.setenv("DATABASE_URL", explicit_url)
    monkeypatch.setenv("SQLITE_DATABASE_URL", explicit_url)
    (tmp_path / ".env").write_text("DATABASE_URL=sqlite:////app/data/sqlite/moonbox.db\n", encoding="utf-8")

    resolved = module.resolve_seed_database_url()

    assert resolved == explicit_url


def test_seed_script_auto_detects_runtime_sqlite_without_env_file(tmp_path, monkeypatch) -> None:
    module = _load_script_module()
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SQLITE_DATABASE_URL", raising=False)
    runtime_sqlite = tmp_path / "data" / "runtime" / "backend" / "sqlite" / "moonbox.db"
    runtime_sqlite.parent.mkdir(parents=True)
    runtime_sqlite.write_text("", encoding="utf-8")

    resolved = module.resolve_seed_database_url()

    assert resolved == f"sqlite:///{runtime_sqlite.resolve()}"
