---
bug_id: BUG-0034-chat-standalone-archive-scope-tool-path
title: 产品内纯治理 Change 归档因权限与命令路径缺失失败
status: done
created_at: 2026-10-09 10:50:49
updated_at: 2026-10-13 18:51:16
owner: 产品团队
source: 用户截图与本地执行轮次只读取证
lifecycle_stage: plan
environment: local docker chat-platform
related_requirement:
related_bug: BUG-0026-chat-platform-opsx-archive-source-permission
severity: high
---

# 产品内纯治理 Change 归档因权限与命令路径缺失失败

## 现象

在纯治理 Change 对象会话发送 `/opsx-archive prevent-issue-iteration-tool-dirs` 后，轮次完成但归档被阻断。输出称规格和归档目录不可写、Node/OpenSpec 不可用。

## 复现步骤

1. 在本地 Chat 工作台打开已 applied 的纯治理 Change 对象会话。
2. 发送 `/opsx-archive prevent-issue-iteration-tool-dirs`。
3. 检查该轮权限决策、命令退出码、Change active/archive 路径和最终回复。

## 期望与实际

- 期望：经成员、对象和 Change 状态校验后，归档命令使用最小归档权限，命令沙箱能找到镜像内置工具，并完成标准脚本闭环。
- 实际：服务端下发 `governance_write / moonbox-governance`；工具调用分别出现 `cat: command not found` 与 `env: node: No such file or directory`。模型因此停止归档，Change 保持 applied。

## 影响范围与相似项检查

影响本地 Chat 工作台中以纯治理 Change 为主对象的产品内归档。BUG-0026 已覆盖 REQ/BUG 来源归档，但其 proposal 和验收范围限定完整 REQ/BUG ID；本条补充独立的纯治理对象权限和命令 PATH 修复，关联原 BUG，不重复原交付范围。两处偏差由同一归档命令触发，需在一次产品内归档验收中共同闭环，因此记录为一条缺陷。
