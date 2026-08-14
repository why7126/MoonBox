---
change_id: add-requirement-center-real-data-integration
status: applied
created_at: 2026-08-10 22:12:00
updated_at: 2026-08-11 13:49:52
---

# Tasks

## 1. UI Skeleton 与数据契约先行

- [x] 1.1 确认 REQ-0013 `prototype/web/context.md`、`prototype/web/prototype.html`、`acceptance.md` 和 REQ-0012 页面实现为 UI 与状态事实源。
- [x] 1.2 在需求中心页面建立真实数据状态 Skeleton，覆盖 LoadingState、ErrorState、ForbiddenState、EmptyWorkspaceState、EmptyFilterState 和 DriftWarning。
- [x] 1.3 标注可测选择器，覆盖 `data-state`、`data-stage`、`data-issue-id`、用户菜单、空间浮层、空间设置、`#themeSwitch` 和 toast。
- [x] 1.4 定义前后端共享的数据契约或等价 TypeScript/Pydantic schema，覆盖 current_user、workspaces、permissions、stats、filters、issues 和 action。
- [x] 1.5 明确 Mock/API 边界：生产运行时不得使用 `initialIssues`、`workspaces`、`currentUser`，测试 fixture 仅用于测试路径。

## 2. 后端 BFF 聚合接口

- [x] 2.1 新增 `/api/v1/requirement-center/context` 路由并接入统一响应结构。
- [x] 2.2 新增需求中心 response schema，字段使用白名单映射。
- [x] 2.3 实现 REQ/BUG registry 读取和基础对象聚合。
- [x] 2.4 实现 Issue `trace.md`、Sprint 四件套和 OpenSpec Change 元信息读取。
- [x] 2.5 实现 9 阶段状态映射和对象级 `blocked` / `drift` 提示。
- [x] 2.6 实现空间列表、当前空间、当前用户和最小权限态返回。
- [x] 2.7 增加读取边界和轻量缓存，避免无界扫描 archive、generated、node_modules、dist、coverage。
- [x] 2.8 实现错误脱敏，禁止响应包含本机绝对路径、系统用户名、Markdown 全文、`.env`、token、日志或堆栈。

## 3. 前端真实数据接入

- [x] 3.1 新增需求中心 API client 或 hook，统一处理 loading、success、error 和 retry。
- [x] 3.2 替换 `initialIssues`，让看板卡片、统计、筛选选项和阶段计数来自接口数据。
- [x] 3.3 替换 `workspaces`，让空间列表、当前空间和本地最近选择校验来自接口数据。
- [x] 3.4 替换 `currentUser`，让头像缩写、用户名称和“进入后台”等入口由接口权限态驱动。
- [x] 3.5 实现加载态、错误态、空空间态、筛选无结果态、无权限态和 drift warning 展示。
- [x] 3.6 切换空间、保存空间设置或点击重试后重新请求 context，并保持统计、筛选、卡片和用户区摘要一致。
- [x] 3.7 保持 REQ-0012 已验收的侧边栏、用户菜单、空间切换、空间设置弹窗、主题切换和 9 阶段看板视觉结构。

## 4. API、文档与安全同步

- [x] 4.1 同步 `docs/03-api-index.md` 中需求中心 API 说明。
- [x] 4.2 如项目当前 OpenAPI 来源需要更新，补齐 `/api/v1/requirement-center/context` schema。
- [x] 4.3 同步安全规则或测试说明，记录治理文件字段白名单和错误脱敏边界。
- [x] 4.4 在 Change trace 记录 Mock/API 边界、数据来源、读取排除项和权限规则。

## 5. 测试

- [x] 5.1 后端测试覆盖 context 接口成功返回真实治理对象。
- [x] 5.2 后端测试覆盖 9 阶段状态映射、trace 优先级和 drift 提示。
- [x] 5.3 后端测试覆盖字段白名单、错误脱敏和读取边界。
- [x] 5.4 前端测试覆盖 loading、error、empty workspace、empty filter、forbidden 和 retry。
- [x] 5.5 前端测试覆盖真实数据筛选、搜索、统计一致性和 9 阶段列保留。
- [x] 5.6 前端测试覆盖权限态入口：进入后台、设置空间、创建或加入空间。
- [x] 5.7 前端测试确认生产运行时不再依赖 `initialIssues`、`workspaces`、`currentUser`。

## 6. 视觉验收与追溯

- [x] 6.1 执行 1440px 桌面视觉验收，覆盖真实数据首屏、加载态、错误态、空态、筛选无结果态、权限差异态和空间切换后刷新状态。
- [x] 6.2 记录 computed style 或等价证据，覆盖状态容器、统计 skeleton、错误按钮、空态说明、9 阶段列宽和卡片文本溢出。
- [x] 6.3 回填 Change trace 的 UI Skeleton、1440px 视觉证据、computed style、Mock/API 边界和最终一致性状态。
- [x] 6.4 更新 sprint-002 acceptance-report 中 REQ-0013 验收证据。
- [x] 6.5 归档前确认 REQ-0013 requirement.md、acceptance.md、trace.md 与 Change design、实现证据和真实数据行为一致。

## 验收返修记录

| 时间 | 反馈 | 调整 | 验证 |
|---|---|---|---|
| 2026-08-11 13:49:52 | 空间列表仍由后端硬编码演示数据返回，不是真实空间事实源。 | 移除 `moonbox-platform`、`moonbox-growth`、`demo-founder` 固定数组；首版在不新增 Workspace DB 边界的前提下，从 `MOONBOX_GOVERNANCE_ROOT/project.yaml` 派生当前项目空间，并结合治理对象负责人和当前登录用户计算成员数与空间角色。 | `uv run pytest tests/integration/api/test_requirement_center.py` 7 passed。 |
| 2026-08-10 23:40:00 | `/requirements` 未登录可访问；版本号为硬编码 Mock；Docker 下 context 加载失败；失败时用户菜单显示“加载中 / 加载空间中”。 | `/requirements` 增加登录守卫，context BFF 增加 Bearer 鉴权；版本 badge 改为 `PRODUCT_VERSION`；Docker 后端新增只读治理事实源挂载和 `MOONBOX_GOVERNANCE_ROOT`；context 请求携带 token，数据源缺失返回脱敏 503，未登录时不进入需求中心页面。 | `uv run pytest tests/integration/api/test_requirement_center.py` 5 passed；`pnpm --dir src/web test -- requirement-center.test.tsx admin-auth.test.tsx --run` 5 files / 41 tests passed；`pnpm --dir src/web build` passed；`docker compose config --quiet` passed。 |
