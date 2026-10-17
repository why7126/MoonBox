---
title: Chat 平台 source 工作区归档权限与状态诊断修复
created_at: '2026-10-04 11:17:53'
updated_at: 2026-10-10 07:21:24
---

# Chat 平台 source 工作区归档权限与状态诊断修复

## 背景与问题

本地 Chat 工作台已启用 source 工作区策略，用户期望产品内 `/opsx-archive <完整 REQ 或 BUG ID>` 直接以治理事实源为准完成 OpenSpec 归档。但实际执行 `/opsx-archive REQ-0039-requirement-center-card-chat-session-reuse` 时，上一轮执行端报告 `openspec/specs/` 与 `openspec/archive/` 无写权限，Change 身份校验被 `openspec/changes/.agents`、`.codex`、`.git` 影响，后续重试又在 setup 阶段落为 `unknown/platform_execution_setup_failed` 且没有 executor turn id。

这会让用户既无法在产品内完成归档，也无法确认是否安全重试，破坏“事实源优先”的 Chat 工作台可信度。

## 变更目标

- 为 Chat 平台中的 `/opsx-archive` 提供最小化 archive 写权限，允许写入 `openspec/specs/`、`openspec/archive/`、必要 Issue/Sprint 文档和治理日志。
- 保持普通治理写命令的最小权限，不因为 archive 扩权而获得规格生效目录或归档目录写权限。
- 让本地 source 工作区的 worker 能实际写入用户授权的真实仓库，同时保持 backend 只读投影和执行容器内部权限 profile 约束。
- 将未启动执行器的 setup / workspace / sandbox 失败记录为明确 failed 状态和安全错误码，不再展示为不可诊断的 unknown。
- 修正 Change 身份校验对隐藏系统目录的处理，避免 `.agents`、`.codex`、`.git` 等非 Change 目录阻断归档。

## 能力影响

- Chat 工作台对象会话在满足归档门禁时，可以通过完整 REQ/BUG ID 发送 `/opsx-archive` 并写入治理事实源。
- 状态投影继续以事实源重读为准；执行失败时页面展示可恢复失败，而不是把 setup 阶段错误伪装成执行中断。
- Docker 本地常驻 Chat 部署需要明确 source 工作区写入边界，避免后端投影可写或执行容器无限制写入。
- 归档及其他写入型 Chat 轮次不得在仓库自有目录留下空 `.agents`、`.codex`；根目录 `.agents` 保留为技能入口。执行中临时挂载与宿主残留分别判断。

## 观测与边界

`product_data_collection_observability` 适用。受影响层包括 Chat turn 状态、request_logs、task_traces、task_trace_spans、执行事件和治理事实源刷新。错误码和事件摘要必须脱敏，不得记录本机绝对路径、密钥、Token、认证文件内容或执行器完整异常栈。

## 非目标

- 本 Change 不替代 `/opsx-archive` 既有归档门禁，不自动归档未完成 Change。
- 本 Change 不为普通治理写命令开放 `openspec/specs/` 或 `openspec/archive/` 写权限。
- 本 Change 不改变生产云端隔离策略；source 写入仅适用于本地受信任部署配置。
