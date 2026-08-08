-- MoonBox SQLite baseline schema.
-- Business tables evolve through reviewed OpenSpec changes.

CREATE TABLE IF NOT EXISTS schema_metadata (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    schema_version TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO schema_metadata (id, schema_version)
VALUES (1, '0000-initialize-project');

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
);

CREATE INDEX IF NOT EXISTS ix_admin_users_role ON admin_users (role);
CREATE INDEX IF NOT EXISTS ix_admin_users_status ON admin_users (status);

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
);

CREATE INDEX IF NOT EXISTS ix_admin_sessions_user_id ON admin_sessions (user_id);
CREATE INDEX IF NOT EXISTS ix_admin_sessions_token_hash ON admin_sessions (token_hash);

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
);
