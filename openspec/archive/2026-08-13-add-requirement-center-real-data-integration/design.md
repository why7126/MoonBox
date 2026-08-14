---
change_id: add-requirement-center-real-data-integration
status: applied
source_requirement: REQ-0013-requirement-center-real-data-integration
source_sprint: sprint-002
created_at: 2026-08-10 22:12:00
updated_at: 2026-08-11 13:49:52
---

# 设计说明

## 背景

前台需求中心当前已有 UI 骨架、9 阶段看板、筛选搜索、用户菜单、空间切换和空间设置交互，但生产运行时数据仍来自页面内静态 Mock。REQ-0013 要将页面数据源替换为真实后端聚合结果，并在不重做 REQ-0012 视觉结构的前提下补齐加载、错误、空态、权限和安全脱敏边界。

当前后端尚无 REQ/BUG/Sprint/OpenSpec/Workspace 的完整产品化数据库模型，因此首版采用 BFF 聚合接口读取治理文件事实源，后续再演进为数据库索引或缓存。

## 目标 / 非目标

**目标：**

- 提供需求中心首屏上下文 API，返回用户、空间、权限、统计、筛选和治理对象。
- 从治理事实源聚合 REQ、BUG、Sprint 和 OpenSpec Change 状态，并映射为 9 阶段看板数据。
- 用真实接口数据替换前端 `initialIssues`、`workspaces`、`currentUser` 运行时依赖。
- 覆盖加载态、错误态、空态、筛选无结果态、无权限态和空间切换后的刷新。
- 保持 REQ-0012 已验收的页面结构、视觉 token、侧边栏、用户菜单、空间切换和看板密度。
- 建立字段白名单和错误脱敏，避免治理资产或本地环境泄露到浏览器。

**非目标：**

- 不实现 req/bug/sprint/opsx 命令在线执行。
- 不建设完整数据库事实源或历史数据迁移。
- 不重做 REQ-0012 的页面视觉体系、9 阶段定义或空间设置弹窗主体能力。
- 不新增移动端、微信小程序、桌面端或后台需求中心页面。

## 决策

### D1 数据接入策略

采用需求中心 BFF 聚合接口，而不是前端分别读取多个领域 API。

理由：
- 当前项目治理事实源分散在 `issues/`、`iterations/`、`openspec/changes/` 和文档 frontmatter 中，前端直接读取会暴露路径和安全边界。
- BFF 可以统一状态映射、字段白名单、权限判断、缓存和错误脱敏。
- 后续数据库索引出现后，可在 BFF 内替换数据来源，不破坏前端契约。

### D2 首版事实源

首版事实源采用治理文档、registry、OpenSpec 和 Sprint 文件聚合。

读取优先级：

```text
Issue trace.md
  > Issue _registry.yaml
  > Sprint 四件套
  > OpenSpec Change 元信息
  > 可推导默认值
```

出现冲突时不静默覆盖，返回对象级 `blocked` 或 `drift` 提示。

### D3 API 契约

首屏接口：

```text
GET /api/v1/requirement-center/context
```

访问约束：

- `/requirements` 是登录后页面，未登录用户先进入登录页，不渲染需求中心看板。
- context 接口必须携带有效 Bearer 会话；未登录返回 401，前端展示登录入口或无权限态，不长期显示加载占位。
- Docker 环境通过 `MOONBOX_GOVERNANCE_ROOT=/app/governance` 读取只读治理挂载，不依赖容器镜像内包含仓库根目录。
- 首版空间上下文仍不新增 Workspace 数据库边界；BFF 必须从 `MOONBOX_GOVERNANCE_ROOT/project.yaml` 派生当前项目空间，成员数由治理对象负责人和当前登录用户计算，空间角色由登录用户角色派生，不返回固定演示空间。

响应结构：

```yaml
current_user:
  name: string
  avatar_initial: string
  permissions: string[]
workspaces:
  - workspace_id: string
    organization_name: string
    name: string
    slug: string
    description: string
    timezone: string
    member_count: integer
    role: string
    permissions: string[]
selected_workspace:
  workspace_id: string
permissions:
  can_access_admin: boolean
  can_manage_workspace: boolean
  can_create_workspace: boolean
stats:
  total: integer
  requirements: integer
  bugs: integer
  blocked: integer
filters:
  owners: string[]
  priorities: string[]
  sprints: string[]
issues:
  - id: string
    type: requirement|bug
    title: string
    priority: string
    owner: string
    source: string
    stage: string
    documents: string[]
    updated_at: string
    blocked: string|null
    sprint_id: string|null
    change_id: string|null
    task_progress: [integer, integer]|null
    test_progress: [integer, integer]|null
    manual_acceptance_count: integer|null
    action:
      label: string
      command: string
```

### D4 UI Contract

事实源优先级：

| 来源 | 优先级 | 结论 |
|---|---:|---|
| `prototype/web/prototype.html` | 1 | 状态原型结构输入，定义状态容器和真实数据页面壳。 |
| `prototype/web/context.md` | 2 | 原型拆解事实源，定义页面清单、状态矩阵、数据依赖和 1440px 验收焦点。 |
| `acceptance.md` | 3 | 功能 AC、UI 状态 AC、AC-PROTOTYPE 和 AC-XCUT 事实源。 |
| REQ-0012 页面实现 | 4 | 作为既有页面骨架和视觉一致性事实源。 |
| `rules/ui-design.md` | 5 | 作为 MoonBox token、字体、近直角和原型驱动 UI Gate 规则。 |
| `openspec/specs/*` | 6 | 当前无已生效需求中心 spec，新增能力规格。 |

