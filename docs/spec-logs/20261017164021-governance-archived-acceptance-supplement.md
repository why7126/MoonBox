---
title: 已归档验收附件补证治理日志
created_at: 2026-10-17 16:40:21
updated_at: 2026-10-17 16:40:21
---

# 已归档验收附件补证治理日志

## 迭代目标

归档后单个验收附件变化时，保留原完整验收清单，提供受控复证并防止 Sprint 关闭投影错误回退。

## 变更摘要与影响范围

新增命令型 AC 单项补证生成器；Workflow Sync 核对原运行、计划命令、输入指纹、旧/新附件哈希与退出码后接受补证。产品轮次和视觉 AC 不适用。

## 更新文件

- `scripts/opsx_acceptance.py`、`scripts/create-archived-acceptance-supplement.py`、`scripts/workflow_sync/issue_subdocuments.py`
- `tests/unit/test_archived_acceptance_supplement.py`
- `docs/standards/opsx-acceptance.md`、`.agents/skills/sprint-archive/SKILL.md`
- `openspec/changes/verify-archived-acceptance-artifact-supplement/`、`iterations/change/sprint-008/`

## 验证结果

BUG-0025 AC-003 原命令重跑 1 passed；补证与关闭扫描聚焦测试 7 passed、相关状态同步单元测试 6 passed。Workflow Sync 关闭预演 0 errors，8 个 Issue 验收投影均为 passed。目录、上下文预算、中文优先与 Change 校验通过。

## 产品与部署影响

API、数据库、Web、客户端、管理端、Orval、Docker Compose 均无运行时变更；安全边界不变。

## 后续建议

归档后文档追加说明时保留原 manifest，先比较附件哈希并按 AC 类型选择受控补证，不将补证冒充完整重验。
