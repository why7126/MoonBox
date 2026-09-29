---
title: tasks 分类与返修任务统计口径规格
created_at: '2026-09-15 23:08:22'
updated_at: '2026-09-15 23:08:22'
---

# tasks 分类与返修任务统计口径规格

## ADDED Requirements

### Requirement: tasks 分类统计口径

MoonBox MUST 在 `tasks.md` 中沉淀可被需求中心稳定识别的研发、测试、人工验收三类任务口径。该口径 MUST 适用于首次 `/opsx-apply` 任务和后续 `/opsx-modify` 验收返修任务。

#### Scenario: 生成可分类任务

- **WHEN** `/req-opsx`、`/bug-opsx` 或等价命令生成 Change `tasks.md`
- **THEN** 任务应按实施任务、回归验证、文档同步和人工验收等稳定章节或显式标记组织
- **AND** 需求中心可将可关闭 checkbox 分类为研发、测试或人工验收
- **AND** 任务正文、证据链接、说明段落和表格正文不得作为卡片进度分母

#### Scenario: 返修任务纳入分类

- **WHEN** `/opsx-modify` 根据验收反馈追加返修任务
- **THEN** 返修实现任务必须进入研发类分母
- **AND** 返修回归测试、视觉证据和校验任务必须进入测试类分母
- **AND** 人工复验、人工确认或 sign-off 任务必须进入人工验收类分母
- **AND** `acceptance-fixes.md` 继续作为完整返修台账事实源，但其表格正文和说明文字不直接计入卡片进度

#### Scenario: 分类口径缺失时提示

- **WHEN** Change `tasks.md` 缺少可识别分类
- **THEN** 需求中心 SHALL 返回待核实或降级提示
- **AND** Agent 在后续修复、返修或归档前 SHOULD 补齐分类口径或记录不适用原因
- **AND** 系统不得通过文档存在性、默认人工验收计数或总 checkbox 完成率误报三类进度完成
