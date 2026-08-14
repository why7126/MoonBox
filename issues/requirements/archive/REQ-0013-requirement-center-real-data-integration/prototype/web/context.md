---
requirement_id: REQ-0013-requirement-center-real-data-integration
title: 需求中心真实数据接入状态原型
status: draft
created_at: 2026-08-10 21:53:16
updated_at: 2026-08-10 21:53:16
---

# 原型上下文

## 页面清单

| 页面 | 路由 | 说明 |
|---|---|---|
| 需求中心 | `/requirements` | 在 REQ-0012 页面骨架上替换真实数据，并新增加载、错误、空态、无权限态和刷新反馈。 |

## 关键区域

| 区域 | 状态要求 |
|---|---|
| 侧边栏 | 继续使用 REQ-0012 前台侧边栏；不因数据加载而跳动。 |
| 用户区 | 用户姓名、头像、当前空间和权限入口来自 BFF。 |
| 统计区 | 加载中展示 skeleton；成功后展示真实统计；错误时不展示过期 Mock 数字。 |
| 筛选工具栏 | 选项来自真实数据；加载中禁用；失败后提供重试或保留安全空值。 |
| 9 阶段看板 | 始终保留 9 列；对象卡片来自真实数据；空列显示 00。 |
| 状态反馈 | 加载、错误、空空间、筛选无结果、无权限、事实源漂移均有独立表达。 |

## 组件层级

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
        EmptyWorkspaceState
        EmptyFilterState
      KanbanBoard
        StageColumn x9
          IssueCard
```

## 状态矩阵

| 状态 | 触发 | UI 表达 | 主操作 |
|---|---|---|---|
| loading | context 请求中 | 统计、筛选和列内 skeleton | 无 |
| loaded | context 成功且有对象 | 真实统计和真实卡片 | 阶段动作 |
| error | context 请求失败 | 错误说明，不暴露内部信息 | 重试 |
| forbidden | 当前用户无空间访问权 | 无权限说明 | 返回默认入口或重新登录 |
| empty-workspace | 当前空间无对象 | 空空间提示 | 新建 Capture |
| empty-filter | 筛选后无结果 | 筛选空态 | 清空筛选 |
| drift-warning | 事实源状态冲突 | 卡片阻塞提示 | 查看 trace 或刷新 |

## 交互触发

- 进入页面时自动请求 context。
- 点击重试重新请求 context。
- 切换空间后重新请求 context。
- 保存空间设置成功后重新请求 context。
- 修改筛选和搜索时基于当前 context 过滤并重算统计。
- 本地保存空间不可访问时回退到默认空间并更新本地缓存。

## 数据依赖

```yaml
api:
  context: GET /api/v1/requirement-center/context
  optional_issues: GET /api/v1/requirement-center/issues
fields:
  current_user:
    - name
    - avatar_initial
    - permissions
  workspaces:
    - workspace_id
    - organization_name
    - name
    - slug
    - description
    - timezone
    - member_count
    - role
    - permissions
  issues:
    - id
    - type
    - title
    - priority
    - owner
    - source
    - stage
    - documents
    - updated_at
    - blocked
    - sprint_id
    - change_id
    - task_progress
    - test_progress
    - manual_acceptance_count
```

## 响应式断点

| 断点 | 要求 |
|---|---|
| 1440px desktop | 首要验收视口；统计、筛选和 9 阶段横向看板必须稳定。 |
| 1024px tablet | 侧边栏可收起；筛选工具栏允许换行；看板横向滚动。 |
| 375px mobile | 不作为首版重点，但文本不得溢出，状态反馈可纵向堆叠。 |

## 1440px 验收焦点

- loading 到 loaded 不产生明显布局跳动。
- 错误态、空态、筛选无结果态保留页面骨架和 9 阶段列边界。
- 真实长标题、长负责人、长文档产物不遮挡卡片主动作。
- 无权限用户不出现“进入后台”和“设置空间”等高权限入口。
- 空间切换后用户区空间名、统计和卡片数据同步刷新。
- 深色与浅色主题下状态反馈可读。

## PNG 策略

当前阶段仅要求结构与状态拆解；PNG 视觉证据在 `/opsx-apply` 1440px 验收时产出。
