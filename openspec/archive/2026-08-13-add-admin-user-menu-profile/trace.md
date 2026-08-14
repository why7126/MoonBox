---
change_id: add-admin-user-menu-profile
type: add
status: applied
source_requirement: REQ-0011-admin-user-menu-profile
source_sprint: sprint-002
created_at: 2026-08-10 09:30:11
updated_at: 2026-08-10 10:23:28
prototype_sources:
  - issues/requirements/review/REQ-0011-admin-user-menu-profile/prototype/web/prototype.html
  - issues/requirements/review/REQ-0011-admin-user-menu-profile/prototype/web/context.md
knowledge_base_refs:
  - docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md
  - docs/knowledge-base/best-practices/admin-media-upload-chain.md
  - docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
  - docs/knowledge-base/retrospectives/sprint-001-retrospective.md
conflict_resolution: documented
ui_skeleton: documented
visual_acceptance_1440: passed
req_final_consistency: passed
---

# Trace

## 状态

```yaml
status: applied
source_requirement: REQ-0011-admin-user-menu-profile
source_sprint: sprint-002
task_progress: 29/29
prototype_gate:
  decomposition: done
  ui_skeleton: documented
  visual_acceptance_1440: passed
  req_final_consistency: passed
```

## 实现摘要

- 后端新增 `PATCH /api/v1/admin/auth/me`，只允许当前登录后台管理员更新自己的 `nickname` 与 `avatar_url`。
- 后端新增当前用户资料更新 schema 和 repository 方法，昵称 trim/清空/128 字符校验，拒绝 `blob:` 头像 URL，并返回最新当前用户摘要。
- 前端用户菜单“个人资料”改为打开 `ProfileModal`，复用创建用户头像上传结构，保存成功后刷新当前用户摘要、本地 session 和菜单展示。
- 前端头像显示链路统一处理持久 URL：上传后的 `blob:` 仅用于预览，不写入用户资料保存体；菜单栏、用户列表、个人资料弹窗和用户编辑弹窗读取持久头像时使用当前后台 session token 鉴权 fetch，并通过共享缓存复用同一份 `blob:` object URL。
- 个人资料保存成功后同步更新当前用户摘要、本地 session 以及用户列表中的当前用户行，避免菜单栏与列表数据源短暂不一致。
- API 索引已同步；`src/web/openapi.json` 已由 FastAPI 导出更新。Orval 阶段因当前 `src/web/node_modules/.bin/orval` 不存在未生成客户端，本项目当前前端 API client 为手写 `adminAuth.ts`，已同步并通过 build/test。

## 验证记录

| 时间 | 类型 | 命令 / 证据 | 结果 |
|---|---|---|---|
| 2026-08-10 09:39:00 | 后端集成测试 | `uv run pytest tests/integration/api/test_admin_users.py -q` | 16 passed |
| 2026-08-10 09:44:52 | 前端测试 | `pnpm --dir src/web test -- admin-user-management.test.tsx admin-auth.test.tsx` | 4 files / 29 tests passed |
| 2026-08-10 09:46:30 | 前端构建 | `pnpm --dir src/web build` | passed |
| 2026-08-10 09:46:30 | OpenAPI 导出 | `bash scripts/generate-openapi-client.sh` | OpenAPI JSON 已导出；Orval 可执行文件缺失，客户端生成跳过 |
| 2026-08-10 09:49:20 | 1440px 视觉验收 | `/tmp/moonbox-req0011-profile-modal-open-1440.png` | Modal 宽 560px；单头像预览；无 `modal-card`；保存/上传按钮可见 |
| 2026-08-10 09:49:20 | 1440px 交互验收 | `/tmp/moonbox-req0011-profile-modal-1440.png` | 保存后用户菜单展示刷新为“月盒管理员” |
| 2026-08-10 10:01:42 | 前端返修测试 | `pnpm --dir src/web test -- admin-user-management.test.tsx admin-auth.test.tsx` | 4 files / 30 tests passed；覆盖保存后菜单/列表相对头像 URL 按 API base 渲染、创建用户保存持久 URL |
| 2026-08-10 10:02:10 | 前端返修构建 | `pnpm --dir src/web build` | passed |
| 2026-08-10 10:04:39 | 1440px 返修验收 | `/tmp/moonbox-req0011-profile-avatar-modify-1440.png` | 保存后个人资料 Modal 关闭；用户菜单和用户列表均显示后端返回的持久头像 URL |
| 2026-08-10 10:10:53 | 前端鉴权头像测试 | `pnpm --dir src/web test -- admin-user-management.test.tsx admin-auth.test.tsx` | 4 files / 30 tests passed；覆盖头像 GET 携带 `Authorization`，菜单/列表最终使用 `blob:` 图像 |
| 2026-08-10 10:11:10 | 前端鉴权头像构建 | `pnpm --dir src/web build` | passed |
| 2026-08-10 10:11:44 | 1440px 鉴权头像验收 | `/tmp/moonbox-req0011-profile-auth-avatar-modify-1440.png` | 保存后菜单栏和用户列表头像均显示为 `blob:`；头像 GET `avatarAuthHits=3`，均携带 `Bearer admin-token` |
| 2026-08-10 10:21:34 | 前端共享头像测试 | `pnpm --dir src/web test -- admin-user-management.test.tsx admin-auth.test.tsx` | 4 files / 31 tests passed；覆盖同 URL 头像缓存复用、两个编辑弹窗已有头像鉴权显示、保存后同步列表当前用户行 |
| 2026-08-10 10:22:00 | 前端共享头像构建 | `pnpm --dir src/web build` | passed |
| 2026-08-10 10:23:28 | 1440px 共享头像验收 | `/tmp/moonbox-req0011-profile-shared-avatar-modify-1440.png` | 菜单栏、用户列表、个人资料弹窗、用户编辑弹窗四处头像均为同一个 `blob:`；`avatarAuthHits=1` |

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-10 09:30:11 | req.opsx | 从 REQ-0011 创建 OpenSpec Change，承接个人资料 Modal 原型、单头像上传结构、admin-modal/media-upload 横切 AC、UI Skeleton 和 1440px 视觉验收要求。 |
| 2026-08-10 09:50:12 | opsx.apply | 完成当前用户资料 API、个人资料 Modal、上传/保存状态、测试、API 文档、OpenAPI 导出和 1440px 视觉验收。 |
| 2026-08-10 10:04:39 | opsx.modify | 修复保存后菜单栏和用户列表头像无法显示的问题：持久相对 URL 渲染时补齐 API base，上传预览 `blob:` 不再进入用户保存体，并补充测试、构建和 1440px 返修验收。 |
| 2026-08-10 10:11:44 | opsx.modify | 基于验收截图进一步修复头像鉴权链路：菜单栏和用户列表不再直接用普通 `<img>` 请求受保护头像，改为带后台 token fetch 后转 `blob:` 展示，并补充鉴权请求断言与 1440px 证据。 |
| 2026-08-10 10:23:28 | opsx.modify | 统一头像鉴权展示缓存，菜单栏、用户列表、个人资料弹窗和用户编辑弹窗共同复用同一持久 URL 的 `blob:`，并在个人资料保存后同步列表当前用户行。 |
| 2026-08-13 22:42:34 | opsx.archive | 归档前复核 REQ-0011 requirement、acceptance、prototype、Change design 与 1440px 验收证据一致，prototype final consistency 标记为 passed。 |
