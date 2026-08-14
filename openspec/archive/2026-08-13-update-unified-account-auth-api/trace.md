---
change_id: update-unified-account-auth-api
source_type: requirement
source_id: REQ-0016-unified-account-auth-api
type: update
status: applied
created_at: 2026-08-12 11:30:00
updated_at: 2026-08-12 13:13:07
sprint: sprint-002
impact:
  backend: true
  web: true
  miniapp: false
  admin: true
  database: false
  storage: true
  api: true
capabilities:
  new: []
  modified:
    - web-admin-auth-system
    - api-governance
prototype:
  present: false
  refs: []
ui_contract:
  required: false
  reason: "REQ-0016 不包含 prototype 且不重做视觉；仅进行现有 UI 的 API/session wiring。"
validation_status: applied
---

# Trace

## Requirement Readiness Report

Result: ready

- `requirement.md`: present
- `user-stories.md`: present
- `business-flow.md`: present
- `acceptance.md`: present
- `trace.md`: present, status `in_sprint`, iteration `sprint-002`
- `prototype/**`: absent; UI Explore Gate not required

## Impact Analysis

```yaml
impact:
  backend: true
  web: true
  miniapp: false
  admin: true
  database: false
  storage: true
  api: true
capabilities:
  new: []
  modified:
    - web-admin-auth-system
    - api-governance
change_type: update
```

## Conflict Report

No `prototype/` artifacts exist for this REQ. Final implementation should preserve existing frontend/admin visual systems and validate behavior through tests and Docker `:3000` evidence.

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-12 13:13:07 | opsx.modify | 修复前台个人资料弹窗、后台用户菜单和后台个人资料弹窗仍可能读取旧 session 头像快照的问题；统一前台文字头像 fallback 为两字规则并保持菜单/弹窗样式一致。 |
| 2026-08-12 12:57:13 | opsx.modify | 修复历史 `avatar_url` 仍指向 `/api/v1/admin/users/avatar/*` 导致已有头像不回显的问题；服务端读模型规范化为 `/api/v1/auth/avatar/*`，旧读取接口仍不恢复。 |
| 2026-08-12 12:50:00 | opsx.modify | 验收反馈确认 Docker `:3000` 可重复验收问题由独立会话处理；本 Change 仅保留 Docker `:3000` 占用与默认端口 `18102` 登录失败尝试记录，不再以该外部治理缺陷阻断 REQ-0016 主体实现收尾。 |
| 2026-08-12 11:43:00 | opsx.apply | 完成统一 `/api/v1/auth/*` 实现、单一 `moonbox.session`、头像上传读取迁移、OpenAPI/API 文档同步和前后端测试；Docker `:3000` 真实边界验证待运行环境启动后补充。 |
| 2026-08-12 11:30:00 | req.opsx | 创建 OpenSpec Change；将 REQ-0016 转为 `update-unified-account-auth-api`，状态 proposed。 |

## 验证记录

