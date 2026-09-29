---
title: 需求中心验收进度分类统计规格
created_at: '2026-09-15 23:08:22'
updated_at: '2026-09-15 23:08:22'
---

# 需求中心验收进度分类统计规格

## MODIFIED Requirements

### Requirement: 治理对象列表

系统 SHALL 为需求中心返回能支撑卡片文档查看、动作流转、AI 聊天反馈和任务进度展示的治理对象字段。

#### Scenario: 治理对象包含文档入口

- **WHEN** 后端返回 Requirement 或 Bug 卡片数据
- **THEN** 每个关联文档必须包含文件名、文档类型、打开方式、可访问 URL 或禁用原因
- **AND** 前端卡片必须按当前阶段可展示文档白名单渲染这些入口；采集池阶段只展示 `capture.md` 与 `trace.md`
- **AND** Markdown 文件打开方式必须可映射到右侧抽屉
- **AND** HTML 文件打开方式必须可映射到新 Tab 预览

#### Scenario: 治理对象包含动作映射

- **WHEN** 后端返回 Requirement 或 Bug 卡片数据
- **THEN** 每个对象必须包含当前阶段主动作的产品化文案、命令映射、是否需要选择弹窗、禁用状态和禁用原因
- **AND** 命令映射必须使用完整 REQ 或 BUG ID

#### Scenario: 治理对象包含任务进度

- **WHEN** 对象关联 OpenSpec Change 且存在 `tasks.md`
- **THEN** 系统必须返回任务总数、已完成数量、是否只读、是否可验收和阻塞提示
- **AND** `tasks.md` 缺失或解析失败时必须返回脱敏错误摘要，而不是误报完成

#### Scenario: 验收中治理对象包含分类进度

- **WHEN** REQ、BUG 或独立 Change 映射为验收中且当前关联 Change 存在 `tasks.md`
- **THEN** 系统 SHALL 返回研发、测试、人工验收三组分类进度，每组包含已完成数量、总数量和可展示状态
- **AND** 三组分类进度 SHALL 来自当前关联 Change 的 `tasks.md` 可关闭 checkbox 任务，不得使用 `acceptance.md`、`review.md`、`trace.md` 文档存在性替代测试完成度
- **AND** 人工验收进度 SHALL 来自 `tasks.md` 人工验收类任务，不得因 `manual_acceptance_count <= 0` 或缺少显式计数默认显示 `1/1`

#### Scenario: 验收中分类缺失降级

- **WHEN** 当前关联 Change 的 `tasks.md` 缺失、解析失败或缺少可识别分类
- **THEN** 系统 SHALL 返回脱敏错误摘要或待核实提示
- **AND** 前端 SHALL 显示明确的待核实或不可用状态，不得误报研发、测试或人工验收满格

#### Scenario: 返回独立与关联 Change 身份

- **WHEN** 授权项目快照含无 Issue 来源的 Change 或 Issue 已关联 Change
- **THEN** 系统 SHALL 为独立 Change 返回 type=change 的自身身份、只读文档、状态及进度，且不伪造 Issue；阶段动作使用真实能力元数据，依据实际文档和权限给出禁用原因，不按独立Change类型固定禁用，文档仍只读
- **AND** Issue 卡片保留原 id，返回受控关联摘要及可空当前 Change，含糊时不任意选取末项或首项
- **AND** 卡片 ID、中文标题、文档和进度必须指向同一当前 Change；无分级的独立对象不得伪造默认优先级

## ADDED Requirements

### Requirement: 文档进度入口

系统 SHALL 允许用户从卡片进度入口打开当前关联 `tasks.md`，并定位对应章节或任务。

#### Scenario: 卡片追踪文档固定所属Issue

- **WHEN** 用户在任一阶段查看REQ或BUG卡片
- **THEN** 卡片仅提供一个标签为trace.md的入口，读取所属Issue目录的trace.md
- **AND** 不提供Change trace入口，文件缺失时明确不可用且不回退Change trace
- **AND** Change仍用于内部阶段计算，其他文档入口和原授权边界保持

#### Scenario: 卡片进度入口定位任务文档

- **WHEN** 用户点击 REQ 或 BUG 卡片的研发、测试或人工验收入口
- **THEN** 系统 SHALL 通过当前卡片关联文档入口读取完整 tasks.md，在加载后优先定位对应章节、其次定位匹配任务并高亮，不打开独立进度面板，不改变文档权限
- **AND** 关联或文件缺失时 SHALL 明确提示；目标章节或任务缺失时 SHALL 展示完整文档并说明未找到目标，不回退其他文档或历史返修任务
- **AND** 点击研发、测试或人工验收入口时，定位目标 SHALL 与对应分类进度使用同一 `tasks.md` 分类模型
