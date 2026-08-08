from __future__ import annotations

import os

import pytest
from sqlalchemy import text

from app.core.config import settings
from app.db.session import get_engine, init_database, reset_engine


def test_sqlite_initialization_creates_schema_metadata(tmp_path) -> None:
    settings.app_env = "test"
    settings.database_type = "sqlite"
    settings.database_url = None
    settings.sqlite_database_url = f"sqlite:///{tmp_path / 'moonbox.db'}"

    reset_engine()
    init_database()

    with get_engine().connect() as connection:
        row = connection.execute(text("SELECT schema_version FROM schema_metadata WHERE id = 1")).one()

    assert row[0] == "0000-initialize-project"
    reset_engine()


@pytest.mark.skipif(os.getenv("RUN_MYSQL_TESTS") != "1", reason="MySQL compatibility test requires RUN_MYSQL_TESTS=1")
def test_mysql_initialization_creates_schema_metadata() -> None:
    mysql_url = os.getenv("MYSQL_DATABASE_URL")
    if not mysql_url:
        pytest.skip("MYSQL_DATABASE_URL is required for MySQL compatibility test")

    settings.app_env = "test"
    settings.database_type = "mysql"
    settings.database_url = mysql_url

    reset_engine()
    init_database()

    with get_engine().connect() as connection:
        row = connection.execute(text("SELECT schema_version FROM schema_metadata WHERE id = 1")).one()

    assert row[0] == "0000-initialize-project"
    reset_engine()
