---
created_at: 2026-09-12 17:48:54
updated_at: 2026-09-12 17:48:54
---

# Issue 分级元数据统一

## 迭代目标与变更摘要

REQ 使用 priority，BUG 使用 severity。trace Frontmatter 为事实源，capture 与主文档同步；规范化模板与 Sprint BUG 表头，保留正文历史及 created_at。

## 影响范围与更新文件

- rules/document-governance.md、requirement-management.md、bug-management.md、agent-context-budget.md。
- AGENTS.md、docs/README.md；req/bug capture 与 generate、workflow-sync 技能。
- scripts/workflow_sync/collect.py、classification.py、engine.py、patch.py、README.md。
- tests/unit/test_issue_classification.py；BUG-0015 分级文案、sprint-005 范围和派生文档；本次 OpenSpec Change。

## 验证结果

9 项聚焦单元测试通过；上下文预算、中文、目录、Change 和 Sprint scope 校验通过；Workflow Sync 实际执行 Errors=0。用量 Hook 结果见 Change trace。

## 边界声明

product_data_collection_observability: not_applicable

affected_layers: 治理文档与 CLI 分级同步。

N/A 原因：不新增行为事件、请求日志、Task Trace 或链路字段；不修改 API、DB、Web、客户端、管理端、Orval、Docker Compose、对象存储及安全边界。无需客户端生成或数据库迁移。

validation: 分级冲突优先级、旧 hint 兼容、非法/缺失拒绝、类型隔离、注册表、dry-run、幂等和时间戳保留测试。

## 后续建议

归档前按本 Change 验收记录复核。未批量迁移历史归档，未自动创建后续 Issue/Change。
