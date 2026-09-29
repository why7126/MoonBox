---
requirement_id: REQ-0032-requirement-center-sprint-dropdown-status
title: 需求中心 Sprint 下拉列表新增状态展示
terminal: web-catalog
version: v1
status: done
owner: product
source: capture.md
parent_requirement: REQ-0012-frontend-requirement-center
created_at: 2026-09-14 10:21:59
updated_at: 2026-09-17 08:31:36
priority: P2
---

# 需求中心 Sprint 下拉列表新增状态展示

## 1. 背景与价值

需求中心已有 Sprint 下拉选择能力，用于按迭代查看或筛选需求、缺陷和 Change 卡片。当前用户在下拉列表中只能依赖 Sprint 编号或名称判断目标迭代，无法直接区分规划中、进行中、已完成或已归档等状态，选择历史迭代或当前迭代时容易误判。

本需求在 Sprint 下拉选项中补充状态展示，帮助产品负责人、研发成员和验收人员快速识别迭代生命周期，减少切换错误，并保持需求中心既有筛选、默认选中和项目快照行为稳定。

## 2. 目标用户与目标

目标用户为使用需求中心查看迭代范围、需求卡片、缺陷卡片和 Change 交付状态的产品负责人、研发成员、测试/验收人员。

目标是在不重做需求中心筛选体系的前提下，让用户打开 Sprint 下拉列表时即可看到每个 Sprint 的可理解状态，并能稳定选择目标迭代。状态展示必须来自项目内 Sprint 生命周期事实源，不由前端临时编造。

## 3. 范围

### 3.1 首版包含

- 需求中心 Sprint 下拉列表的每个 Sprint 选项展示状态信息。
- 状态文案与项目 Sprint 生命周期一致，覆盖规划中、进行中、已完成、归档或状态待核实等可追溯表达。
- 当前选中项、默认选中项、搜索/筛选联动、项目切换后的下拉内容与状态展示保持一致。
- 状态缺失、未知或事实源冲突时提供稳定兜底展示，不阻断用户选择已有 Sprint。
- 深浅主题、窄屏、长 Sprint 名称和长状态组合下保持文本不溢出、不遮挡。

### 3.2 首版不包含

- 新增 Sprint 创建、编辑、启动、完成或归档操作。
- 重做需求中心筛选栏、卡片布局、统计口径或 Sprint 生命周期。
- 按状态分组、批量选择、多选筛选或高级搜索；如后续需要，单独评审。
- 新增独立的状态维护入口，或在前端保存与 Sprint 事实源不一致的状态。
- 自动修复 Sprint trace、sprint.yaml、CHANGELOG 或历史归档数据漂移。

## 4. 功能要求

### FR-001 状态事实源与映射

Sprint 下拉选项的状态必须来自后端或现有稳定快照中的 Sprint 生命周期事实源，优先使用 `sprint.yaml`、Workflow Sync 派生状态或现有 Sprint 列表接口中的结构化状态字段。

状态文案使用产品化中文表达：规划中、进行中、已完成、已归档、状态待核实。若底层状态字段为 `planning`、`in_progress`、`completed` 或归档目录事实，应映射到对应中文文案；无法识别、字段缺失或事实冲突时显示“状态待核实”，不得隐藏 Sprint 或编造正常状态。

### FR-002 下拉选项展示

每个 Sprint 选项展示 Sprint 标识/名称与状态信息。状态可采用轻量文本、标签或二者组合，视觉层级低于 Sprint 主名称，但需要一眼可读。

长 Sprint 名称、长编号或状态组合必须支持受控换行、省略或弹层宽度内布局，不得撑破筛选栏、遮挡其他选项或导致列表高度异常跳动。当前选中项展示也应保留状态提示，避免收起后丢失上下文。

### FR-003 选择、排序与默认行为兼容

新增状态展示不得改变用户选择 Sprint 的核心交互。用户点击某个 Sprint 选项后，应继续按现有逻辑刷新需求中心内容、卡片、统计和文档入口。

默认选中行为沿用既有需求中心规则。若当前迭代存在，应优先保持当前迭代的默认识别；若用户已手动选择其他 Sprint，刷新、筛选和项目切换后的保留策略沿用现有实现。新增状态信息不得导致默认项漂移。

排序默认沿用现有 Sprint 下拉顺序。若后续需要按状态分组或把当前迭代置顶，应在需求补全或评审阶段明确规则和验收，不在本草稿中默认扩大范围。

### FR-004 空态、异常与降级

当项目没有可展示 Sprint 时，下拉保持现有空态或禁用态，并给出稳定提示。该状态不应被误展示为“状态待核实”选项。

