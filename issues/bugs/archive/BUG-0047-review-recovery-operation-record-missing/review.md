---
bug_id: BUG-0047-review-recovery-operation-record-missing
title: 评审恢复记录缺失导致成果未应用与卡片未流转评审记录
result: approved
created_at: '2026-10-19 14:30:30'
updated_at: '2026-10-19 14:30:30'
reviewer: 用户明确批准；AI 辅助核对
decision_source: 本会话 /bug-review --approve
---

# 评审恢复记录缺失导致成果未应用与卡片未流转评审记录

## 评审结论

批准修复，保留 high，采用常规 Sprint/OpenSpec 路径。根因 confirmed，10 项可复核证据及实际部署函数的隔离复现足以支持修复评审；9 项验收标准明确。无已证实的数据丢失或全站不可用，不采用绕过流程的 hotfix。

## 评审依据

- 部署 backend 与 worker 的动作名单均缺少 req-review，prepare 静默跳过 operation，而收尾强制读取；真实部署函数在隔离目录复现 direct_command_recovery_blocked。
- 工作区名单扩展不等于部署修复完成，需检查覆盖、版本和历史基线兼容，避免重复实现已有改动。
- 验收覆盖正常评审、缺失/损坏记录、重启与历史兼容、幂等恢复、并发与权限、准确诊断、部署和关联回归；全部仍未执行。

## 修复边界

聚焦记录初始化、预检、收尾契约及本故障诊断；不补空 operation、不跳过验证、不强改原失败轮次。历史成果应用需重新核对归属、基线、权限和当前版本。

通用持久化阶段与恢复能力增量归属 REQ-0047-governance-command-durable-recovery；展示优化归属 REQ-0046-chat-execution-output-status-feedback；复用 BUG-0044 的完成门禁与互斥。本次批准不代表已修复、验收通过或发布，不授权自动执行生产恢复。

## 数据采集与链路观测

product_data_collection_observability: applicable

affected_layers: API、请求日志、Task Trace、轮次/候选/应用、Web 状态关联。

validation: 后续按 acceptance.md 验证原始错误、阶段与操作版本关联。当前仅评审和生命周期同步，不改变 API、DB、UI、安全、部署、对象存储或客户端生成物；这些实现变更本轮 N/A。

## 后续链路

先执行 /sprint-propose --bug BUG-0047-review-recovery-operation-record-missing，纳入 Sprint 后再生成对应 OpenSpec。当前无 Sprint、无 Change，不自动推进开发。
