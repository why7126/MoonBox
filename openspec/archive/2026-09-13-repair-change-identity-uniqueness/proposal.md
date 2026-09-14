---
created_at: 2026-09-13 15:59:31
updated_at: 2026-09-13 23:43:10
---

# 修复 Change 身份重复与唯一性门禁

## 背景

初建与强化复用了同一 ID，两个归档使需求中心无法选择唯一事实源。用户已确认它们是不同工作。

## 变更内容

- 保留初建 ID，强化改为 enhance-ui-reference-replication-action-matrix，保留历史身份纠正证据。
- 同步 Sprint 引用与归档状态；新增跨活动和归档的唯一性校验，接入目录与归档门禁。

## 能力范围

### 新增能力

- `change-identity-uniqueness`: 跨生命周期身份唯一性。

## 影响范围

仅治理脚本、文档和历史归档身份修正；不修改 src、正式规格、API、DB、UI、部署或客户端生成。

## 归档门禁修复补充

用户追加授权：规范本地 logs/ 取证边界并保留现有日志，中文化 fix-requirement-center-apply-lifecycle-sync 标题；此项作为原治理修复的完成门禁收尾，不新增业务能力。
