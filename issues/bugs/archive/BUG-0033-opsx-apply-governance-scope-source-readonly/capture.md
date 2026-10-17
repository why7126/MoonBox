---
bug_id: BUG-0033-opsx-apply-governance-scope-source-readonly
title: 产品内执行 opsx-apply 误授治理写权限导致源码只读
status: done
created_at: 2026-10-06 22:22:15
updated_at: 2026-10-12 23:44:10
owner: 产品团队
source: 用户反馈与只读代码定位
lifecycle_stage: plan
environment: 产品内 Chat 工作台，具体部署环境待确认
related_requirement:
related_bug: BUG-0026-chat-platform-opsx-archive-source-permission
severity: high
---

# 产品内执行 opsx-apply 误授治理写权限导致源码只读

## 现象

用户反馈：产品内对已纳入 Sprint 的 Change 执行 `/opsx-apply` 时，执行器获得治理写权限，源码处于只读状态，阻断实现任务。

## 复现步骤

1. 在产品内打开已纳入 Sprint、已创建 OpenSpec Change 的 REQ 或 BUG 对象会话。
2. 发送该对象的 `/opsx-apply` 命令。
3. 核对该 turn 的 `write_scope`、权限 profile，并尝试在授权范围内修改 Change 对应的源码文件。
4. 记录脱敏的执行结果及失败信息；勿在仓库保存凭证或原始会话内容。

## 期望 vs 实际

- 期望：满足 Sprint 与 Change 门禁的 `/opsx-apply` 获得实现任务所需的源码写权限，同时遵守治理文件的写入边界。
- 实际：据用户反馈，该命令被授予治理写权限，源码只读；具体运行环境、目标 Change 和失败文件尚待核实。

## 影响范围与初判

- 影响产品内已纳入 Sprint 的 Change 开发执行；其他命令和部署模式的影响范围待核查。
- 严重度暂定 `high`：正式开发命令可能被阻断，未见数据损坏证据。
- 只读代码显示 `src/backend/app/chat/policy.py` 将满足 `_implementation_ready` 的对象授予 `implementation_write`，未满足时仍可回退到 `governance_write`；`src/backend/app/chat/app_server.py` 将两者分别映射到不同权限 profile。这为核查方向，不构成已确认根因。

## 附件与待补证

- 用户本次文字反馈；未提供截图、脱敏 turn 轨迹或失败日志。
- 后续需核对目标 Issue/Change/Sprint 的事实源、turn 权限决策原因、实际 profile、源码写入失败信息与产品部署模式。

## 相似项检查

- BUG-0026 记录 `/opsx-archive` 的归档目录权限与未知状态。本条聚焦 `/opsx-apply` 的实现写权限及源码只读，命令阶段和验收闭环不同；用户确认新建关联 BUG。
