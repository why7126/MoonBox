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
);

CREATE INDEX IF NOT EXISTS ix_admin_spaces_status ON admin_spaces (status);
CREATE INDEX IF NOT EXISTS ix_admin_spaces_owner ON admin_spaces (owner_id);

CREATE TABLE IF NOT EXISTS admin_space_products (
    id TEXT PRIMARY KEY,
    space_id TEXT NOT NULL UNIQUE,
    product_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    immutable_binding INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (space_id) REFERENCES admin_spaces(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_admin_space_products_product ON admin_space_products (product_id);

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
);

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
    status TEXT NOT NULL CHECK (status IN ('待审批', '已通过', '已拒绝', '已撤回')),
    application_type TEXT NOT NULL DEFAULT 'create',
    target_space_id TEXT,
    decision_reason TEXT,
    decision_by TEXT,
    decision_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (applicant_id) REFERENCES admin_users(id),
    FOREIGN KEY (proposed_owner_id) REFERENCES admin_users(id)
);

CREATE INDEX IF NOT EXISTS ix_admin_space_applications_status ON admin_space_applications (status);

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
);

CREATE INDEX IF NOT EXISTS ix_admin_space_audit_space ON admin_space_audit_events (space_id);
