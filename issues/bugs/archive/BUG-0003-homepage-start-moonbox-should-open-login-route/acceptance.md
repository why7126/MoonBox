---
bug_id: BUG-0003-homepage-start-moonbox-should-open-login-route
acceptance_status: passed
created_at: 2026-08-11 08:27:11
updated_at: 2026-08-14 16:29:34
---

# 验收标准

## 回归验收

### AC-001 首页 CTA 进入独立登录路由

WHEN 用户访问 `http://localhost:18102/`
AND 点击首页「开启 MoonBox」
THEN 浏览器地址应变为 `/login`
AND 页面应展示前台登录页
AND 地址不应包含 `#login`。

### AC-002 顶部入口进入独立登录路由

WHEN 用户访问 `http://localhost:18102/`
AND 点击首页「打开第一个项目」
THEN 浏览器地址应变为 `/login`
AND 页面应展示前台登录页
AND 地址不应包含 `#login`。

### AC-003 直接访问登录页

WHEN 用户直接访问或刷新 `http://localhost:18102/login`
THEN 页面应展示前台登录页
AND 不应展示官网首页内容作为主视图
AND 不应展示管理后台登录页。

### AC-004 返回首页

WHEN 用户位于 `/login`
AND 点击「返回首页」
THEN 浏览器地址应回到 `/`
AND 页面应展示官网首页。

### AC-005 登录提交后保持既有前台流转

WHEN 用户位于 `/login`
AND 填写前台登录原型表单并提交
THEN 浏览器地址应进入 `/requirements`
AND 当前原型阶段不应调用后台登录 API
AND 不应展示管理后台登录页。

### AC-006 未登录访问前台需求中心回到前台登录

WHEN 用户未建立前台登录状态
AND 访问 `/requirements`
THEN 浏览器地址应回到 `/login`
AND 页面应展示前台登录页
AND 不应展示管理后台登录页。

### AC-007 需求中心用户菜单识别后台权限

WHEN 用户已建立前台登录状态
AND 本地存在有效后台 admin session
AND 进入 `/requirements`
THEN 用户菜单应展示后端返回的当前用户名称
AND 不应显示「未登录」
AND 有后台权限时应展示「进入后台」。

### AC-008 仅前台登录时用户菜单不显示未登录

WHEN 用户已建立前台登录状态
AND 本地不存在后台 admin session
AND 进入 `/requirements`
THEN 用户菜单应展示前台登录用户名
AND 不应显示「未登录」
AND 不应展示「进入后台」。

### AC-009 匿名上下文使用前台用户名兜底

WHEN 用户已建立前台登录状态
AND 需求中心上下文返回空用户、空用户名或「未登录」
THEN 用户菜单应展示前台登录用户名
AND 不应显示「未登录」。

### AC-010 统一登录页替代管理后台登录页

WHEN 用户未登录并访问 `/admin`
THEN 浏览器地址应回到 `/login`
AND 页面应展示统一 MoonBox 登录页
AND 不应展示独立的「管理后台登录」页面。

### AC-011 统一登录页调用后台登录 API

WHEN 用户在 `/login` 输入后台账号密码并提交
THEN 系统应调用既有后台登录 API
AND 登录成功后应保存后台 session 与前台进入态
AND 浏览器地址应进入 `/requirements`。

### AC-012 Docker Web 同源登录 API 可用

WHEN Docker Web 通过同源 `/api/v1/admin/auth/login` 调用后台登录 API
AND 使用 `admin/Admin123!` 登录
THEN 后端容器应保持 healthy
AND 登录 API 应返回 200 JSON
AND 不应因需求中心服务导入期路径解析失败返回 502 或前端兜底错误。

### AC-013 需求中心退出登录清理完整会话

WHEN 用户已登录进入 `/requirements`
AND 点击用户菜单中的「退出登录」
THEN 系统应清理 `moonbox.frontend.session`
AND 系统应清理 `moonbox.admin.session`
AND 应调用后台 logout API 吊销后台会话
AND 浏览器地址应跳转到 `/login`。

### AC-014 用户菜单昵称与空间显示规则

WHEN 用户进入 `/requirements`
THEN 前台用户菜单第一行应显示用户昵称
AND 前台用户菜单第二行应显示当前空间
AND 当用户昵称为空时，前台用户菜单第一行应显示用户名。

WHEN 用户进入 `/admin`
THEN 后台用户菜单应显示用户昵称
AND 当用户昵称为空时，后台用户菜单应显示用户名
AND 后台用户触发区不应显示角色、空间或其他第二行信息。

### AC-015 昵称保存后同步当前会话展示

WHEN 当前登录用户通过「个人资料」修改昵称
THEN 后端当前用户资料应保存新昵称
AND `moonbox.admin.session` 应同步新昵称
AND 后台用户菜单应立即显示新昵称
AND 前台需求中心用户菜单应通过当前 admin token 显示新昵称。

WHEN 管理员通过「用户管理」编辑当前登录用户列表项的昵称
THEN 后台用户菜单应立即显示新昵称
AND `moonbox.admin.session` 应同步新昵称。

### AC-016 前台用户菜单头像展示

WHEN 当前登录用户存在头像地址
AND 用户进入 `/requirements`
THEN 需求中心 BFF 应在 `current_user.avatar_url` 返回头像地址
AND 前台用户菜单应使用后台 admin token 读取受保护头像资源
AND 前台用户菜单应显示用户头像。

WHEN 当前登录用户头像地址为空或头像读取失败
THEN 前台用户菜单应回退显示用户名称首字。

## 测试建议

- 更新 `src/web/src/homepage.test.tsx` 中关于 `#login` 的断言。
- 增加或调整应用路由测试，覆盖直接访问 `/login` 的行为。
- 覆盖 `/requirements` 未建立前台 session 时回到 `/login` 的行为，避免前后台登录入口混淆。
- 覆盖已有后台 admin session 时需求中心上下文请求携带 Bearer token 并展示「进入后台」。
- 覆盖仅有前台 session 且后端返回显式匿名、空用户名或缺失用户对象时，用户菜单显示前台用户名而不是「未登录」。
- 覆盖 `/admin` 未登录时使用统一 `/login` 页面，不再展示「管理后台登录」。
- 覆盖 `/login` 提交调用后台登录 API，成功后进入 `/requirements`。
- 覆盖需求中心服务在容器浅路径下优先使用 `MOONBOX_GOVERNANCE_ROOT`，避免导入期根路径兜底越界。
- 覆盖需求中心用户菜单「退出登录」清理前台 session 与后台 admin session，调用后台 logout API 并跳转 `/login`。
- 覆盖前台用户菜单显示昵称与当前空间，昵称为空时使用用户名；覆盖后台用户菜单仅显示一行昵称，昵称为空时使用用户名，不显示角色第二行。
- 覆盖通过个人资料保存当前用户昵称后，后端当前用户、admin session、后台菜单和前台需求中心菜单同步新昵称；覆盖用户管理编辑当前登录用户列表项后，后台菜单和 admin session 同步新昵称。
- 覆盖需求中心 BFF 返回 `current_user.avatar_url`，前台用户菜单用 admin token 读取受保护头像资源，头像为空时回退首字；同步运行后台头像展示回归，避免前后台头像逻辑分叉。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: fix-homepage-login-route
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

