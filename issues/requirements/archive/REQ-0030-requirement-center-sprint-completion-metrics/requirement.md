---
requirement_id: REQ-0030-requirement-center-sprint-completion-metrics
title: 需求中心指标卡新增 Sprint 已完成与累计数量
terminal: web-catalog
version: v1
status: done
owner: product
source: capture.md
parent_requirement: REQ-0012-frontend-requirement-center
created_at: 2026-09-14 10:21:15
updated_at: 2026-09-17 08:31:00
priority: P1
---

# 需求中心指标卡新增 Sprint 已完成与累计数量

## 背景

需求中心已承接 REQ、BUG、Sprint 与 OpenSpec Change 的研发治理看板能力，当前顶部指标卡主要帮助用户理解需求、缺陷、阻塞和阶段分布。随着 Sprint 治理流程完善，产品负责人需要在进入需求中心时快速判断项目迭代沉淀情况：已经闭环多少个 Sprint，以及项目历史上累计规划过多少个 Sprint。

用户本次反馈“指标卡新增 Sprint 数量 已完成/累计数”，并在验收返修中确认展示文案调整为“已完成/总体”。该指标应使用 Sprint 生命周期事实源计算，避免仅按当前看板卡片、前端筛选结果或局部 Mock 数据推导，导致统计口径漂移。

## 目标用户

- 产品负责人：需要快速了解当前项目已经完成的 Sprint 数量和累计 Sprint 数量。
- 项目负责人：需要在需求中心首页评估迭代交付节奏和历史规划规模。
- 开发与测试协作者：需要通过 Sprint 总览指标理解当前看板所处的迭代上下文。

## 范围

### 包含

- 在需求中心顶部或既有指标卡区域新增 Sprint 数量统计。
- 指标展示已完成 Sprint 数与总体 Sprint 数，文案建议为“已完成 / 总体”。
- 所有指标名后展示统一信息图标，鼠标悬停或键盘聚焦时通过项目内统一浮层 tooltip 展示统计口径。
- 需求、Bug 与独立 Change 指标展示“已完成 / 总体”，并继续跟随当前筛选条件变化。
- 已完成 Sprint 默认统计已进入 `iterations/archive/` 的 Sprint；若系统保留 `status: completed` 但尚未物理归档的兼容状态，应在聚合逻辑中明确处理并避免重复计数。
- 累计 Sprint 统计所有可识别的有效 Sprint，包括 `iterations/change/` 与 `iterations/archive/` 下的 Sprint。
- 指标统计口径不受需求中心当前搜索、对象类型、负责人、优先级或 Sprint 筛选条件影响，始终反映当前项目级 Sprint 总览。
- 指标刷新应跟随需求中心数据刷新、手动刷新和空间切换，保持与后端聚合结果一致。
- 覆盖无 Sprint、仅有规划中 Sprint、仅有已归档 Sprint、接口失败或数据解析失败等展示状态。

### 不包含

- 不在本需求内新增 Sprint 创建、归档、评审或执行流程。
- 不在本需求内改变现有 REQ、BUG、OpenSpec Change 的状态映射规则。
- 不在本需求内建设独立的 Sprint 趋势图、燃尽图、交付周期分析或团队效率分析。
- 不在本需求内改变需求中心既有筛选条件对卡片列表和现有对象统计的影响方式。
- 不在本需求内新增移动端、微信小程序、桌面端或管理后台页面。

## 功能要求

### FR-001 Sprint 数量指标卡

需求中心应在既有指标卡区域新增或扩展 Sprint 指标，展示当前项目的已完成 Sprint 数与总体 Sprint 数。

指标文案应清晰表达两个数字的关系，例如“3 / 5”。卡片标题为 `Sprint`，项目级口径说明通过标题旁 tooltip 展示，避免让用户误解为当前筛选结果内的 Sprint 数量。

### FR-002 统计口径

系统应以 Sprint 生命周期事实源计算数量。累计数量应覆盖 `iterations/change/` 与 `iterations/archive/` 中可识别的有效 Sprint；已完成数量默认以 `iterations/archive/` 中的 Sprint 为准。

