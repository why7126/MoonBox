from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import make_url
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import ConfigurationError, Settings, settings

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def _sqlite_connect_args(database_url: str) -> dict[str, bool]:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def _ensure_sqlite_parent_dir(database_url: str) -> None:
    if not database_url.startswith("sqlite"):
        return
    database_path = make_url(database_url).database
    if not database_path or database_path == ":memory:":
        return
    Path(database_path).expanduser().parent.mkdir(parents=True, exist_ok=True)


def create_database_engine(config: Settings = settings) -> Engine:
    config.validate_database()
    database_url = config.resolved_database_url()
    _ensure_sqlite_parent_dir(database_url)
    engine = create_engine(
        database_url,
        connect_args=_sqlite_connect_args(database_url),
        pool_pre_ping=True,
        future=True,
    )

    if config.database_type.lower() == "sqlite":

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:  # type: ignore[no-untyped-def]
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_database_engine(settings)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, future=True)
    return _session_factory


def reset_engine() -> None:
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None


def get_db() -> Generator[Session, None, None]:
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()


def init_database() -> None:
    engine = get_engine()
    dialect = engine.dialect.name
    if dialect == "sqlite":
        statements = [
            """
            CREATE TABLE IF NOT EXISTS schema_metadata (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                schema_version TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """,
            "INSERT OR IGNORE INTO schema_metadata (id, schema_version) VALUES (1, '0000-initialize-project')",
            """
            CREATE TABLE IF NOT EXISTS admin_users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                nickname TEXT,
                avatar_url TEXT,
                role TEXT NOT NULL CHECK (role IN ('后台管理员', '前台用户')),
                status TEXT NOT NULL CHECK (status IN ('待激活', '正常', '已冻结', '已删除')),
                status_before_freeze TEXT CHECK (status_before_freeze IN ('待激活', '正常') OR status_before_freeze IS NULL),
                workspace_count INTEGER NOT NULL DEFAULT 0,
                last_login_at TEXT,
                password_hash TEXT,
                is_system_superadmin INTEGER NOT NULL DEFAULT 0,
                deleted_at TEXT,
                session_invalidated_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """,
            "CREATE INDEX IF NOT EXISTS ix_admin_users_role ON admin_users (role)",
            "CREATE INDEX IF NOT EXISTS ix_admin_users_status ON admin_users (status)",
            "ALTER TABLE admin_users ADD COLUMN password_hash TEXT",
            "ALTER TABLE admin_users ADD COLUMN status_before_freeze TEXT CHECK (status_before_freeze IN ('待激活', '正常') OR status_before_freeze IS NULL)",
            """
            CREATE TABLE IF NOT EXISTS admin_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                expires_at TEXT NOT NULL,
                revoked_at TEXT,
                last_used_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES admin_users(id)
            )
            """,
            "CREATE INDEX IF NOT EXISTS ix_admin_sessions_user_id ON admin_sessions (user_id)",
            "CREATE INDEX IF NOT EXISTS ix_admin_sessions_token_hash ON admin_sessions (token_hash)",
            """
            CREATE TABLE IF NOT EXISTS admin_audit_events (
                id TEXT PRIMARY KEY,
                actor TEXT NOT NULL,
                target_id TEXT NOT NULL,
                action TEXT NOT NULL,
                before_value TEXT,
                after_value TEXT,
                reason TEXT NOT NULL,
                result TEXT NOT NULL,
                request_id TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS admin_spaces (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                code TEXT NOT NULL UNIQUE,
                description TEXT,
                owner_id TEXT NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'FROZEN', 'RECYCLE')),
                source TEXT NOT NULL CHECK (source IN ('后台创建', '申请审批')),
                member_count INTEGER NOT NULL DEFAULT 0,
                member_quota INTEGER NOT NULL,
                storage_used_gb REAL NOT NULL DEFAULT 0,
                storage_quota_gb REAL NOT NULL,
                ai_used_tokens INTEGER NOT NULL DEFAULT 0,
                ai_quota_tokens INTEGER NOT NULL,
                expiry_type TEXT NOT NULL CHECK (expiry_type IN ('fixed_date', 'long_term')),
                expires_at TEXT,
                protected INTEGER NOT NULL DEFAULT 0,
                freeze_reason TEXT,
                deleted_at TEXT,
                deleted_by TEXT,
                delete_reason TEXT,
                purge_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (owner_id) REFERENCES admin_users(id)
            )
            """,
            "CREATE INDEX IF NOT EXISTS ix_admin_spaces_status ON admin_spaces (status)",
            "CREATE INDEX IF NOT EXISTS ix_admin_spaces_owner ON admin_spaces (owner_id)",
            """
            CREATE TABLE IF NOT EXISTS admin_space_products (
                id TEXT PRIMARY KEY,
                space_id TEXT NOT NULL UNIQUE,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                immutable_binding INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (space_id) REFERENCES admin_spaces(id) ON DELETE CASCADE
            )
            """,
            "CREATE INDEX IF NOT EXISTS ix_admin_space_products_product ON admin_space_products (product_id)",
            """
            CREATE TABLE IF NOT EXISTS admin_space_members (
                id TEXT PRIMARY KEY,
                space_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE (space_id, user_id),
                FOREIGN KEY (space_id) REFERENCES admin_spaces(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES admin_users(id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS admin_space_applications (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                code TEXT NOT NULL,
                applicant_id TEXT NOT NULL,
                proposed_owner_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                purpose TEXT NOT NULL,
                expected_members INTEGER NOT NULL,
                requested_storage_gb REAL NOT NULL,
                requested_ai_tokens INTEGER NOT NULL,
                expires_at TEXT,
                status TEXT NOT NULL CHECK (status IN ('待审批', '已通过', '已拒绝')),
                decision_reason TEXT,
                decision_by TEXT,
                decision_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (applicant_id) REFERENCES admin_users(id),
                FOREIGN KEY (proposed_owner_id) REFERENCES admin_users(id)
            )
            """,
            "CREATE INDEX IF NOT EXISTS ix_admin_space_applications_status ON admin_space_applications (status)",
            """
            CREATE TABLE IF NOT EXISTS admin_space_audit_events (
                id TEXT PRIMARY KEY,
                space_id TEXT NOT NULL,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                before_value TEXT,
                after_value TEXT,
                reason TEXT NOT NULL,
                result TEXT NOT NULL,
                request_id TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """,
            "CREATE INDEX IF NOT EXISTS ix_admin_space_audit_space ON admin_space_audit_events (space_id)",
        ]
    elif dialect == "mysql":
        statements = [
            """
            CREATE TABLE IF NOT EXISTS schema_metadata (
                id INTEGER PRIMARY KEY,
                schema_version VARCHAR(64) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                CONSTRAINT ck_schema_metadata_singleton CHECK (id = 1)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """,
            "INSERT IGNORE INTO schema_metadata (id, schema_version) VALUES (1, '0000-initialize-project')",
            """
            CREATE TABLE IF NOT EXISTS admin_users (
                id VARCHAR(64) PRIMARY KEY,
                username VARCHAR(32) NOT NULL UNIQUE,
                nickname VARCHAR(128),
                avatar_url VARCHAR(512),
                role VARCHAR(32) NOT NULL,
                status VARCHAR(32) NOT NULL,
                status_before_freeze VARCHAR(32) NULL,
                workspace_count INTEGER NOT NULL DEFAULT 0,
                last_login_at DATETIME NULL,
                password_hash VARCHAR(255),
                is_system_superadmin BOOLEAN NOT NULL DEFAULT FALSE,
                deleted_at DATETIME NULL,
                session_invalidated_at DATETIME NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                CONSTRAINT ck_admin_users_role CHECK (role IN ('后台管理员', '前台用户')),
                CONSTRAINT ck_admin_users_status CHECK (status IN ('待激活', '正常', '已冻结', '已删除')),
                CONSTRAINT ck_admin_users_status_before_freeze CHECK (status_before_freeze IN ('待激活', '正常') OR status_before_freeze IS NULL)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """,
            "CREATE INDEX ix_admin_users_role ON admin_users (role)",
            "CREATE INDEX ix_admin_users_status ON admin_users (status)",
            "ALTER TABLE admin_users ADD COLUMN password_hash VARCHAR(255)",
            "ALTER TABLE admin_users ADD COLUMN status_before_freeze VARCHAR(32) NULL",
            """
            CREATE TABLE IF NOT EXISTS admin_sessions (
                id VARCHAR(64) PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                token_hash VARCHAR(128) NOT NULL UNIQUE,
                expires_at DATETIME NOT NULL,
                revoked_at DATETIME NULL,
                last_used_at DATETIME NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                CONSTRAINT fk_admin_sessions_user FOREIGN KEY (user_id) REFERENCES admin_users(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """,
            "CREATE INDEX ix_admin_sessions_user_id ON admin_sessions (user_id)",
            "CREATE INDEX ix_admin_sessions_token_hash ON admin_sessions (token_hash)",
            """
            CREATE TABLE IF NOT EXISTS admin_audit_events (
                id VARCHAR(64) PRIMARY KEY,
                actor VARCHAR(64) NOT NULL,
                target_id VARCHAR(64) NOT NULL,
                action VARCHAR(64) NOT NULL,
                before_value TEXT,
                after_value TEXT,
                reason VARCHAR(512) NOT NULL,
                result VARCHAR(32) NOT NULL,
                request_id VARCHAR(64) NOT NULL,
                created_at DATETIME NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """,
            """
            CREATE TABLE IF NOT EXISTS admin_spaces (
                id VARCHAR(64) PRIMARY KEY,
                name VARCHAR(80) NOT NULL,
                code VARCHAR(48) NOT NULL UNIQUE,
                description VARCHAR(512),
                owner_id VARCHAR(64) NOT NULL,
                status VARCHAR(16) NOT NULL,
                source VARCHAR(32) NOT NULL,
                member_count INTEGER NOT NULL DEFAULT 0,
                member_quota INTEGER NOT NULL,
                storage_used_gb DECIMAL(12,2) NOT NULL DEFAULT 0,
                storage_quota_gb DECIMAL(12,2) NOT NULL,
                ai_used_tokens BIGINT NOT NULL DEFAULT 0,
                ai_quota_tokens BIGINT NOT NULL,
                expiry_type VARCHAR(16) NOT NULL,
                expires_at DATETIME NULL,
                protected BOOLEAN NOT NULL DEFAULT FALSE,
                freeze_reason VARCHAR(512),
                deleted_at DATETIME NULL,
                deleted_by VARCHAR(64),
                delete_reason VARCHAR(512),
                purge_at DATETIME NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                CONSTRAINT fk_admin_spaces_owner FOREIGN KEY (owner_id) REFERENCES admin_users(id),
                CONSTRAINT ck_admin_spaces_status CHECK (status IN ('ACTIVE', 'FROZEN', 'RECYCLE')),
                CONSTRAINT ck_admin_spaces_source CHECK (source IN ('后台创建', '申请审批')),
                CONSTRAINT ck_admin_spaces_expiry CHECK (expiry_type IN ('fixed_date', 'long_term'))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """,
            "CREATE INDEX ix_admin_spaces_status ON admin_spaces (status)",
            "CREATE INDEX ix_admin_spaces_owner ON admin_spaces (owner_id)",
            """
            CREATE TABLE IF NOT EXISTS admin_space_products (
                id VARCHAR(64) PRIMARY KEY,
                space_id VARCHAR(64) NOT NULL UNIQUE,
                product_id VARCHAR(64) NOT NULL,
                product_name VARCHAR(80) NOT NULL,
                immutable_binding BOOLEAN NOT NULL DEFAULT TRUE,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                CONSTRAINT fk_admin_space_products_space FOREIGN KEY (space_id) REFERENCES admin_spaces(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """,
            "CREATE INDEX ix_admin_space_products_product ON admin_space_products (product_id)",
            """
            CREATE TABLE IF NOT EXISTS admin_space_members (
                id VARCHAR(64) PRIMARY KEY,
                space_id VARCHAR(64) NOT NULL,
                user_id VARCHAR(64) NOT NULL,
                role VARCHAR(32) NOT NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                UNIQUE KEY uq_admin_space_members_user (space_id, user_id),
                CONSTRAINT fk_admin_space_members_space FOREIGN KEY (space_id) REFERENCES admin_spaces(id) ON DELETE CASCADE,
                CONSTRAINT fk_admin_space_members_user FOREIGN KEY (user_id) REFERENCES admin_users(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """,
            """
            CREATE TABLE IF NOT EXISTS admin_space_applications (
                id VARCHAR(64) PRIMARY KEY,
                name VARCHAR(80) NOT NULL,
                code VARCHAR(48) NOT NULL,
                applicant_id VARCHAR(64) NOT NULL,
                proposed_owner_id VARCHAR(64) NOT NULL,
                product_id VARCHAR(64) NOT NULL,
                product_name VARCHAR(80) NOT NULL,
                purpose VARCHAR(512) NOT NULL,
                expected_members INTEGER NOT NULL,
                requested_storage_gb DECIMAL(12,2) NOT NULL,
                requested_ai_tokens BIGINT NOT NULL,
                expires_at DATETIME NULL,
                status VARCHAR(16) NOT NULL,
                decision_reason VARCHAR(512),
                decision_by VARCHAR(64),
                decision_at DATETIME NULL,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                CONSTRAINT fk_admin_space_applications_applicant FOREIGN KEY (applicant_id) REFERENCES admin_users(id),
                CONSTRAINT fk_admin_space_applications_owner FOREIGN KEY (proposed_owner_id) REFERENCES admin_users(id),
                CONSTRAINT ck_admin_space_applications_status CHECK (status IN ('待审批', '已通过', '已拒绝'))
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """,
            "CREATE INDEX ix_admin_space_applications_status ON admin_space_applications (status)",
            """
            CREATE TABLE IF NOT EXISTS admin_space_audit_events (
                id VARCHAR(64) PRIMARY KEY,
                space_id VARCHAR(64) NOT NULL,
                actor VARCHAR(64) NOT NULL,
                action VARCHAR(64) NOT NULL,
                before_value TEXT,
                after_value TEXT,
                reason VARCHAR(512) NOT NULL,
                result VARCHAR(32) NOT NULL,
                request_id VARCHAR(64) NOT NULL,
                created_at DATETIME NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
            """,
            "CREATE INDEX ix_admin_space_audit_space ON admin_space_audit_events (space_id)",
        ]
    else:
        raise ConfigurationError(f"不支持的数据库方言：{dialect}。")

    with engine.begin() as connection:
        for statement in statements:
            try:
                connection.execute(text(statement))
            except Exception as exc:
                if "duplicate column" in str(exc).lower():
                    continue
                raise


def validate_runtime_database() -> None:
    settings.validate_database()