当某个 Sprint 缺少状态字段、状态非法、活动/归档事实冲突或快照解析失败时，仅该选项显示“状态待核实”或等价异常提示；列表整体仍可展示其余可用 Sprint。异常信息不得泄漏本机路径、内部文件路径、未授权项目内容或原始日志。

### FR-005 权限与项目边界

Sprint 状态展示复用需求中心现有项目绑定、空间成员权限、对象读取授权和稳定快照边界。用户只能看到当前授权项目内可见 Sprint 的状态，不得通过下拉选项、状态文案、搜索结果或数量差异推断其他项目或无权访问 Sprint。

项目切换、空间冻结、只读成员和授权失败时，下拉状态展示必须与既有需求中心权限反馈一致，不新增绕过授权的读取路径。

### FR-006 刷新与兼容性

需求中心刷新后，Sprint 状态应随稳定快照同步更新。Sprint 状态变化、归档迁移或 Workflow Sync 刷新后，用户重新打开下拉应看到新状态。

迟到响应不得覆盖当前项目的下拉选项。已有 Sprint 选项字段保持向后兼容；旧数据缺少状态时按异常降级展示，不造成页面崩溃。

## 5. UI 约束

沿用需求中心现有筛选栏、下拉组件、字体 token、近直角细边框和深浅主题。状态信息使用低噪音视觉，不引入大面积高饱和颜色、营销式胶囊或新的卡片结构。

状态标签或文本应与 MoonBox Ops 视觉系统一致：字号小于或等于 Sprint 主名称，颜色具备足够对比度，状态色只作辅助，不作为唯一识别方式。键盘导航、hover、focus、选中态、禁用态和滚动列表均需保持可达。

若后续在 `/req-complete` 阶段补充 prototype 或 UI Skeleton，需要覆盖 1440px 桌面、窄屏、深浅主题、长 Sprint 名称、状态缺失和项目切换场景。

## 6. 关联需求

- REQ-0012-frontend-requirement-center：本需求是需求中心筛选体验的局部增强，复用其页面入口、项目范围和卡片刷新机制。
- REQ-0022-local-project-import-product-iteration：复用项目绑定、稳定快照和迭代数据读取边界。
- REQ-0026-requirement-center-standalone-change-cards：保持需求中心卡片、Change 追溯和 Sprint 标签展示的整体一致性。
- REQ-0030-requirement-center-sprint-completion-metrics、REQ-0031-requirement-center-current-iteration-capacity：同属需求中心迭代信息增强，后续补全时需避免状态、完成度和容量口径互相混淆。

## 7. 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
  reason: 本需求改变需求中心 Sprint 下拉展示与筛选选择体验，可能复用或扩展 Sprint 列表查询；需要保留用户选择、请求结果和异常降级的可排障链路。首版不新增长耗时、多步骤任务，不预期接入 task_traces 或 task_trace_spans。
  validation: 后续实现需验证 Sprint 下拉打开、选择、项目切换和异常降级时的行为事件安全摘要、请求日志 request_id、授权拒绝与状态缺失场景；不得记录完整响应体、本机路径、密钥或未授权对象内容。
```

## 8. 验收要点

- AC-001：Sprint 下拉列表中每个可见 Sprint 都展示可理解状态，状态来自可追溯事实源。
- AC-002：planning、in_progress、completed 和归档事实能映射为中文状态；未知、缺失或冲突状态稳定降级为“状态待核实”。
- AC-003：新增状态展示不改变默认选中、手动选择、刷新、项目切换、搜索/筛选联动和卡片统计的既有行为。
- AC-004：长 Sprint 名称、长编号、多状态混合、深浅主题、窄屏和键盘操作下，下拉内容不溢出、不遮挡、可读可选。
- AC-005：无 Sprint、授权失败、只读成员、冻结空间和状态解析失败时有安全反馈，不暴露内部路径、日志或无权对象。
- AC-006：如实现涉及接口字段、OpenAPI 或客户端类型，需同步 API 文档、类型生成和请求日志验证；如确认复用既有字段，则在 Change 中记录不新增 API/DB 的依据。

## 9. 当前状态

```yaml
status: done
lifecycle_stage: review
iteration: sprint-006
openspec_changes:
  - change_id: add-requirement-center-sprint-dropdown-status
    type: update
    status: archived
next: closed
```

本需求已纳入 sprint-006，并已创建 OpenSpec Change，可进入实现。默认状态呈现形态为“文本 + 轻量标签”，不默认按状态分组或置顶当前迭代；现有 Sprint 列表接口是否已提供稳定状态字段将在实现阶段核实。
