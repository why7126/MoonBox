from __future__ import annotations

import pytest

from app.core.config import ConfigurationError, Settings, sanitize_database_url


def test_development_defaults_to_sqlite_without_mysql() -> None:
    settings = Settings(app_env="development", database_type="sqlite", sqlite_database_url="sqlite:///./data/test.db")

    settings.validate_database()

    assert settings.resolved_database_url() == "sqlite:///./data/test.db"


def test_production_requires_explicit_mysql_type() -> None:
    settings = Settings(app_env="production", database_type="", database_url="mysql+pymysql://user:pass@db/moonbox")

    with pytest.raises(ConfigurationError, match="DATABASE_TYPE=mysql"):
        settings.validate_database()


def test_production_rejects_sqlite_database() -> None:
    settings = Settings(app_env="production", database_type="sqlite", database_url="sqlite:///./prod.db")

    with pytest.raises(ConfigurationError, match="生产环境禁止使用 SQLite"):
        settings.validate_database()


def test_mysql_configuration_is_valid_without_exposing_password() -> None:
    settings = Settings(
        app_env="production",
        database_type="mysql",
        database_url="mysql+pymysql://moonbox:secret@mysql:3306/moonbox",
    )

    settings.validate_database()

    sanitized = sanitize_database_url(settings.resolved_database_url())
    assert "secret" not in sanitized
    assert "***" in sanitized
