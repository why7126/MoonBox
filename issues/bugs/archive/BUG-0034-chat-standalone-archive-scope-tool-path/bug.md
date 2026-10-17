---
bug_id: BUG-0034-chat-standalone-archive-scope-tool-path
title: 产品内纯治理 Change 归档因权限与命令路径缺失失败
status: done
created_at: 2026-10-09 10:51:17
updated_at: 2026-10-13 18:51:16
owner: 产品团队
discovered_at: 2026-10-09 10:42:35
environment: local docker chat-platform
related_requirement:
related_bug: BUG-0026-chat-platform-opsx-archive-source-permission
related_change:
severity: high
---

# 产品内纯治理 Change 归档因权限与命令路径缺失失败

## 现象

已 applied 的纯治理 Change `prevent-issue-iteration-tool-dirs` 在对象 Chat 中执行 `/opsx-archive`，轮次标为 completed，实际回复“归档受阻，未修改文件”。Change 当时仍留在 active 目录；宿主标准脚本随后完成该 Change 的归档，说明 Change 内容本身满足归档门禁。

## 复现

1. 绑定本地 source 工作区，关联已 applied 且纳入 Sprint 的纯治理 Change 主对象。
2. 发送 `/opsx-archive prevent-issue-iteration-tool-dirs`。
3. 读取同轮次脱敏权限决策和命令完成事件，并核对 active/archive 事实源。

## 期望与实际

- 期望：已授权的纯治理对象归档获得 `archive_write / moonbox-archive`；执行命令的 PATH 包含镜像中经过预检的 Python、Node、OpenSpec 等工具；归档脚本完成规格合并、目录迁移和 Workflow Sync。
- 实际：同轮次决策为 `governance_write / moonbox-governance`；首个命令以退出码 127 报 `cat: command not found`，后续 OpenSpec 调用以退出码 127 报 `env: node: No such file or directory`。执行器镜像独立工具链探针为 ready，显示工具存在但命令环境无法解析。

## 影响范围

影响纯治理 Change 在产品 Chat 内归档，导致用户需要转到宿主环境完成闭环。未见规格误合并或数据丢失；原轮次未修改 Change 文件。严重等级为 `high`：正式治理闭环被阻断，但有受控宿主归档方式可恢复。

## 已确认根因摘要

服务端归档策略 `_archive_ready` 只接受 `trace.requirement` / `trace.bug` 与主对象 ID 对应，纯治理 Change 的两个来源字段均为空，因此回落普通治理写权限。执行器在 app-server 以 `shell_environment_policy.inherit="none"` 启动，私有配置只注入 HOME、XDG、遥测等变量，没有显式 PATH；工具链预检在独立环境通过，不能证明模型命令环境可找到工具。证据详见后续根因文档。
