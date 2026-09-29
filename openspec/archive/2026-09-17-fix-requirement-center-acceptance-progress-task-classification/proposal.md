---
title: 修复需求中心验收进度分类统计
created_at: '2026-09-15 23:08:22'
updated_at: '2026-09-15 23:08:22'
---

# 修复需求中心验收进度分类统计

## 背景

[BUG-0023-requirement-center-acceptance-progress-task-classification](../../../issues/bugs/review/BUG-0023-requirement-center-acceptance-progress-task-classification/bug.md) 已评审通过并纳入 `sprint-007`。用户截图显示需求中心「验收中」卡片存在 `研发 33/33 测试 3/3 人工验收 1/1` 和 `研发 29/29 测试 3/3 人工验收 1/1` 等满格展示，但当前三类进度不是统一来自 `tasks.md` 分类任务。

根因已确认：研发进度读取 linked Change `tasks.md` 的全部 checkbox，测试进度读取 `acceptance.md`、`review.md`、`trace.md` 文档存在性，人工验收进度由前端默认推导。该口径无法表达 `tasks.md` 中研发、测试、人工验收三类任务，也无法稳定纳入 `/opsx-modify` 返修任务。

## 变更内容

- 后端建立 `tasks.md` 分类统计模型，输出研发、测试、人工验收三组完成数 / 总数。
- 验收中卡片不再使用文档存在性或 `manual_acceptance_count <= 0` 默认值误报测试、人工验收完成。
- `/opsx-modify` 追加到 `tasks.md` 的可关闭返修任务按任务性质进入对应分类分母。
- `acceptance-fixes.md` 保留为完整返修台账事实源，但台账正文、说明文字和证据链接不直接计入卡片分母。
- 同步后端响应、OpenAPI / 客户端类型、前端卡片展示、回归测试和统计口径文档。

## 能力影响

### 新增能力

无新增能力目录。

### 修改能力

- `web-catalog-requirement-center-real-data`：需求中心治理对象进度摘要从单一任务总数扩展为验收中三类任务进度，并明确降级提示和错误摘要。
- `harness-runtime`：沉淀 `tasks.md` 三类任务与 `/opsx-modify` 返修任务统计口径，避免后续任务生成和卡片统计再次漂移。

## 影响范围

影响需求中心后端治理事实聚合、`/api/v1/requirement-center/context` 响应字段或兼容字段、OpenAPI / Orval 客户端类型、前端验收中卡片进度展示、`tasks.md` 分类解析和相关测试。无需数据库迁移，不改变真实执行状态、Change apply 事实或归档状态。

`product_data_collection_observability` 适用：本 Change 涉及 API 响应字段、Web 消费和请求日志链路验证；不新增数据库表、行为事件、Task Trace 或对象存储写入。实施时需验证响应脱敏、直接 API 和前端展示一致、OpenAPI / 客户端类型同步。

## 回滚方案

如实施后出现解析兼容问题，回滚后端分类统计与前端消费逻辑，恢复旧字段兼容展示；保留新测试样例和文档口径作为后续修复依据。回滚不得修改历史 BUG、Sprint 或已归档 Change 状态，不删除既有 `tasks.md` 或 `acceptance-fixes.md` 内容。
