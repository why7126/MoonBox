from __future__ import annotations

import os
from dataclasses import dataclass

from sqlalchemy.engine import make_url

SUPPORTED_DATABASE_TYPES = {"sqlite", "mysql"}
PRODUCTION_ENVS = {"production", "prod"}
MYSQL_SCHEMES = {"mysql", "mysql+pymysql", "mysql+mysqlconnector", "mysql+aiomysql"}


class ConfigurationError(RuntimeError):
    """Raised when runtime configuration violates an environment boundary."""


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def sanitize_database_url(database_url: str) -> str:
    url = make_url(database_url)
    return url.render_as_string(hide_password=True)


@dataclass
class Settings:
    app_env: str = "development"
    app_secret_key: str = "change-me-in-local-env"
    backend_cors_origins: str = "http://localhost:18102,http://127.0.0.1:18102"
    jwt_access_token_expire_minutes: int = 120
    jwt_remember_me_expire_days: int = 7
    admin_username: str = "admin"
    admin_initial_password: str = "change-me-on-first-run"
    database_type: str = "sqlite"
    database_url: str | None = None
    sqlite_database_url: str = "sqlite:///./data/sqlite/moonbox.db"
    mysql_database_url: str | None = None
    mysql_charset: str = "utf8mb4"
    mysql_collation: str = "utf8mb4_0900_ai_ci"
    database_timezone: str = "+00:00"
    object_storage_endpoint: str = "localhost:9000"
    object_storage_access_key: str = "change-me"
    object_storage_secret_key: str = "change-me"
    object_storage_bucket: str = "moonbox"
    object_storage_secure: bool = False
    object_storage_avatar_prefix: str = "images/avatars/"

    @classmethod
    def from_env(cls) -> "Settings":
        app_env = _clean(os.getenv("APP_ENV")) or "development"
        explicit_database_type = _clean(os.getenv("DATABASE_TYPE"))
        sqlite_url = _clean(os.getenv("SQLITE_DATABASE_URL")) or "sqlite:///./data/sqlite/moonbox.db"
        database_url = _clean(os.getenv("DATABASE_URL"))
        mysql_url = _clean(os.getenv("MYSQL_DATABASE_URL"))

        if explicit_database_type:
            database_type = explicit_database_type.lower()
        elif app_env.lower() in PRODUCTION_ENVS:
            database_type = ""
        else:
            database_type = "sqlite"

        return cls(
            app_env=app_env,
            app_secret_key=_clean(os.getenv("APP_SECRET_KEY")) or "change-me-in-local-env",
            backend_cors_origins=_clean(os.getenv("BACKEND_CORS_ORIGINS"))
            or "http://localhost:18102,http://127.0.0.1:18102",
            jwt_access_token_expire_minutes=int(_clean(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")) or "120"),
            jwt_remember_me_expire_days=int(_clean(os.getenv("JWT_REMEMBER_ME_EXPIRE_DAYS")) or "7"),
            admin_username=_clean(os.getenv("ADMIN_USERNAME")) or "admin",
            admin_initial_password=_clean(os.getenv("ADMIN_INITIAL_PASSWORD")) or "change-me-on-first-run",
            database_type=database_type,
            database_url=database_url,
            sqlite_database_url=sqlite_url,
            mysql_database_url=mysql_url,
            mysql_charset=_clean(os.getenv("MYSQL_CHARSET")) or "utf8mb4",
            mysql_collation=_clean(os.getenv("MYSQL_COLLATION")) or "utf8mb4_0900_ai_ci",
            database_timezone=_clean(os.getenv("DATABASE_TIMEZONE")) or "+00:00",
            object_storage_endpoint=_clean(os.getenv("OBJECT_STORAGE_ENDPOINT"))
            or _clean(os.getenv("MINIO_ENDPOINT"))
            or "localhost:9000",
            object_storage_access_key=_clean(os.getenv("MINIO_ACCESS_KEY")) or "change-me",
            object_storage_secret_key=_clean(os.getenv("MINIO_SECRET_KEY")) or "change-me",
            object_storage_bucket=_clean(os.getenv("MINIO_BUCKET")) or "moonbox",
            object_storage_secure=(_clean(os.getenv("MINIO_SECURE")) or "false").lower() in {"1", "true", "yes"},
            object_storage_avatar_prefix=_clean(os.getenv("OBJECT_STORAGE_PREFIX_IMAGES_AVATARS")) or "images/avatars/",
        )

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() in PRODUCTION_ENVS

    def resolved_database_url(self) -> str:
        db_type = self.database_type.lower()
        if db_type == "sqlite":
            return self.database_url or self.sqlite_database_url
        if db_type == "mysql":
            return self.database_url or self.mysql_database_url or ""
        return self.database_url or ""

    def validate_database(self) -> None:
        db_type = self.database_type.lower()
        if db_type not in SUPPORTED_DATABASE_TYPES:
            if self.is_production and not db_type:
                raise ConfigurationError("生产环境必须显式配置 DATABASE_TYPE=mysql。")
            raise ConfigurationError(f"不支持的 DATABASE_TYPE：{self.database_type!r}。")

        database_url = self.resolved_database_url()
        if not database_url:
            raise ConfigurationError(f"缺少 {db_type} 数据库连接串。")

        try:
            url = make_url(database_url)
        except Exception as exc:
            raise ConfigurationError("数据库连接串格式无效。") from exc

        if db_type == "sqlite" and not url.drivername.startswith("sqlite"):
            raise ConfigurationError("DATABASE_TYPE=sqlite 时连接串必须使用 sqlite scheme。")

        if db_type == "mysql" and url.drivername not in MYSQL_SCHEMES:
            raise ConfigurationError("DATABASE_TYPE=mysql 时连接串必须使用 MySQL scheme。")

        if self.is_production:
            if db_type != "mysql":
                raise ConfigurationError("生产环境禁止使用 SQLite，必须配置 DATABASE_TYPE=mysql。")
            if url.drivername not in MYSQL_SCHEMES:
                raise ConfigurationError("生产环境 DATABASE_URL 必须指向 MySQL。")
            if not url.username or not url.host or not url.database:
                raise ConfigurationError("生产 MySQL 连接串必须包含用户名、主机和数据库名。")

    def validate_admin_initial_password(self) -> None:
        password = self.admin_initial_password
        weak_values = {
            "",
            "admin",
            "password",
            "change-me",
            "change-me-on-first-run",
            "example-test-password",
        }
        if self.is_production and (password.strip().lower() in weak_values or len(password) < 12):
            raise ConfigurationError("生产环境禁止使用空密码、示例密码或弱密码初始化超级管理员。")

    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


settings = Settings.from_env()
