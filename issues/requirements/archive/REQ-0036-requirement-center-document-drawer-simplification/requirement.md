---
requirement_id: REQ-0036-requirement-center-document-drawer-simplification
title: 需求中心文档抽屉简化与 Change 属性模块移除
terminal: web-catalog
version: v1
status: done
owner: product
source: capture.md
parent_requirement: REQ-0026-requirement-center-standalone-change-cards
created_at: 2026-09-15 23:08:23
updated_at: 2026-09-17 08:35:51
priority: P2
---

# 需求中心文档抽屉简化与 Change 属性模块移除

## 1. 背景与价值

需求中心右侧文档抽屉当前在正文前展示“Change 追溯属性”模块。该模块混合了 Change 状态、任务进度、关联文档和告警信息，但用户打开文档抽屉时的核心任务是阅读当前文档的属性与正文。独立 Change 仅显示任务进度时信息价值有限，多 Change 场景又容易把不同 Change 的 trace、proposal 或任务进度和当前文档阅读混在一起。

用户已明确要求直接删除整个 Change 属性模块。该需求作为 REQ-0026 的体验 refinement：保留父需求已经建立的 Change 可见性、关联关系、阶段、任务进度、告警和文档可达性事实，但不再把这些治理追溯信息放在文档抽屉顶部。

成功标准：REQ、BUG 和独立 Change 的文档抽屉只保留文档属性与正文；删除模块后不出现空白占位、贴边文本或重复分隔；多 Change 关联及 Change 文档仍可通过抽屉外紧凑入口到达，不在卡片上展开完整 Change ID；Issue 自身文档与关联 Change 文档合并时按文件名和语义去重，不默认选择第一个 Change，不混淆 Issue trace 与 Change trace。

## 2. 目标用户与目标

目标用户是使用需求中心阅读需求、缺陷和 Change 文档的产品负责人、研发成员与验收人员。

目标：

- 降低文档抽屉的阅读干扰，让用户优先看到当前文档的属性与正文。
- 删除“Change 追溯属性”整块 UI，不把该模块迁移为抽屉内的新折叠区。
- 保留底层 Change 关联、阶段、任务进度、告警和文档入口能力，避免多 Change 场景丢失追溯入口。
- 延续现有权限、只读、编辑、脏数据保护和文档读取约束。

## 3. 范围

### 3.1 首版包含

- 删除需求中心右侧文档抽屉中的“Change 追溯属性”模块。
- REQ、BUG 和独立 Change 文档抽屉统一只展示文档属性、正文、加载态、错误态、关闭/展开等既有文档阅读能力。
- 文档属性模块继续使用当前统一样式、展开/收起和可访问性语义。
- 保留底层 `current_change`、`related_changes`、Change 阶段、任务进度、告警和 `document_entries` 数据，不因抽屉模块删除而破坏其他入口。
- 多 Change 关联及 Change 文档必须在抽屉外仍可达；优先复用卡片直接紧凑文档入口、详情或既有文档入口，不新增抽屉内替代模块，不在卡片上展开完整 Change ID；合并展示时按文件名和语义去重。
- 继续区分 Issue trace 与 Change trace，用户打开某个 Change 文档时必须能辨认其归属。

### 3.2 首版不包含

- 不新增独立 Change 编辑、任务勾选、阶段流转或归档执行能力。
- 不重做需求中心卡片布局、阶段列、统计口径或搜索体系。
- 不删除 Change 数据、trace、proposal、design、tasks 或历史归档文档。
- 不改变 REQ/BUG 与 Change 的关联识别、授权、阶段映射、任务完成语义。
- 不在文档抽屉内新增“关联 Change”“追溯信息”“任务进度”等替代面板。

## 4. 功能要求

### FR-001 删除抽屉 Change 属性模块

需求中心文档抽屉在任意对象类型下均不得渲染“Change 追溯属性”模块，包括模块标题、边框、左侧色条、任务进度文案、告警分隔符、关联 Change 列表和 Change 文档按钮。

删除后，文档属性模块应直接成为抽屉正文前的唯一属性区块。若当前文档没有可展示的文档属性，抽屉不得保留来自 Change 属性模块的空白占位。

### FR-002 保留文档属性与正文阅读

文档抽屉继续保留当前文档的文档属性、正文、加载态、错误态、空态、关闭、全屏或展开能力。文档属性的展开/收起按钮、间距、边框、文本对齐、键盘可达性和屏幕阅读语义不能因删除 Change 模块而退化。

正文阅读区域应在删除模块后自然上移，滚动容器高度、顶部间距和分隔线不应出现残留断层。

### FR-003 保留 Change 关联与文档可达性

删除抽屉模块不代表删除 Change 追溯数据。系统仍需保留并正确使用 `current_change`、`related_changes`、`task_progress`、`warnings`、`drift_warnings` 和 `document_entries` 等事实，用于卡片、详情或其他抽屉外入口。

