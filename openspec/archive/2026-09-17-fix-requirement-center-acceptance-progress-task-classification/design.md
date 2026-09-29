---
title: 需求中心验收进度分类统计修复设计
created_at: '2026-09-15 23:08:22'
updated_at: '2026-09-15 23:08:22'
---

# 需求中心验收进度分类统计修复设计

## 背景与现状

BUG-0023 的根因状态为 `confirmed`，证据链包含用户截图、后端 `_build_issue` / `_change_tasks` / `_test_progress`、前端 `visibleManualAcceptanceProgress`、现有测试 fixture 和文档治理规则。

当前实现将三类进度拆成三种不同事实源：

| 展示项 | 当前来源 | 问题 |
|---|---|---|
| 研发 | linked Change `tasks.md` 的所有 checkbox | 不区分研发、测试、人工验收 |
| 测试 | `acceptance.md`、`review.md`、`trace.md` 存在性 | 文档齐备不等于测试任务完成 |
| 人工验收 | 前端按 `manual_acceptance_count` 默认推导 | `1/1` 不等于真实人工 sign-off |

这导致验收中卡片可能在返修任务未完成、测试任务未执行或人工复验未发生时显示完成态。

## 根因

需求中心缺少统一的 `tasks.md` 分类统计模型。后端没有输出研发、测试、人工验收三类结构化进度，前端为了补齐展示使用默认推导，测试也固化了旧口径。

## 修复方案

### 分类解析模型

后端在读取当前关联 Change 的 `tasks.md` 时，按稳定章节或显式标记识别可关闭 checkbox 任务，并输出三组进度：

| 分类 | 统计范围 |
|---|---|
| 研发 | 实施、修复、后端、前端、API、类型、迁移、实现类 checkbox |
| 测试 | 回归验证、自动化测试、视觉证据、OpenAPI / 客户端生成校验、手工复核类 checkbox |
| 人工验收 | 人工复验、sign-off、验收确认、归档前人工确认类 checkbox |

统计对象仅包含 `- [ ]` / `- [x]` 形式的任务项。普通段落、表格正文、证据链接、历史说明和 `acceptance-fixes.md` 台账正文不进入分母。

### 返修任务纳入

`/opsx-modify` 追加到 `tasks.md` 的返修实现、返修验证、视觉证据、文档同步和人工复验任务，应按同一分类规则进入对应分母。`acceptance-fixes.md` 继续作为完整返修台账事实源，卡片统计只读取 `tasks.md` 中可关闭任务。

### 降级与兼容

如果 `tasks.md` 缺失、解析失败或无法识别分类：

- 后端返回脱敏错误摘要或待核实状态，不得误报三类进度满格。
- 前端显示明确的待核实/不可用提示，不再用文档存在性或 `manual_acceptance_count <= 0` 推导人工验收完成。
- 旧字段在过渡期保持兼容，但验收中卡片优先使用新的分类进度结构。

### 接口与前端

需求中心 context 响应增加或调整结构化进度字段，表达研发、测试、人工验收三类完成数、总数、状态和可选 warning。前端卡片渲染三组值时只消费后端分类结果；点击进度入口仍打开当前关联 `tasks.md` 并定位对应章节或任务。

### 产品数据采集与链路观测

product_data_collection_observability: applicable

affected_layers: API响应、Web消费、request_logs、OpenAPI / 客户端生成。

reason：本 Change 修改需求中心 context 响应字段和 Web 展示口径，需要验证请求日志与链路 ID 不回归、响应不暴露本机路径或原始 Markdown 内容。usage_events、task_traces、task_trace_spans、DB 和对象存储不新增结构或写入。

validation：实施时验证直接 API 与前端展示一致、OpenAPI / Orval 同步、错误摘要脱敏、文档读取失败不泄露内部路径。

## 测试策略

- 后端聚合测试覆盖三类章节、显式标记、无分类降级、返修任务纳入、历史台账不计入分母。
- 前端测试覆盖 Image #1 等价场景：验收中卡片存在三类任务时按分类进度展示，未完成人工复验时不得显示 `1/1`。
- 回归测试覆盖 `acceptance.md`、`review.md`、`trace.md` 齐备但测试任务未完成的场景，确保测试进度不再显示完成。
- API / OpenAPI / 客户端类型校验覆盖新增或调整字段。
- 保留 `tasks.md` 点击入口定位对应分类章节或任务的行为。

## 风险与回滚方案

分类解析若仅依赖关键词可能产生漏分或误分，因此应优先使用稳定章节或显式标记，并对无分类任务给出待核实提示。回滚时恢复旧字段兼容展示，但不得删除新测试样例、BUG 证据和统计口径说明。
