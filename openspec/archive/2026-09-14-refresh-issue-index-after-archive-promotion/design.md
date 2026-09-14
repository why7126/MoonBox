---
created_at: 2026-09-14 09:01:23
updated_at: 2026-09-14 09:01:23
---

## 设计说明

`promote-issues-for-archive.py` 的职责仍是归档阶段迁移 Issue 目录。迁移成功后，脚本重新读取 Issue 集合，让 `IssueRecord.path` 指向新的 `archive/` 目录，再调用 `derive_issue`、`patch_registry_entry` 与 `patch_issue_changelog_index`。

该方案不在 promote 脚本中复制状态推导规则，避免与 Workflow Sync 形成第二套事实逻辑。Sprint 来源按命令上下文解析：`--sprint` 使用显式 Sprint，`--change` 按 `opsx.archive` 自动解析 Sprint。

## 不适用影响

- API/DB/Web/客户端/管理端/Orval：不适用，本次只改治理脚本。
- Docker Compose/部署：不适用，不改变运行服务。
- 产品数据采集与链路观测：不适用，不新增日志、事件或 Task Trace。

## 验证策略

- 单元测试覆盖 promote 后 registry 与 CHANGELOG 从旧 `review/` 路径刷新到 `archive/` 路径。
- 运行上下文预算、OpenSpec 语言、目录结构和目标 Change 校验。
