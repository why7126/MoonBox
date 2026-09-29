---
change_id: remove-requirement-center-document-drawer-change-attributes
title: 需求中心文档抽屉移除 Change 属性模块 - 设计
status: proposed
created_at: 2026-09-15 23:32:00
updated_at: 2026-09-16 08:45:49
---

# 需求中心文档抽屉移除 Change 属性模块 - 设计

## 背景与现状

当前需求中心文档抽屉复用文档属性面板样式渲染“Change 追溯属性”模块。该模块包含独立 Change 的任务进度、关联 Change 的阶段/进度/告警和 Change 文档按钮。它解决了追溯入口问题，但占用了文档阅读首屏，并且和“文档属性”在信息架构上混在一起。

REQ-0036 的最终产品决策是直接删除整个抽屉内 Change 属性模块。Change 关联、任务进度、告警和文档入口仍是有效事实，但必须通过抽屉外入口承接。

## 目标

- 文档抽屉只承担当前文档阅读：标题区、文档属性区、正文区。
- 删除“Change 追溯属性”模块，不保留标题、边框、左侧色条、任务进度、告警分隔符、关联 Change 列表和 Change 文档按钮。
- 保留单 Change、多 Change 和独立 Change 的文档可达性，不默认选择第一个 Change。
- 不扩大文档读取、编辑、只读或 URL 授权边界。
- 以最小实现影响完成体验收敛，不修改 DB、API、OpenAPI、Orval、对象存储或部署拓扑。

## 非目标

- 不新增独立 Change 创建、编辑、任务勾选、阶段流转或归档执行能力。
- 不重做需求中心卡片布局、阶段列、筛选、搜索或统计口径。
- 不删除 Change 数据、trace、proposal、design、tasks 或历史归档文档。
- 不把“Change 追溯属性”改名后放回抽屉内。

## 设计方案

### D1：直接移除抽屉内 Change 属性渲染分支

从右侧 Markdown 文档抽屉渲染逻辑中删除“Change 追溯属性”模块的条件渲染分支。删除范围包括模块标题、容器、独立 Change 任务进度文案、关联 Change 列表、告警拼接和模块内 Change 文档按钮。

删除后，文档属性区成为正文前唯一属性区块。文档属性为空时，也不得保留来自 Change 模块的空白占位。

### D2：保留抽屉外 Change 文档入口

`related_changes`、`current_change`、`document_entries`、`task_progress`、`warnings` 和 `drift_warnings` 继续作为需求中心卡片、详情或既有文档分组的事实来源。实现不得因为删除抽屉模块而删除这些字段或后端聚合逻辑。

多 Change 场景必须避免“默认第一项”。抽屉外入口应保持紧凑，优先使用直接紧凑文档入口承接，不在卡片上展开完整 Change ID。用户点击对应紧凑文档入口后，打开对应 Change 文档。Issue 自身文档与关联 Change 文档合并展示时，非 `trace.md` 文档按文件名和语义去重，`proposal.md`、`spec.md`、`design.md`、`tasks.md`、`sprint.md` 不重复出现；Issue trace 保持 `trace.md`，Change trace 使用 `Change trace.md` 或等价上下文区分。

### D3：样式收敛与回归

删除模块后不新增替代样式。重点检查文档属性区的顶部间距、边框、圆角、左侧强调线、展开/收起按钮、正文起始位置和滚动容器高度。已有 `.rc-markdown-frontmatter-panel` 和 `.rc-markdown-frontmatter-toggle` 仍作为文档属性事实源。

## UI Contract

