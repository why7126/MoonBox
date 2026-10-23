---
bug_id: BUG-0062-archive-requirement-scope-conflict
title: 归档恢复冲突误判临时处置方案
created_at: '2026-10-21 17:58:42'
updated_at: '2026-10-21 17:58:42'
---

# 归档恢复冲突误判临时处置方案

## 可用临时处置

当前无可安全自动解除阻塞的已验证workaround。保持sprint-011未关闭，保留现有Change归档、Issue完成事实及原36项AC证据。其他无依赖工作可继续，但不能把受阻迭代标为已完成。

## 只读诊断

- `python scripts/validate-issue-acceptance-ready.py fix-chat-unified-run-status-verification`：复核准入阻塞。
- `python scripts/sync-workflow-status.py --event sprint.archive --sprint sprint-011 --dry-run`：只预演，不写入待验收投影。
- 对照根因文档E1—E8；记录真实AC已通过与恢复仍阻塞两项事实。

## 禁止的规避方式

不删除或重写journal、manifest和历史哈希，不强填passed，不回滚已合入的后继规格，不重复执行成功归档、模型或Issue迁移，不使用force绕过完整门禁。

## 退出条件

独立修复Change完成评审、实现和验收，共享入口判定一致且安全负例通过后，再按当前授权执行sprint-011关闭流程。重新核验输入版本，保留原完成事实；本文件不授权实际归档或生产操作。
