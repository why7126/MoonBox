---
change_id: add-frontend-user-menu-profile
type: add
status: in_progress
created_at: 2026-08-11 17:36:19
updated_at: 2026-08-11 18:48:00
source_requirement: REQ-0014-frontend-user-menu-profile
sprint: sprint-002
linked_requirements:
  - REQ-0014-frontend-user-menu-profile
knowledge_base_refs:
  - docs/knowledge-base/best-practices/admin-media-upload-chain.md
  - docs/standards/prototype-ui-acceptance.md
prototype_refs:
  - path: issues/requirements/review/REQ-0014-frontend-user-menu-profile/prototype/web/prototype.html
    role: html-structure
  - path: issues/requirements/review/REQ-0014-frontend-user-menu-profile/prototype/web/context.md
    role: prototype-decomposition
ui_contract_status: accepted
ui_skeleton_status: accepted
visual_acceptance_1440: partial
computed_style_acceptance: accepted
mock_api_boundary: declared
req_final_consistency: aligned
---

# Trace

## 创建记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-11 17:36:19 | req.opsx | 从 REQ-0014 创建 OpenSpec Change，状态为 proposed。 |
| 2026-08-11 17:52:00 | opsx.apply | 完成前台个人资料弹窗实现、测试、构建和 1440px 视觉证据；Docker `:3000` 边界因本地栈端口与账号阻塞未完成。 |
| 2026-08-11 18:05:00 | opsx.modify | 验收返修：统一前后台个人资料 Modal 交互结构，前台保留 `rc-*` 视觉 token，后台同步增加右上角关闭按钮。 |
| 2026-08-11 18:48:00 | opsx.modify | 验收返修：个人资料摘要仅显示用户名，前后台菜单头像统一 32px、弹窗头像统一 48px，并移除前台昵称字段说明文案。 |
| 2026-08-11 19:10:00 | opsx.modify | 验收返修：本机 `:3000` 被 unrelated `tilesfst-web` 占用，按用户选择 B 改用 Docker Web `:18102` 隔离栈补齐头像上传、受保护读取和前台菜单回显证据；验收后已清理隔离栈并恢复原 `moonbox-web`。 |
| 2026-08-11 19:56:00 | opsx.modify | 验收返修：补齐前台保存头像/昵称后进入后台的用户菜单同步，统一前后台界面主题偏好缓存，并修复前台个人资料昵称输入框低对比文字色。 |

## Requirement Readiness Report

| 项 | 结果 |
|---|---|
| status | in_sprint |
| sprint | sprint-002 |
| requirement.md | present |
| user-stories.md | present |
| business-flow.md | present |
| acceptance.md | present |
| prototype/web | present |
| Readiness | Ready |

## Conflict Report

| 来源 | 状态 | 处理 |
|---|---|---|
| prototype.html | present | 作为 HTML 结构和视觉方向最高事实源。 |
| prototype context | present | 承接页面清单、组件层级、状态矩阵和 1440px 验收焦点。 |
| acceptance.md | present | 功能 AC、AC-XCUT、AC-PROTOTYPE 全部转入 design/tasks/spec。 |
| ui-design.md | present | 作为 `rc-*` 视觉 token 和原型驱动 UI Gate 约束。 |
| openspec/specs | no direct frontend profile spec | 新增 `web-catalog-user-profile` 能力。 |

## UI Contract

- 状态：accepted
- 事实源优先级：`prototype.html > context.md > acceptance.md > requirement.md > ui-design.md > existing implementation > specs`
- Mock/API 边界：实现使用真实头像上传接口 `/api/v1/admin/users/avatar`、受保护头像读取 URL 与当前用户保存接口 `/api/v1/admin/auth/me`；Playwright 视觉证据使用路由 mock 固定 UI 状态，不作为 API 成功证据。
- 权限：后端认证上下文决定当前用户，前端不得指定任意目标用户。

## UI Skeleton

- 状态：accepted
- 先行任务：tasks 1.1 至 1.4 已完成
- 1440px Skeleton 证据：
  - `/private/tmp/req-0014-user-menu-1440.png`
  - `/private/tmp/req-0014-profile-default-1440.png`

## 实现证据

| 文件 | 说明 |
|---|---|
| `src/web/src/pages/catalog/RequirementCenterPage.tsx` | 新增前台 `FrontendProfileModal`、个人资料入口、头像上传状态机、保存后 currentUser 与前台 session 同步。 |
| `src/web/src/pages/home/uiPreferences.ts` | 新增共享 UI 偏好缓存，用于前后台主题跨路由同步。 |
| `src/web/src/App.tsx` | 在路由切换和 admin session 事件中重读当前后台 session，避免前台保存后后台菜单拿旧 state。 |
| `src/web/src/styles/globals.css` | 新增 `rc-profile-*` 弹窗、头像区、错误提示和按钮样式，保持前台 `rc-*` 视觉边界。 |
| `src/web/src/requirement-center.test.tsx` | 覆盖打开弹窗、头像上传成功/失败、持久 URL 保存、昵称保存/清空回退、保存失败保留输入、菜单与 session 刷新。 |
| `src/web/src/pages/admin/AdminUserManagementPage.tsx` | 后台个人资料 Modal 增加右上角关闭按钮，用于与前台个人资料交互结构对齐。 |
| `src/web/src/admin-user-management.test.tsx` | 覆盖后台个人资料 Modal 标题行、右上角关闭按钮和共享主题偏好。 |
| `src/web/src/admin-auth.test.tsx` | 覆盖前台进入后台时使用刷新后的 admin session。 |

