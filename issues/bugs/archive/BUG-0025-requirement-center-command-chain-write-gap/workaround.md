---
bug_id: BUG-0025-requirement-center-command-chain-write-gap
title: 需求中心看板治理命令真实写入链路缺口临时规避
status: active
created_at: 2026-09-29 15:56:27
updated_at: 2026-09-29 15:56:27
owner: user_f694abc671d548b48d9eb897f720ba4d
---

# 需求中心看板治理命令真实写入链路缺口临时规避

## 可用规避

在正式修复前，不要把需求中心看板中展示的完整命令链视为都已经具备产品内真实写入能力。

临时处理方式：

1. 只有采集池需求的 `/req-generate` 可按产品内治理候选与应用链路处理。
2. BUG 生成、complete、review、sprint-propose 和 opsx 系列仍通过 Codex 命令执行。
3. 执行 Codex 命令后，以目标 Issue 的 `trace.md`、`_registry.yaml` 和 CHANGELOG 行作为事实源确认状态。
4. 如果产品内 Chat 只返回普通说明，且没有 governance candidate / application 记录，不视为已完成治理写入。
5. 看板上未真实接入的动作应人工标记为“需 Codex 命令执行”或在操作说明中提示用户。

## 限制

- 该规避依赖人工区分产品链路与 Codex 命令链路，仍可能让用户误判。
- 不能替代正式修复，也不能保证产品 UI 与事实源状态天然一致。
- 对 BUG 链路，产品内点击 Bug Generate 仍不能自动生成 `bug.md`。

## 解除条件

完成正式修复并通过回归验收后解除。解除前至少需要确认：

- `/bug-generate` 已具备真实治理候选与应用写入链路。
- 未接入的命令在 UI 中不再表现为可执行成功。
- 完整命令能力矩阵已在产品或治理文档中明确。
