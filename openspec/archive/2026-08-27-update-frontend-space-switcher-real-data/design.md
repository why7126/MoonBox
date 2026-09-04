## 背景

REQ-0012 已提供前台需求中心和用户菜单空间切换 UI；REQ-0013 将需求中心接入真实治理数据，但空间列表仍首版从 `MOONBOX_GOVERNANCE_ROOT/project.yaml` 派生单个项目治理空间。REQ-0017 已完成后台空间管理模块，具备 `admin_spaces`、`admin_space_members`、`admin_space_products` 等真实空间事实源。

本 Change 将 REQ-0018 的文档包转为实现合同：前台空间切换列表只展示当前用户已加入的后台真实空间，冻结空间可切换查看但保留只读提示，回收中空间默认隐藏，创建/加入流程继续由 REQ-0019 承接。

## 目标 / 非目标

**Goals:**

- 后端返回当前用户已加入的真实空间列表，并过滤未加入、无权限和回收中空间。
- 前端空间切换浮层展示真实空间名称、角色、成员数、当前项和冻结/只读标记。
- 最近选择必须经过接口返回列表校验；失效时回退默认空间或空态。
- 切换空间后同步用户区空间名称、浮层当前项、需求中心上下文、统计、筛选和看板数据。
- 明确 UI Contract、UI Skeleton、Mock/API 边界和 1440px 验收点。

**Non-Goals:**

- 不实现创建空间、加入空间申请、审批、撤回或重提；这些由 REQ-0019 处理。
- 不新增后台空间管理操作，不修改配额、续期、成员管理、负责人移交或审计详情。
- 不支持可申请加入空间搜索、推荐列表、一空间多产品或跨空间迁移。
- 不用前端隐藏替代服务端冻结状态和权限校验。

## 设计决策

### D1. 使用需求中心 BFF 承载前台空间上下文

需求中心已有 `/api/v1/requirement-center/context` 聚合接口，前端空间切换也已消费其 `workspaces` 字段。本 Change 优先在该 BFF 中替换空间来源，而不是让普通前台用户调用 `/api/v1/admin/spaces`。

原因：

- 避免暴露后台全量空间、配额、审计、删除原因和高风险操作集合。
- 保持前端数据入口稳定，降低 UI 重构范围。
- 便于同时返回 `selected_workspace_id`、当前用户权限、只读语义和治理对象过滤结果。

备选：新增独立 `/api/v1/frontend/spaces`。可作为后续拆分，但当前 BFF 已是需求中心页面上下文事实源，先复用更稳。

### D2. 空间可见性以后台成员关系为准

后端空间列表只返回当前用户作为负责人或成员加入的空间。回收中空间默认不返回；冻结空间返回但标记 `readonly` 或等价只读字段。

字段白名单：

- `workspace_id` / `id`
- `name`
- `slug` / `code`
- `description` 可选
- `member_count`
- `role`
- `status`
- `readonly`

不得返回：

- 后台配额详情
- 审计记录
- 删除原因
- 负责人内部 ID
- 高风险 allowed actions
- 原始数据库错误、堆栈、本机路径或 `.env` 内容

### D3. 本地最近选择只作为候选，不作为事实源

前端读取 `moonbox.workspace` 后必须与接口返回的 `workspaces[]` 对比。命中且可访问时作为当前空间；未命中时覆盖本地缓存并回退接口默认空间或首个空间。无可访问空间时展示空态，不显示 Mock 空间。

### D4. 冻结空间可查看但只读

冻结空间保留在列表中，用户可切换查看。UI 使用低干扰的“已冻结”或“只读”标记；当前上下文保留只读语义，后续写入、Agent 执行或其他受限能力仍由服务端按空间状态拒绝。

## UI Contract

### 事实源优先级

1. `issues/requirements/review/REQ-0018-frontend-space-switcher-real-data/prototype/web/prototype.html`
2. `issues/requirements/review/REQ-0018-frontend-space-switcher-real-data/prototype/web/context.md`
3. `issues/requirements/review/REQ-0018-frontend-space-switcher-real-data/acceptance.md`
4. `rules/ui-design.md`
5. `openspec/specs/web-catalog-requirement-center-real-data/spec.md`
6. `openspec/specs/web-catalog-requirement-center/spec.md`

如发生冲突，优先保留 REQ-0018 对真实数据、可见性、冻结只读和安全边界的约束；视觉密度和交互方式继续服从 REQ-0012 既有用户菜单。

### 页面与入口