若 REQ/BUG 关联多个 Change，用户必须能从需求中心通过紧凑文档入口辨认并打开可读文档。Issue 自身文档与关联 Change 文档合并展示时，`proposal.md`、`spec.md`、`design.md`、`tasks.md`、`sprint.md` 等非 trace 同名文档按文件名和语义去重；Change trace 以短文案保留独立入口。入口不得在卡片上展开完整 Change ID，不得任意默认选择第一个 Change，不得把多个 Change 的任务进度汇总成单个 Change 的进度。

### FR-004 独立 Change 文档行为

独立 Change 打开文档抽屉时，也不显示“Change 追溯属性”模块。其任务进度、状态和告警可在卡片、阶段区域或详情入口中呈现，但不得重新塞回文档抽屉顶部。

独立 Change 的 proposal、design、tasks、trace 等文档入口继续按现有授权和可用性规则打开。缺失文档仍使用现有缺失提示，不自动生成文件。

### FR-005 权限与安全

本需求复用现有空间成员、项目绑定、对象读取授权、只读权限和冻结空间策略。删除 UI 模块不能放宽文档 API 的访问限制，也不能让无权用户通过入口、搜索、文档 URL 或错误提示获得受限 Change 内容。

文档读取仍必须属于当前项目和当前授权对象。跨项目同 ID、路径越界、符号链接越界和伪造文档 URL 均不得绕过授权。

### FR-006 兼容与回归

删除模块后，需求中心既有 REQ/BUG 卡片、独立 Change 卡片、文档按钮、编辑草稿保护、只读提示、阶段按钮、筛选、搜索和刷新行为保持兼容。

已有测试若仅验证抽屉内 Change 属性模块，应调整为验证模块不存在，以及验证 Change 文档仍可通过抽屉外入口到达。不得用“模块仍能显示”作为回归标准。

## 5. UI 约束

文档抽屉采用简化结构：

```text
抽屉标题区
文档属性
正文
```

不得在文档属性之前或之后保留 Change 属性模块残影。文档属性区块继续使用现有设计 token 和组件样式，模块删除后需要在 1440px 与窄视口验证顶部间距、边框、圆角、滚动、深浅主题和长文档阅读。

若实现需要承接多 Change 入口，入口必须位于文档抽屉外，例如卡片直接紧凑文档入口、详情页或已有文档分组区域；该入口应保持紧凑，只负责到达关联 Change 文档，不在卡片上展开完整 Change ID，也不在文档抽屉内复制原模块。

## 6. 验收要点

- AC-001：REQ、BUG 和独立 Change 的文档抽屉均不再出现“Change 追溯属性”标题、任务进度文案、关联 Change 列表或模块边框。
- AC-002：文档属性和正文正常展示；展开/收起、滚动、关闭、全屏或展开状态无视觉断层。
- AC-003：关联一个 Change 的 REQ/BUG 仍能打开该 Change 的可读文档；关联多个 Change 时，文档入口通过紧凑入口可辨认且不会串读，卡片不展开完整 Change ID；同名 proposal/spec/design/tasks/sprint 不重复出现，Issue trace 与 Change trace 可区分。
- AC-004：独立 Change 的 proposal、design、tasks 和 trace 等文档入口继续可用；只读、编辑、缺失文档和草稿保护行为不回归。
- AC-005：权限回归覆盖无权对象、只读成员、冻结空间、跨项目同 ID 和直接文档 URL，不能因模块删除暴露受限内容。
- AC-006：1440px 与窄视口、深浅主题、长标题、长 ID 和长正文均具有截图或 computed style 证据。

## 7. 影响层与数据采集观测

依据 `docs/standards/product-data-collection-observability.md`：

```yaml
product_data_collection_observability:
  status: not_applicable
  affected_layers:
    - web
  reason: 本需求只调整需求中心前端文档抽屉的信息展示与入口组织，计划复用现有文档读取、权限、请求封装、日志审计和行为采集链路；不新增或修改 API、DB、请求日志字段、行为事件、Task Trace、对象存储或客户端请求封装。
  validation: 实施阶段验证模块已删除、文档读取和权限回归通过；若后续为了承接入口新增 API 字段、埋点或请求封装变化，需重新评估为 applicable 并补充观测验收。
```

影响层为 Web UI。API、DB、部署、对象存储、安全策略和客户端生成预期不变；若实现证明需要改变接口或授权返回字段，必须在进入 OpenSpec 前补充范围与验收。

## 8. 关联需求与交付边界

- REQ-0026-requirement-center-standalone-change-cards：本需求是其体验 refinement，保留 Change 可见性与关联追溯事实，调整文档抽屉承载方式。
- REQ-0020-requirement-center-card-document-actions-ai-chat：复用既有文档阅读、文档按钮、草稿保护和权限边界。

本需求不改变父需求已交付状态，不从草稿直接开发。后续按 req-complete、req-review、sprint-propose、req-opsx 顺序推进。

## 9. 当前状态

```yaml
status: done
lifecycle_stage: review
iteration: sprint-007
openspec_changes:
  - remove-requirement-center-document-drawer-change-attributes
```

当前已评审通过，等待纳入 Sprint；未创建 OpenSpec Change。
