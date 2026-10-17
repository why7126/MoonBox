---
bug_id: BUG-0026-chat-platform-opsx-archive-source-permission
title: Chat 平台无法归档 source 工作区 Change 且状态未知临时规避方案
created_at: 2026-10-04 11:11:31
updated_at: 2026-10-04 11:11:31
status: active
---

# Chat 平台无法归档 source 工作区 Change 且状态未知临时规避方案

## 临时规避

在修复完成前，不建议继续在同一个 unknown Chat 会话里重复发送 `/opsx-archive`。可以在具备仓库写权限、OpenSpec CLI 和项目依赖可用的本地开发环境中直接执行归档命令：

```bash
/opsx-archive REQ-0039-requirement-center-card-chat-session-reuse
```

执行前需要确认：

- 当前工作区没有未核对的归档副本结果。
- `openspec/changes/add-requirement-center-card-chat-session-reuse` 仍处于 applied。
- `openspec/archive/` 中不存在同名归档目录。
- 当前 shell 环境具备写入 `openspec/specs/`、`openspec/archive/`、`issues/` 和 `iterations/` 的权限。

## 风险

临时规避只解决当前归档任务，不能修复 Chat 工作台内的权限模型和 unknown 可诊断性。若继续从 Chat 平台重试，仍可能得到状态未知或权限阻断。