- 页面：前台需求中心。
- 入口：侧边栏底部用户菜单中的“切换空间”。
- 结构：一级用户菜单右侧轻量二级浮层，不新增全屏遮罩、复杂搜索或组织分组。

### 视觉与组件

- 空间项为紧凑列表行，名称为主信息，角色/成员数/状态为辅助信息。
- 当前空间使用勾选图标，不使用重色块或大面积高亮。
- 冻结/只读标记必须在深浅主题可读，不与当前项勾选冲突。
- 浮层不得被看板列、页面滚动容器或侧边栏 overflow 裁剪。
- 文本过长时截断或换行，不挤压勾选图标和状态标记。

### 交互状态

- loading：展示轻量加载占位，不闪现 Mock 空间。
- active-space：可切换。
- frozen-space：可切换查看，展示只读标记。
- empty：无已加入空间时展示空态和“创建或加入空间”入口。
- error：展示脱敏错误态和重试/重新登录提示。
- stale-local：本地空间失效时不闪现旧空间，直接回退。
- close：点击外部、Escape、选择空间、侧边栏收起时关闭浮层。

### Mock/API 边界

- prototype HTML 为静态结构原型，不能作为生产运行时数据。
- 实现必须接入真实 BFF 或前台空间接口。
- “创建或加入空间”入口只保留位置，流程由 REQ-0019 实现。

### Computed Style 验收点

实现阶段至少记录或断言：

- 空间浮层 `position`、`z-index`、`width`、`overflow`
- 空间行 `min-height`、`padding`、`gap`
- 冻结标记 `color`、`border-color`、`font-size`
- 当前勾选图标可见性
- 深浅主题下浮层背景、边框和文字对比

## UI Skeleton

### 页面结构

```text
RequirementCenterPage
  └─ Sidebar
      └─ UserZone
          ├─ UserMenu
          │   └─ SpaceSwitcherTrigger
          └─ SpacePopover
              ├─ LoadingState
              ├─ SpaceList
              │   └─ SpaceOption[]
              ├─ EmptyState
              ├─ ErrorState
              └─ CreateOrJoinEntry
```

### 状态容器

- `data-testid="space-switcher-popover"` 或等价稳定选择器。
- 正常空间、冻结空间、当前空间、无空间、加载、错误各有可测状态。
- 当前空间选择与本地缓存校验逻辑独立封装，避免 UI 渲染直接信任 localStorage。

### 1440px 验收焦点

- 一级菜单和二级浮层同时可见。
- 空间列表三类状态：正常、冻结/只读、当前项。
- 无空间空态和接口错误态不撑开一级用户菜单。
- 切换空间后用户区空间名称同步更新。

## 冲突处理

| 来源 | 冲突点 | 处理 |
|---|---|---|
| `web-catalog-requirement-center-real-data` 现行 spec | 首版空间来自项目治理元数据 | 本 Change 修改为空间来自后台空间事实源；项目治理元数据只可作为无后台空间数据时的非生产兼容兜底，生产路径不得冒充真实空间 |
| `web-catalog-requirement-center` 现行 spec | 空间列表已存在创建或加入入口 | 保留入口位置，流程实现仍归 REQ-0019 |
| prototype HTML | 静态空间示例 | 仅作为结构和状态表达，生产数据必须来自接口 |

## 风险与权衡

- [Risk] 当前 BFF 可能没有空间成员查询 helper。→ Mitigation：优先在后端 repository/service 层增加前台可见空间查询，复用已有后台空间表结构和头像/用户归一化工具。
- [Risk] `REQ-0018` 与 `REQ-0019` 同在 sprint-003，入口与流程容易混边界。→ Mitigation：本 Change 只保留入口和空态文案，不实现申请提交。
- [Risk] 需求中心治理对象暂未全部具备空间归属字段。→ Mitigation：先保证空间摘要和权限态真实；若对象可归属则过滤，否则在文档和测试中声明项目级聚合暂存边界。
- [Risk] 冻结空间只读若仅前端处理会绕过。→ Mitigation：服务端状态校验作为 AC 和测试门禁。

## 迁移计划

1. 先完成 UI Skeleton 和状态容器，确认浮层结构不偏离 REQ-0012。
2. 后端替换 BFF `workspaces` 数据源并增加字段白名单。
3. 前端接入真实字段、最近选择校验和冻结/空态/错误态。
4. 补齐后端、前端和 1440px 视觉验收。
5. 同步 API 文档、OpenAPI 来源和相关安全测试。

## 开放问题

无阻塞问题。若实现中发现治理对象需要按空间过滤但缺少空间归属字段，应作为实现边界记录，不在本 Change 中扩展创建/加入流程。
