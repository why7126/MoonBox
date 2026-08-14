#!/usr/bin/env python3
"""Seed demo admin space applications for local approval acceptance."""

from __future__ import annotations

import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "src" / "backend"
sys.path.insert(0, str(BACKEND_ROOT))


def _parse_dotenv_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None
    key, value = stripped.split("=", 1)
    key = key.strip()
    value = value.strip().strip("'\"")
    if not key:
        return None
    return key, value


def load_dotenv_if_present(path: Path | None = None) -> None:
    path = path or ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        parsed = _parse_dotenv_line(line)
        if parsed is None:
            continue
        key, value = parsed
        os.environ.setdefault(key, value)


def _sqlite_url_for_path(path: Path) -> str:
    return f"sqlite:///{path.resolve()}"


def _map_container_sqlite_url(database_url: str) -> str | None:
    container_prefix = "sqlite:////app/data/"
    if not database_url.startswith(container_prefix):
        return None
    relative = database_url.removeprefix(container_prefix)
    host_path = ROOT / "data" / "runtime" / "backend" / relative
    return _sqlite_url_for_path(host_path)


def resolve_seed_database_url() -> str:
    load_dotenv_if_present()
    for key in ("DATABASE_URL", "SQLITE_DATABASE_URL"):
        value = os.environ.get(key)
        if not value:
            continue
        mapped = _map_container_sqlite_url(value)
        if mapped:
            os.environ["DATABASE_URL"] = mapped
            os.environ["SQLITE_DATABASE_URL"] = mapped
            return mapped
        if value.startswith("sqlite"):
            return value

    runtime_sqlite = ROOT / "data" / "runtime" / "backend" / "sqlite" / "moonbox.db"
    if runtime_sqlite.exists():
        database_url = _sqlite_url_for_path(runtime_sqlite)
        os.environ["DATABASE_URL"] = database_url
        os.environ["SQLITE_DATABASE_URL"] = database_url
        return database_url

    return os.environ.get("SQLITE_DATABASE_URL") or "sqlite:///./data/sqlite/moonbox.db"


def main() -> int:
    database_url = resolve_seed_database_url()

    from app.core.config import sanitize_database_url, settings  # noqa: PLC0415
    from app.db.seed import seed_admin_user, seed_demo_space_applications  # noqa: PLC0415
    from app.db.session import get_session_factory, init_database  # noqa: PLC0415

    if settings.is_production:
        print("Production environment refuses demo space application seed.")
        return 1

    init_database()
    session = get_session_factory()()
    try:
        seed_admin_user(session)
        created_count = seed_demo_space_applications(session, force=True)
    finally:
        session.close()

    print(f"Target database: {sanitize_database_url(database_url)}")
    print(f"Seeded {created_count} pending demo space application(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
