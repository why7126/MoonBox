---
title: 历史归档验收样本状态兼容提案
created_at: 2026-10-17 17:00:00
updated_at: 2026-10-17 17:00:00
---
# 历史归档验收样本状态兼容提案

## 背景

sprint-009 关闭时，Workflow Sync 读取已归档 Change 的验收计划，AC-005 `required_sample.status` 为历史值 `completed-source-archive`，当前校验仅允许 `passed`、`partial`、`pending`，导致 `sprint.archive` 失败。原归档证据不得直接改写。

## 变更内容

只读兼容已归档计划中的该历史值，保留原始计划与 manifest；依据既有通过证据决定投影，绝不因为历史状态文字自动签认。

## 能力范围

### 修改能力

- `automated-opsx-acceptance`：历史归档计划读取兼容与证据门禁。

## 影响

影响 `scripts/opsx_acceptance.py` 的计划读取、Workflow Sync 验收投影及聚焦测试。API、DB、请求日志、行为事件、Task Trace 和客户端请求封装不变，产品数据采集与链路观测不适用。
