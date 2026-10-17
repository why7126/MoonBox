---
title: 修复产品内实现命令的治理字段兼容与权限留痕
created_at: 2026-10-07 15:16:20
updated_at: 2026-10-07 15:16:20
---

# 修复产品内实现命令的治理字段兼容与权限留痕

## 背景

来源 [BUG-0033](../../../issues/bugs/review/BUG-0033-opsx-apply-governance-scope-source-readonly/bug.md)，已评审、根因 confirmed，纳入 sprint-008，估算 M / 3 人天。原 BUG-0029 的 Change 使用 bug_id/iteration，策略只读取 bug/sprint，导致已纳入 Sprint 的实现任务回退治理权限、源码只读。原轮次 profile 与完整策略内存对照支持因果结论；历史 reason_code 不得伪造。

## 变更内容

- 归一化可信 Change trace 的来源 Issue 与 Sprint 字段，兼容既有字段；冲突和非法关联拒绝实现权限。
- 保持成员权限、Sprint 双向成员、Change 阶段、准备候选和运行中撤权门禁。
- 在执行器启动边界关联同一 turn 的 scope、reason_code、实际选用 profile、治理输入版本摘要和时间；验证失败不伪装为已启动。
- 覆盖原 BUG-0029、REQ/BUG 字段矩阵、负向权限与 AC-011 留痕回归。

## 能力影响

### 新增能力

无独立能力模块。

### 修改能力

- codex-session-execution：补充实现授权字段兼容、冲突拒绝与权限决策审计要求。

## 影响范围

后端 chat policy、execution、app_server 及现有事件记录路径；必要的测试和权限观测文档。优先复用现有事件存储，不预设新增业务 API、数据库表或前端交互。若实现确需契约变化，先更新本设计和相应 API/DB 文档与验证。当前仅规划，不写源码或正式 specs。

## 回滚方案

回滚权限解析与新事件生成代码，保留已产生的脱敏证据；恢复后原别名场景可能再次只读，应明确阻塞而非放宽权限。无生产升级、数据库恢复或权限扩张动作。
