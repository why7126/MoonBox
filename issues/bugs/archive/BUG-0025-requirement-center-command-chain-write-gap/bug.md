---
bug_id: BUG-0025-requirement-center-command-chain-write-gap
title: 需求中心看板展示完整治理命令链但多数命令未接入真实写入
status: done
owner: user_f694abc671d548b48d9eb897f720ba4d
discovered_at: '2026-09-16 23:49:40'
environment: MoonBox Web 需求中心；本地项目治理仓库；非 demo 产品链路
related_requirement: null
related_change: null
created_at: 2026-09-29 15:55:09
updated_at: 2026-10-14 17:43:05
severity: medium
---

# 需求中心看板展示完整治理命令链但多数命令未接入真实写入

## 现象

需求中心看板展示了完整治理命令链，但产品内目前只有采集池需求的 `/req-generate` 具备真实治理候选、应用和事实源写入链路。

`/bug-generate`、`/req-complete`、`/bug-complete`、`/req-review`、`/bug-review`、`/sprint-propose`、`/req-opsx`、`/bug-opsx`、`/opsx-apply`、`/opsx-archive` 等命令在看板、弹窗或 action hint 中可见，但未形成等价的产品内真实执行链路。

## 复现

1. 打开需求中心看板，查看各阶段卡片或阶段标题展示的命令链。
2. 在非 demo 产品链路中对非采集池需求生成动作，或对 BUG / complete / review / sprint / opsx 类动作尝试执行。
3. 观察产品行为是否进入对应治理候选、应用、文件写入和阶段同步流程。

## 期望结果

产品中展示的可执行治理命令应与真实能力一致：

- 已实现的命令应进入受控治理链路，生成候选、校验写入边界、应用文件变更，并同步 trace、registry、CHANGELOG 和阶段投影。
- 未实现的命令不应表现为可执行成功，至少应明确提示“尚未接入产品写入链路”。
- BUG 生成类动作应像 `/req-generate` 一样，能够生成 `bug.md` 并推进到规划中 / draft 投影。

## 实际结果

当前产品链路中，`/api/v1/chat/governance-preparations` 仅支持 `REQ-*` 的 `req-generate`。前端非 demo 分支也仅允许采集池需求调用该接口；其他命令更多停留在展示、普通 Chat 回复或前端模拟流转层面。

这会造成用户看到完整治理命令链后，误以为点击或进入 Chat 可以像 Codex 命令一样生成文档、推进阶段并写入事实源。

## 影响范围

- 需求中心看板的命令可信度受影响：展示的命令能力与真实产品写入能力不一致。
- BUG 链路受影响：`bug-generate` 不能通过产品内路径生成 `bug.md` 并进入 draft 投影。
- 后续治理动作受影响：complete、review、sprint-propose、opsx 系列在产品上缺少端到端执行链路，容易产生“看起来执行了、事实源未变”的误判。

## 严重等级说明

严重等级暂定为 `medium`。该问题不直接破坏已有文件或运行时服务，但会导致需求中心用户对治理状态、命令可执行性和事实源写入结果形成错误预期，影响产品内 Agent Workflow 的可信度。