若存在历史兼容状态，例如 Sprint 文件标记为 `completed` 但目录尚未迁入 archive，聚合逻辑应明确是否纳入已完成统计，并通过测试固定口径，避免同一 Sprint 被重复计数。

### FR-003 与筛选条件解耦

Sprint 数量指标应保持项目级总览语义，不受当前搜索关键字、对象类型、负责人、优先级或 Sprint 筛选条件影响。

当用户筛选某个 Sprint 时，卡片列表和局部对象统计可以随筛选变化，但 Sprint 数量指标仍应展示项目级已完成与累计数量。

### FR-004 数据刷新与一致性

当需求中心首次加载、用户手动刷新、切换空间或后端聚合数据重新获取时，Sprint 数量指标应同步刷新。

刷新中应保持布局稳定，不因数字加载导致指标卡高度或邻近卡片位置跳动。刷新失败时应保留最近一次可用数据或展示稳定错误态，不影响需求中心其他区域可用性。

### FR-005 空态、异常态与安全展示

当项目没有任何 Sprint 时，指标应展示 `0 / 0` 或等价空态文案。

当 Sprint 数据解析失败、权限不足或接口失败时，页面应展示轻量错误提示，并允许用户重试。错误内容不得暴露本机绝对路径、内部堆栈、未脱敏治理文档全文、密钥、token 或 `.env` 内容。

### FR-006 测试与文档

本需求进入实现阶段时，应覆盖 Sprint 数量聚合测试、已完成与累计口径测试、筛选不影响指标的前端测试、加载/空态/错误态测试，以及需求中心接口响应字段或 API 文档同步。

如复用既有需求中心聚合接口，应在接口契约中补充 Sprint 数量字段；如新增字段进入客户端类型或生成物，应同步 OpenAPI 与客户端调用约束。

## UI 约束

- 指标卡视觉应延续需求中心既有统计区样式，与现有深浅主题、间距、字号和近直角组件风格一致。
- 指标卡高度应保持紧凑，减少顶部统计区纵向占位。
- 指标标题、主数字和辅助说明应可在桌面与移动宽度下稳定展示，不与相邻指标、筛选栏或看板列头重叠。
- 数字加载态应使用骨架、占位或保持上一值的方式减少布局抖动。
- 指标辅助文案应避免占用卡片底部；需要解释口径时使用统一 tooltip，而不是占用指标卡主视觉。
- 无数据时应展示稳定的 `0 / 0` 语义，不用空白卡片占位。

## 关联需求

- REQ-0012-frontend-requirement-center：本需求承接需求中心指标区与 9 阶段看板的页面框架。
- REQ-0013-requirement-center-real-data-integration：本需求依赖需求中心真实数据聚合能力提供 Sprint 事实源统计。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - request_logs
    - usage_events
  reason: 该指标预计通过需求中心页面数据请求返回，并可能随页面加载、手动刷新、空间切换或筛选操作触发请求与行为事件；不新增长耗时、多步骤或异步任务，因此 task_traces 与 task_trace_spans 暂不适用。
  validation: 实现阶段需验证需求中心聚合接口请求日志不暴露内部路径或原始文档全文，并验证页面加载、刷新和空间切换行为事件仅记录脱敏统计上下文。
```

## 状态块

```yaml
status: done
generated_at: 2026-09-14 10:21:15
completed_at: 2026-09-14 14:50:18
reviewed_at: 2026-09-14 14:56:30
approved_at: 2026-09-14 14:56:30
in_sprint_at: 2026-09-14 15:01:21
source_material:
  - capture.md
  - user-stories.md
  - business-flow.md
  - acceptance.md
  - prototype/web/context.md
  - prototype/web/prototype.html
  - review.md
  - rules/requirement-management.md
  - rules/ui-design.md
  - docs/standards/prototype-ui-acceptance.md
  - docs/standards/product-data-collection-observability.md
  - docs/knowledge-base/README.md
  - docs/knowledge-base/retrospectives/sprint-005-retrospective.md
next: 无
iteration: sprint-006
openspec_change: add-requirement-center-sprint-completion-metrics
```
