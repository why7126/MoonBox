---
bug_id: BUG-0026-chat-platform-opsx-archive-source-permission
title: Chat 平台无法归档 source 工作区 Change 且状态未知
status: done
created_at: 2026-10-04 11:11:31
updated_at: 2026-10-12 14:26:59
environment: local docker chat-platform
related_requirement: REQ-0039-requirement-center-card-chat-session-reuse
related_bug: BUG-0025-requirement-center-command-chain-write-gap
severity: high
---

# Chat 平台无法归档 source 工作区 Change 且状态未知

## 现象

在 Chat 工作台中执行 `/opsx-archive REQ-0039-requirement-center-card-chat-session-reuse` 后，页面提示“状态未知：暂无法确认执行状态，请查看轨迹核实；不要重复发送命令”。治理事实源未归档：Change 仍位于 `openspec/changes/`，REQ 仍为 `in_sprint`，Sprint 仍显示该 Change 待 archive。

## 复现步骤

1. 在本地常驻 Chat 平台中打开 `REQ-0039-requirement-center-card-chat-session-reuse` 对象会话。
2. 发送 `/opsx-archive REQ-0039-requirement-center-card-chat-session-reuse`。
3. 观察 Chat turn 状态、轨迹和治理事实源。

## 期望 vs 实际

期望：Chat 平台能够在具备授权的本地 source 工作区中执行 archive 所需写入，或在权限不足时返回可诊断的失败状态，不把 turn 留在不可恢复的 unknown。

实际：上一轮执行端明确报告 `openspec/specs/` 与 `openspec/archive/` 无写权限、Change 身份校验被 `.agents/.codex/.git` 干扰、OpenSpec CLI 不可用；后续重试在 setup 阶段进入 `unknown`，仅落 `platform_execution_setup_failed`，无 executor turn id 和执行事件。

## 附件

- 用户截图：Chat 工作台显示“状态未知”。
- 本地取证：`chat_turns` 最近记录、Codex runtime thread history、Docker Compose 渲染配置、相关代码路径。

## 2026-10-10 补充现象：全仓工具目录残留

用户确认沿用本 BUG，要求仓库自有目录中除根目录 `.agents/` 外，不出现或遗留 `.agents/`、`.codex/`。当前只读盘点发现 `openspec/archive/`、`openspec/changes/`、`openspec/specs/`、`docs/spec-logs/` 下各有一对空目录；`issues/`、`iterations/` 目前无同类残留。Git 忽略的第三方依赖和虚拟环境目录不作为项目目录治理对象；其中内容不得自动删除。

此前归档返修已证实 Chat 沙箱在 `issues/`、`iterations/` 产生过空目录并遗留到宿主，但本次八个目录的具体创建轮次尚未核实。现有目录校验与 worker 清理仅覆盖两个治理根，不能保证全仓边界。后续需核实创建路径，对仓库自有目录做全范围检查，并分别验证运行中临时挂载、宿主空残留、非空目录和符号链接。此补充不表示既有归档问题已复验通过。
