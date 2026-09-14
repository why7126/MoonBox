---
created_at: 2026-09-12 17:38:39
updated_at: 2026-09-12 17:47:01
---

## 背景

现有 collect 优先读取主文档，BUG 共用内部 priority 展示槽；Capture 模板使用 hint，Sprint BUG 表头使用优先级。

## 目标与非目标

目标：trace Frontmatter 为当前分级唯一事实源，REQ 用 priority，BUG 用 severity。
非目标：业务 API/UI 改造、自动映射 P 等级为严重度、全量历史清洗。

## 设计决策

- 保存范围为 trace、已存在 capture、已存在 requirement/bug；不创建缺失子文档。
- trace 正式字段优先；缺失时按主文档、capture 的正式字段和同类型 hint 回退，校验后写入 trace。非法显式值阻断聚焦同步，缺失值也不猜测。
- 同步只处理本次聚焦 Issue；注册表和展示取同一值。移除被同步文档中异类分级字段与旧 hint，仅处理 Frontmatter，不覆盖正文历史。
- 内部 IssueRecord.priority 暂作为兼容展示槽，BUG 值仍是 severity，不对外写成 priority。
- 当前值变更由命令在 trace 变更记录记载依据；同步保留历史，幂等刷新 updated_at，不变更 created_at。

## 风险与取舍

旧记录不完整时需要人工确认等级；禁止依赖缺省 P1 给 BUG 定级。归档目录不做批量迁移。

## 迁移计划

新模板直接写正式字段；存量记录仅在聚焦同步时规范化。可通过 dry-run 查看变更。

## 待确认事项

用户已明确选择 sprint-005，并通过 scope 脚本纳入。