| 项 | 合同 |
|---|---|
| 事实源优先级 | `prototype/web/prototype.html` > `prototype/web/context.md` > `acceptance.md` > `requirement.md` > `rules/ui-design.md` > 既有需求中心规格 |
| 页面与入口 | 前台需求中心卡片文档入口打开右侧 Markdown 抽屉；关联 Change 文档通过卡片内直接紧凑文档入口、详情或既有文档分组等抽屉外入口打开；同名文档合并展示时按文件名和语义去重 |
| 信息架构 | 抽屉标题区、文档属性区、正文区；不得出现 Change 属性模块或等价追溯面板 |
| 视觉 token | 沿用 MoonBox Ops token：深浅主题、近直角、细边框、金色强调、工作型阅读密度 |
| 交互状态 | 文档属性展开/收起、关闭、全屏/恢复、加载、错误、只读、脏数据保护保持既有行为 |
| 图标与文案 | 用户可见模块文案仅保留“文档属性”；不得展示“Change 追溯属性” |
| Mock/API 边界 | 使用既有 API 和授权数据；本 Change 不新增 Mock，不新增 API 字段 |
| 权限规则 | 文档读取、编辑、只读、冻结空间、跨项目同 ID 和直接文档 URL 复用现有授权 |
| 一致性参照 | 对齐现有需求中心右侧抽屉、REQ-0026 Change 可见性和 REQ-0020 文档阅读能力 |

## UI Skeleton

```text
需求中心页面
  ├─ 卡片/详情/既有文档分组入口
  │    └─ 紧凑 Change 文档入口：直接紧凑文档入口，不展开完整 Change ID
  └─ Markdown 文档抽屉
       ├─ 抽屉标题区：对象 ID、文档名、标题、关闭/全屏
       ├─ 文档属性区：只读 frontmatter，默认收起，可展开
       └─ 正文阅读区：Markdown 阅读态或受控编辑态
```

Skeleton 验收：

- 默认、加载、错误、只读、可编辑 capture、独立 Change、多 Change 关联均不得渲染 Change 属性模块。
- 1440px 基准视口下，文档属性区与正文之间没有残留间距或分隔断层。
- 窄视口下，文档属性折叠、关闭/展开和正文阅读可操作。

## Conflict Resolution

| 事实源 | 冲突处理 |
|---|---|
| `prototype.html` | 作为目标结构：标题区、文档属性、正文；无 Change 属性模块 |
| `context.md` | 明确抽屉外 Change 文档入口承接；实现不得在抽屉内重建同类模块 |
| `acceptance.md` | 功能 AC 和 AC-PROTOTYPE 是实现验收门禁 |
| 既有规格 | 保留文档属性、只读/编辑、权限和文档入口能力；删除 Change 属性模块为本次 delta |
| 现有实现 | 代码可保留后端 Change 数据，但 UI 抽屉分支必须删除 |

## 数据与 API

```yaml
product_data_collection_observability:
  status: not_applicable
  affected_layers:
    - web
  reason: 本 Change 只调整需求中心 Web 文档抽屉展示与入口组织，计划复用现有文档读取、权限、请求封装、日志审计、行为采集、Task Trace 和对象存储链路；不新增或修改 API、DB、请求日志字段、行为事件、Task Trace、对象存储或客户端请求封装。
  validation: 实施阶段验证模块已删除、文档读取和权限回归通过；若实现中新增 API 字段、埋点或请求封装变化，需重新评估为 applicable 并补充 OpenAPI、Orval、API 文档和测试影响。
```

API、DB、部署、对象存储、安全策略和客户端生成预期不变。

## 风险

| 风险 | 处置 |
|---|---|
| 删除模块后多 Change 文档入口不可达或卡片过长 | 保留并回归抽屉外紧凑入口；测试单 Change、多 Change、独立 Change 文档打开以及卡片不展开完整 Change ID |
| UI 删除后留下残留间距或断层 | 采集 1440px、窄视口截图和 computed style 证据 |
| 权限边界被入口调整放宽 | 回归无权对象、只读成员、冻结空间、跨项目同 ID 和直接文档 URL |
| 有效告警信息完全不可见 | 本 Change 不删除底层 warnings；只要求不在文档抽屉内展示 |

## 回滚方案

若删除导致文档入口不可达或权限回归失败，回滚前端抽屉渲染改动，保留后端数据与既有文档入口；不得通过恢复抽屉内 Change 属性模块绕过入口修复。
