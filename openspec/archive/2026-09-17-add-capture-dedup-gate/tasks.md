---
title: Capture 创建前去重门禁任务
created_at: 2026-09-16 22:42:16
updated_at: 2026-09-16 22:42:16
---

# Capture 创建前去重门禁任务

## 1. OpenSpec And Sprint Scope

- [x] 1.1 创建 `add-capture-dedup-gate` Change，补齐 proposal、design、tasks、delta spec 与 trace。
- [x] 1.2 将纯治理 Change 纳入 Sprint scope，并通过 Workflow Sync / Sprint scope 校验。

## 2. Capture Command Contracts

- [x] 2.1 更新 `/capture`，在分类拆分后分别执行 REQ/BUG 创建前重复/相似 Issue 检查。
- [x] 2.2 更新 `/req-capture`，在分配新 REQ ID 前检查已有 REQ 候选并处理 refinement。
- [x] 2.3 更新 `/bug-capture`，在分配新 BUG ID 前检查已有 BUG 候选并处理重复缺陷。

## 3. Governance Rules

- [x] 3.1 同步需求管理、缺陷管理、上下文预算和 AGENTS 入口规则。
- [x] 3.2 写入治理日志并更新 `docs/spec-logs/CHANGELOG.md`。

## 4. 验证

- [x] 4.1 运行上下文预算、OpenSpec 语言、目录结构、目标 Change validate、Sprint scope 和 Workflow Sync 校验。
- [x] 4.2 最终执行 Workflow Sync 与 AI Usage Hook，并输出执行链路复盘。