页面与入口：
- 路由保持 `/requirements`。
- 导航项“需求中心”继续高亮。
- 登录态和权限态由 BFF 返回的 `current_user` 和 `permissions` 控制。
- 版本 badge 使用 `PRODUCT_VERSION`，不得写死展示版本。

视觉与交互：
- 继续使用 REQ-0012 的深色默认主题、浅色主题、侧边栏、用户菜单、空间二级浮层、空间设置弹窗和 9 阶段看板结构。
- 新增状态反馈必须使用 MoonBox token，不引入大圆角卡片、蓝紫渐变或厚重阴影。
- 相同功能沿用已有图标和文案：进入后台、设置空间、切换空间、界面主题、退出登录。

权限规则：
- `can_access_admin=false` 时不渲染“进入后台”。
- `can_manage_workspace=false` 时隐藏或禁用“设置空间”，并提供无权限说明。
- `can_create_workspace=false` 时隐藏或禁用“创建或加入空间”。
- 只读用户可浏览有权限空间对象，但不得触发高风险动作。

Mock/API 边界：
- 生产运行时不得使用 `initialIssues`、`workspaces`、`currentUser`。
- 测试 fixture 可以保留在测试文件或测试 helper 中，但不得参与 production bundle 数据路径。
- 真实 API 覆盖用户、空间、权限、统计、筛选和 issues；空间首版来自项目治理元数据派生，不得返回硬编码演示空间；未实现命令执行动作时，卡片 action 只展示命令映射，不执行命令。

Computed style 验收点：
- 状态容器 `position`、`padding`、`border`、`background-color`、`color`。
- 统计 skeleton 高度和加载/完成状态布局稳定性。
- 错误态按钮、空态说明和无权限提示在深浅主题下的颜色对比。
- 9 阶段列宽、列头计数、卡片标题和 action 文案不重叠。

### D5 UI Skeleton

```text
RequirementCenterPage
  RequirementCenterShell
    FrontendSidebar
      UserMenu
      WorkspacePopover
      WorkspaceSettingsDialog
    RequirementCenterContent
      PageHeader
      StatsStrip
      FilterToolbar
      BoardStatusLayer
        LoadingState
        ErrorState
        ForbiddenState
        EmptyWorkspaceState
        EmptyFilterState
      KanbanBoard
        StageColumn x9
          IssueCard
```

状态容器：

| 状态 | 触发 | UI 表达 | 主操作 |
|---|---|---|---|
| loading | context 请求中 | 统计、筛选和列内 skeleton | 无 |
| loaded | context 成功且有对象 | 真实统计和真实卡片 | 阶段动作 |
| error | context 请求失败 | 脱敏错误说明 | 重试 |
| forbidden | 用户无空间访问权 | 无权限说明 | 返回默认入口或重新登录 |
| empty-workspace | 当前空间无对象 | 空空间提示 | 新建 Capture |
| empty-filter | 筛选后无结果 | 筛选空态 | 清空筛选 |
| drift-warning | 事实源状态冲突 | 卡片阻塞提示 | 查看 trace 或刷新 |

可测选择器：
- 页面标题：role heading，文本“需求研发流转看板”。
- 状态容器：`data-state="loading|error|empty-workspace|empty-filter|forbidden"`。
- 看板列：`data-stage` 覆盖 9 阶段。
- 卡片：`data-issue-id`。
- 用户菜单：role menu。
- 空间浮层：role dialog，label “切换空间”。
- 空间设置：role dialog，标题“空间设置”。
- 主题开关：唯一 `#themeSwitch`。
- Toast：role status。

### D6 Conflict Resolution

当前无阻断冲突。REQ-0013 原型是状态原型，不替代 REQ-0012 的完整页面视觉原型；实现时以 REQ-0012 已验收页面为视觉骨架，以 REQ-0013 prototype/context 为新增状态和数据边界输入。

最终验收以 Change design、delta spec、REQ acceptance、1440px/关键交互视觉证据、computed style、Mock/API 边界和 REQ 最终一致性回填共同为准。

## Risks / Trade-offs

- 文件事实源解析复杂 → 使用白名单字段、聚焦路径解析和状态映射单元测试降低风险。
- Sprint/Issue/Change 状态漂移 → 返回 `drift` 提示，并通过 Workflow Sync/validate-sprint-scope 维持机器事实源。
- BFF 读取文件可能变慢 → 首版限制读取范围，使用 registry 和 mtime 缓存；避免无界扫描 archive/generated/node_modules/dist/coverage。
- Docker 镜像缺少治理文件 → Compose 只读挂载治理事实源到 `/app/governance`，BFF 缺少 registry 时返回脱敏 503 并提示重试。
- 权限模型首版较轻 → BFF 返回最小可用 permissions，后续数据库权限模型出现后保持字段兼容。
- 真实数据接入破坏已验收 UI → UI Skeleton 先行，1440px 覆盖真实首屏、状态态和权限差异。

## Migration Plan

1. 新增后端 schema/service/API 与测试，保持接口只读。
2. 前端添加数据客户端和状态 hook，生产运行时切换到 BFF。
3. 保留测试 fixture，但移出生产数据路径。
4. 补齐 API 文档、OpenAPI 来源和安全测试。
5. 通过 1440px 视觉验收和 REQ 最终一致性回填后再归档。

回滚策略：保留页面结构，回滚前端数据 hook 到安全空态，不回滚到生产 Mock 数据。
