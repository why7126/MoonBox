---
bug_id: BUG-0026-chat-platform-opsx-archive-source-permission
title: Chat 平台无法归档 source 工作区 Change 且状态未知
status: done
owner: 产品团队
discovered_at: 2026-10-04 10:55:31
environment: local docker chat-platform
related_requirement: REQ-0039-requirement-center-card-chat-session-reuse
related_change:
created_at: 2026-10-04 11:11:31
updated_at: 2026-10-12 14:26:59
severity: high
---

# Chat 平台无法归档 source 工作区 Change 且状态未知

## 现象

本地常驻 Chat 平台中执行 `/opsx-archive REQ-0039-requirement-center-card-chat-session-reuse` 后，用户界面显示 turn 状态未知，并提示不要重复发送命令。对应治理事实源没有完成归档：

- `add-requirement-center-card-chat-session-reuse` 仍在 `openspec/changes/`。
- Change trace 仍为 `status: applied`，`execution.last_event: opsx.apply`。
- REQ trace 仍为 `status: in_sprint`，关联 Change 状态 `applied`。
- `sprint-008` 仍显示 `0/3 Change 已 archive；3 applied`。

## 复现

1. 启动本地常驻 Chat 平台，并使用 source 工作区绑定。
2. 在 `REQ-0039-requirement-center-card-chat-session-reuse` 对象会话中发送 `/opsx-archive REQ-0039-requirement-center-card-chat-session-reuse`。
3. 检查 Chat turn 状态、执行轨迹、OpenSpec active/archive 目录和 Sprint 验收报告。

## 期望结果

Chat 平台对已授权的本地 source 工作区应支持 `/opsx-archive` 所需写入：

- 可以合并 delta spec 到 `openspec/specs/`。
- 可以移动 Change 到 `openspec/archive/YYYY-MM-DD-<change-id>/`。
- 可以运行 Workflow Sync、Issue promote 和 AI Usage hook。
- 若执行环境缺少权限或工具链，应返回明确失败状态和安全错误码，允许用户修复后重试，不应只留下 `unknown`。

## 实际结果

上一轮真实执行端返回归档硬阻塞：当前权限禁止写入 `openspec/specs/` 和 `openspec/archive/`；Change 身份校验因 `openspec/changes/.agents`、`.codex`、`.git` 失败；OpenSpec CLI 不可用。后续重试未进入 Codex runtime，`chat_turns` 记录为 `status=unknown`、`error_code=platform_execution_setup_failed`、`executor_turn_id=null`，且没有 `chat_events` 执行事件。

## 影响范围

- 本地 Chat 工作台无法完成 OpenSpec archive 闭环，导致 REQ/BUG/Change 卡片长期停留验收中或待归档。
- 用户看到状态未知后无法判断是否安全重试，容易重复发送归档命令。
- source 工作区策略虽然减少副本漂移，但当前 Compose/执行权限仍按只读源仓库挂载，和“直接写真实仓库”的产品策略不一致。
- 缺少 setup 失败细分错误，排障需要直接查数据库和运行时日志。
- 同类空工具目录目前还出现在 `openspec/archive/`、`openspec/changes/`、`openspec/specs/` 与 `docs/spec-logs/`；项目目录边界应覆盖全仓自有目录，而不只覆盖 `issues/`、`iterations/`。本次路径的创建轮次仍待核实。

## 补充验收方向

除仓库根目录 `.agents/` 外，仓库自有目录不得出现或遗留 `.agents/`、`.codex/`。全仓校验与执行器清理须共同覆盖；仅确认空目录后才可安全清理，非空目录和符号链接应阻断并保留现场。Git 忽略的第三方依赖、虚拟环境和运行时数据不纳入清理范围。

## 严重等级说明

严重等级为 `high`。该问题不破坏已有业务数据，且可通过本地开发环境手动执行归档绕过；但它阻断 Chat 平台内的正式归档闭环，并让失败状态不可诊断，直接影响治理工作流可信度。
