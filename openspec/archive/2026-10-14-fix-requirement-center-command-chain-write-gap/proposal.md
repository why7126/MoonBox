---
title: 需求中心治理命令链真实写入修复
created_at: '2026-09-29 16:07:39'
updated_at: '2026-09-29 16:07:39'
---

# 需求中心治理命令链真实写入修复

## 背景与问题

需求中心看板已展示 Requirement、Bug、Sprint 与 OpenSpec 相关治理命令链，但产品内真实写入闭环目前只覆盖 `req-generate`。`bug-generate`、`complete`、`review`、`sprint-propose`、`opsx` 系列在产品界面中容易被理解为已经具备真实候选生成、确认应用和状态同步能力，实际仍停留在文案提示或 demo 模拟流转。

该偏差会导致用户在产品里点击 Bug Generate 后没有生成可应用的 `bug.md`，也不会产生治理候选和应用记录；未接入的命令还可能被前端展示为执行成功，使看板临时状态与 `trace.md`、registry、CHANGELOG、Sprint 和 OpenSpec 事实源不一致。

## 变更目标

- 将产品内命令能力矩阵显式化，区分真实候选写入、真实应用写入、demo 模拟和仅展示状态。
- 将 `bug-generate` 接入与 `req-generate` 同级的治理准备、候选、应用和状态同步链路。
- 对尚未接入真实写入链路的 `complete`、`review`、`sprint-propose`、`opsx` 系列动作给出明确不可执行提示，不再在非 demo 路径模拟成功。
- 保持 `req-generate` 现有真实链路不回退。

## 能力影响

- 需求中心前台阶段动作需要展示真实能力状态，并在不支持时引导用户使用对应 Codex 命令。
- 本地项目治理闭环需要允许 `BUG-*` 对象和 `bug-generate` action 生成候选，且只允许写入目标 BUG 文档集合。
- API、OpenAPI、前端客户端类型、测试与产品手册应随实际字段变化同步；如仅扩展既有枚举，也必须同步 API 文档和回归说明。

## 观测与边界

`product_data_collection_observability` 适用。受影响层包括 Web、API、governance candidate/application、request_logs、usage_events、task_traces 和 task_trace_spans。治理准备、候选应用与恢复仍不得记录 Markdown 正文、凭证、本机绝对路径或堆栈；直接 API 不伪造页面行为。

## 非目标

- 本 Change 不在提案阶段直接实现 `bug-complete`、`bug-review`、`sprint-propose`、`bug-opsx` 或 `opsx-apply` 的产品真实写入链路。
- 本 Change 不改变 Codex CLI 技能命令的既有事实源；产品内写入链路必须以受控 API、候选和应用记录为准。