| 时间 | 类型 | 命令 / 证据 | 结果 |
|---|---|---|---|
| 2026-08-12 11:39:00 | 后端测试 | `uv run pytest tests/integration/api/test_admin_users.py tests/integration/api/test_requirement_center.py` | 24 passed |
| 2026-08-12 11:42:19 | 前端测试 | `pnpm --dir src/web test --run src/admin-auth.test.tsx src/admin-user-management.test.tsx src/requirement-center.test.tsx src/homepage.test.tsx` | 65 passed |
| 2026-08-12 11:42:19 | 前端构建 | `pnpm --dir src/web build` | passed |
| 2026-08-12 11:42:00 | OpenAPI | `src/web/openapi.json` regenerated from FastAPI `app.openapi()` | passed |
| 2026-08-12 11:42:00 | 静态证据 | `rg "/api/v1/admin/auth|admin/auth|moonbox\\.frontend\\.session|moonbox\\.admin\\.session" src tests docs` | no runtime matches |
| 2026-08-12 11:44:00 | API 标准 | `python scripts/validate-api-standard.py` | passed |
| 2026-08-12 11:44:00 | OpenSpec | `openspec validate update-unified-account-auth-api --strict` | passed |
| 2026-08-12 11:44:00 | OpenSpec 中文 | `python scripts/validate-openspec-language.py --root openspec/changes/update-unified-account-auth-api` | passed |
| 2026-08-12 11:44:00 | Docker 边界 | `node -e` probe `http://localhost:3000/health` | pending: local service not running |
| 2026-08-12 11:48:00 | Docker `:3000` | `HOST_PORT_WEB=3000 docker compose up -d --build backend web minio` | blocked: `tilesfst-web` already binds host port 3000 |
| 2026-08-12 11:49:00 | Docker default port | `docker compose up -d web` then `POST http://localhost:18102/api/v1/auth/login` | blocked: local runtime admin password unknown; stopped MoonBox backend/web after attempt |
| 2026-08-12 12:50:00 | 验收返修 | Docker `:3000` 可重复验收外部治理问题由独立会话处理；本 Change 采用既有 Docker/default-port 尝试记录作为非阻断说明。 | accepted deferral for external governance issue; no code change |
| 2026-08-12 12:57:13 | 后端聚焦测试 | `uv run pytest tests/integration/api/test_admin_users.py::test_legacy_admin_avatar_urls_are_normalized_to_unified_auth_path tests/integration/api/test_admin_users.py::test_old_admin_auth_and_avatar_paths_are_not_registered` | 2 passed |
| 2026-08-12 12:57:13 | 后端回归测试 | `uv run pytest tests/integration/api/test_admin_users.py` | 18 passed |
| 2026-08-12 12:57:13 | 静态证据 | `rg "/api/v1/admin/auth|admin/auth|moonbox\\.frontend\\.session|moonbox\\.admin\\.session" src/backend src/web tests`；`/api/v1/admin/users/avatar` 仅出现在历史头像 URL 规范化逻辑、旧接口不可用测试和迁移文档中。 | passed |
| 2026-08-12 13:13:07 | 前端返修测试 | `pnpm --dir src/web test --run src/admin-user-management.test.tsx src/requirement-center.test.tsx` | 54 passed |
| 2026-08-12 13:13:07 | 前端构建 | `pnpm --dir src/web build` | passed |
| 2026-08-12 13:13:07 | OpenSpec | `openspec validate update-unified-account-auth-api --strict` | passed |
| 2026-08-12 13:13:07 | OpenSpec 中文 | `python scripts/validate-openspec-language.py --root openspec/changes/update-unified-account-auth-api` | passed |
| 2026-08-12 13:13:07 | 文档/代码空白 | `git diff --check -- <touched files>` | passed |
| 2026-08-12 13:13:07 | OpenSpec 任务 | `openspec instructions apply --change update-unified-account-auth-api --json` | 21/21 complete |

## 验收返修记录

| 时间 | 反馈 | 范围判定 | 处理 |
|---|---|---|---|
| 2026-08-12 13:13:07 | 用户管理列表和前台菜单头像已恢复，但前台个人资料弹窗、后台用户菜单、后台个人资料弹窗仍可能使用旧 session 头像快照；前台文字头像 fallback 为一字且背景样式与整体不一致。 | 属于 REQ-0016 统一账号 session 与统一头像 API 后的 UI 回显一致性缺口；不新增 API、不恢复旧路径、不改变权限或存储边界。 | 后台旧头像 session 通过 `/api/v1/auth/me` 刷新当前用户摘要；前台个人资料弹窗优先当前上下文头像并忽略旧 admin 头像 fallback；前台文字头像 fallback 统一为两字规则。 |
| 2026-08-12 12:57:13 | 历史 `avatar_url` 仍指向旧头像读取路径，导致统一 API 迁移后已有头像回显失败。 | 属于 REQ-0016 破坏性 API 迁移的存量数据兼容缺口；不扩大 API 边界，不恢复旧接口，不改变对象存储 Key。 | 后端读模型规范化历史 URL；补充集成测试与文档/spec 说明；前端可继续用统一 Bearer token 读取 `/api/v1/auth/avatar/*`。 |
| 2026-08-12 12:50:00 | Docker `:3000` 可重复验收问题已由独立会话处理，本 Change 仅保留常规 Docker/default-port 尝试记录。 | 不扩大 REQ-0016 的 API、权限、对象存储或前端行为边界；属于外部本地治理/端口复现问题，不作为当前 Change archive 阻断。 | `tasks.md` 任务 4.4 改为记录 Docker/default-port 尝试与外部治理 deferral；`trace.md` 保留失败原因和非阻断结论。无需更新源码、测试、OpenAPI、DB 或长期 API 文档。 |

## Cross-cutting Gate

Change / Tags / Refs:

- Change: `update-unified-account-auth-api`
- Tags: `media-upload`
- Refs: `docs/knowledge-base/best-practices/admin-media-upload-chain.md`

AC-XCUT: pass  
knowledge_base_refs: pass  
best-practices read: pass  
Verdict: PROCEED

## Prototype Gate

Prototype Gate: n/a  
UI Skeleton: n/a  
1440px visual acceptance: n/a  
key interaction screenshots: n/a  
computed style acceptance: n/a  
Mock/API boundary: n/a  
REQ final consistency: pending archive check