## 验收证据

| 类型 | 状态 | 路径/说明 |
|---|---|---|
| 1440px 用户菜单 | passed | `/private/tmp/req-0014-user-menu-1440.png` |
| 1440px 弹窗默认态 | passed | `/private/tmp/req-0014-profile-default-1440.png` |
| 上传成功/失败 | passed | `/private/tmp/req-0014-profile-upload-done-1440.png`、`/private/tmp/req-0014-profile-upload-failed-1440.png` |
| 保存成功/失败 | passed | `/private/tmp/req-0014-profile-saved-menu-1440.png`、`/private/tmp/req-0014-profile-save-failed-1440.png` |
| apply 初版 computed style | superseded | 初版 `.rc-profile-modal width=480px`、头像 `52px x 52px`；已由 2026-08-11 18:05:00 返修证据替代。 |
| 返修后前台交互结构 | passed | `/private/tmp/req-0014-modify-frontend-profile-parity-1440.png`；`.rc-profile-modal width=560px`，`hasHead=true`，`hasClose=true`，`hasEyebrow=false`，头像 `48px x 48px`。 |
| 返修后后台关闭按钮 | passed | `/private/tmp/req-0014-modify-admin-profile-close-1440.png`；`.admin-profile-modal width=560px`，`hasHead=true`，`hasClose=true`，头像 `48px x 48px`。 |
| 二次返修后前台摘要/头像/文案 | passed | `/private/tmp/req-0014-modify2-frontend-profile-clean-1440.png`；摘要 `superadmin`，无“保存后同步刷新前台用户菜单。”，菜单头像 `32px x 32px`，弹窗头像 `48px x 48px`。 |
| 二次返修后后台摘要/头像 | passed | `/private/tmp/req-0014-modify2-admin-profile-clean-1440.png`；摘要 `superadmin`，菜单头像 `32px x 32px`，弹窗头像 `48px x 48px`。 |
| Docker 上传读取回显 | passed | 本机 `:3000` 被 unrelated `tilesfst-web` 占用；按用户选择 B，临时释放 MoonBox Web `:18102` 并启动隔离 Docker 栈完成验收。结果：上传返回持久头像 URL `/api/v1/admin/users/avatar/e070c2c2450f4ee69e86c158d7fd6333.webp`，未授权读取 401，Bearer 读取 200 且内容长度 27，保存昵称 `Docker18102 Profile` 后前台菜单显示该昵称，菜单头像 `32px x 32px` 且为受保护读取后的 blob，弹窗摘要 `admin`，弹窗头像 `48px x 48px`，说明文案已移除；截图 `/private/tmp/req-0014-docker-18102-profile-menu.png`。 |
| 三次返修后主题/输入框/后台菜单同步 | passed | `/private/tmp/req-0014-modify3-theme-profile-1440.png`；前台昵称输入 `color=rgb(233, 238, 251)`、`background=rgb(14, 16, 35)`、`caretColor=rgb(203, 163, 92)`；前台切换 light 后进入后台，后台 `data-theme=light`，后台菜单显示刷新后的昵称。 |

## 验证命令

| 命令 | 结果 |
|---|---|
| `pnpm --dir src/web test -- requirement-center.test.tsx --run` | passed，5 个测试文件 56 个测试通过。 |
| `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx admin-auth.test.tsx --run` | passed，5 个测试文件 59 个测试通过。 |
| `pnpm --dir src/web build` | passed，`tsc -b && vite build` 成功。 |
| `openspec validate add-frontend-user-menu-profile --strict` | passed，Change valid。 |
| `node -e "<Docker 18102 头像上传/读取/回显验收脚本>"` | passed，隔离 Docker 栈验证未授权读取 401、Bearer 读取 200、前台菜单头像 32px 与昵称回显、弹窗头像 48px。 |
| `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx admin-auth.test.tsx --run` | passed，5 个测试文件 61 个测试通过。 |
| `pnpm --dir src/web build` | passed，`tsc -b && vite build` 成功。 |
| `node -e "<1440px 主题偏好/昵称输入 computed style 验收脚本>"` | passed，验证前后台主题偏好同步、后台菜单昵称同步、前台昵称输入框可读对比。 |
