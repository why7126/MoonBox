---
change_id: add-frontend-user-menu-profile
status: in_progress
created_at: 2026-08-11 17:36:19
updated_at: 2026-08-11 18:48:00
source_requirement: REQ-0014-frontend-user-menu-profile
sprint: sprint-002
---

# Tasks

## 1. UI Skeleton 与合同确认

- [x] 1.1 在 `RequirementCenterPage` 中建立前台个人资料弹窗 Skeleton：用户菜单入口、弹窗容器、头像区、昵称输入、错误区、footer 操作区。
- [x] 1.2 为弹窗和关键控件增加可访问标签与可测选择器。
- [x] 1.3 产出 1440px Skeleton 截图，覆盖用户菜单打开态与个人资料弹窗默认态。
- [x] 1.4 在 Change trace 中记录 UI Contract、Skeleton 状态、Mock/API 边界和截图路径。

## 2. 前台个人资料弹窗实现

- [x] 2.1 将前台用户菜单“个人资料”入口从占位项改为打开弹窗。
- [x] 2.2 实现 `rc-*` 风格个人资料弹窗，不使用后台 `admin-*` 视觉类。
- [x] 2.3 弹窗仅展示只读账号摘要、单头像预览位、昵称输入、上传/更换按钮、错误提示、取消和保存。
- [x] 2.4 保持现有用户菜单能力不回归：切换空间、设置空间、主题切换、进入后台权限显示和退出登录。

## 3. 头像上传与受保护读取

- [x] 3.1 复用现有头像上传接口和对象存储链路，保持 JPG/PNG/WebP 与 2MB 限制。
- [x] 3.2 实现上传状态机 `idle -> uploading -> done/failed`。
- [x] 3.3 上传中禁用重复选择和保存，失败后允许重试。
- [x] 3.4 上传成功后通过 Bearer token 读取头像资源并即时预览。
- [x] 3.5 保存资料时只提交持久头像 URL，不保存 `blob:` URL。

## 4. 昵称保存与当前用户上下文刷新

- [x] 4.1 昵称最长 128 个字符，保存时去除首尾空白。
- [x] 4.2 昵称允许清空，清空后前台用户菜单回退展示用户名。
- [x] 4.3 保存成功后直接使用接口返回 user 更新前台 currentUser。
- [x] 4.4 同步刷新用户菜单展示和本地会话缓存。
- [x] 4.5 保存失败时保留输入内容并展示受控错误。

## 5. 测试

- [x] 5.1 前端测试覆盖打开个人资料弹窗。
- [x] 5.2 前端测试覆盖头像上传成功、上传失败、重复提交禁用和持久 URL 保存。
- [x] 5.3 前端测试覆盖昵称保存、昵称清空回退用户名和保存失败保留输入。
- [x] 5.4 前端测试覆盖保存成功后 currentUser、用户菜单和会话缓存刷新。
- [x] 5.5 如 API 契约有新增或调整，补充后端集成测试。

## 6. 视觉与边界验收

- [x] 6.1 完成 1440px 用户菜单打开态截图。
- [x] 6.2 完成 1440px 个人资料弹窗默认态截图。
- [x] 6.3 完成头像上传成功预览、上传失败提示、保存失败提示和保存成功菜单刷新截图。
- [x] 6.4 记录 `.rc-profile-modal`、头像区、按钮、错误提示等关键 computed style。
- [x] 6.5 验证 Docker 本地头像上传、受保护读取和前台菜单回显边界；本机 `:3000` 被 unrelated 容器占用，按验收反馈选择 B 改用 Docker Web `:18102` 隔离栈完成等价链路验收。

## 7. 文档与校验

- [x] 7.1 如 API 路径或响应契约变化，同步 `docs/03-api-index.md`。
- [x] 7.2 回填 Change trace 的实现证据、测试命令、视觉证据和最终一致性状态。
- [x] 7.3 运行 `openspec validate add-frontend-user-menu-profile --strict`。
- [x] 7.4 运行相关前端测试与构建。

## 验收返修记录

| 时间 | 反馈 | 调整 | 验证 |
|---|---|---|---|
| 2026-08-11 18:05:00 | 前台与后台个人资料修改交互样式不一致；按方案 A 统一交互结构，并同步给后台增加右上角关闭按钮。 | 前台保留 `rc-*` token，但对齐后台 Modal 宽度、标题行、单头像 48px、关闭入口和成功文案；后台 ProfileModal 增加右上角关闭按钮。 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx admin-auth.test.tsx --run`、`pnpm --dir src/web build`、1440px 前后台截图。 |
| 2026-08-11 18:48:00 | 个人资料弹窗个人信息只显示用户名；前后台菜单头像统一 32px、弹窗头像统一 48px；移除前台昵称字段说明文案。 | 前后台摘要去除产品域/角色后缀；前台菜单头像调为 32px；删除“保存后同步刷新前台用户菜单。”；测试锁定摘要与头像尺寸合同。 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx admin-auth.test.tsx --run`、`pnpm --dir src/web build`、1440px 前后台截图。 |
| 2026-08-11 19:10:00 | 补齐 Docker `:3000` 头像上传、受保护读取和前台菜单回显验收；本机 `:3000` 被 unrelated `tilesfst-web` 占用。 | 用户选择 B 后，临时停止原 `moonbox-web`，使用隔离 Docker 栈在 `:18102` 完成同源 Web/API/MinIO 链路验收，随后清理隔离栈并恢复原 `moonbox-web`。 | `node -e ...` 端到端验收 passed：未授权头像读取 401，Bearer 读取 200，菜单头像 `32px` 且回显昵称，弹窗头像 `48px`；截图 `/private/tmp/req-0014-docker-18102-profile-menu.png`。 |
| 2026-08-11 19:56:00 | 前台更新头像和昵称后进入后台，后台用户菜单未自动更新；前后台主题切换互不跟随；前台昵称输入框文字与背景低对比。 | 新增共享 UI 偏好缓存；admin session 保存/清理派发同步事件；App 在路由切换和事件中重读 admin session；后台跟随 session prop 与共享主题；前台昵称输入显式设置文字色、光标色和 placeholder 色。 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx admin-auth.test.tsx --run`、`pnpm --dir src/web build`、1440px 主题/输入框截图 `/private/tmp/req-0014-modify3-theme-profile-1440.png`。 |
