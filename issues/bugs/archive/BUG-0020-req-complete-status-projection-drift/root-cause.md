---
bug_id: BUG-0020-req-complete-status-projection-drift
title: req.complete 后 REQ 状态投影残留 draft/enriching 导致数据漂移
status: confirmed
created_at: 2026-09-14 11:42:05
updated_at: 2026-09-14 11:42:05
---

# 根因分析

## 根因状态

status: confirmed

## 现象

`/req-complete` 的业务语义是将已生成 PRD 的 REQ 从 `draft` / `enriching` 推进到 `pending_review`，并通过 Workflow Sync 同步 `trace.md`、`issues/requirements/_registry.yaml`、`issues/requirements/CHANGELOG.md` 与需求中心当前态看板。

用户报告 REQ-0029 样本中，`/req-complete` 后状态投影出现残留旧值，需求中心显示“存在数据漂移”。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | code_path | `rules/requirement-management.md:91-94` | 规则定义 `/req-complete` 入口为 `draft, enriching`，产出为 `pending_review`。 | 证明目标状态应为 `pending_review`。 |
| E2 | code_path | `.agents/skills/req-complete/SKILL.md:88-95` | 技能说明要求 `status -> enriching -> 文档齐后 pending_review`。 | 证明命令执行链路应完成到待评审状态。 |
| E3 | code_path | `scripts/workflow_sync/engine.py:332-335` | `issue_event_targets` 仅包含 `req.generate -> draft` 和 `bug.generate -> draft`，缺少 `req.complete -> pending_review`。 | 证明 Workflow Sync 没有为 `req.complete` 建立聚焦事件目标态。 |
| E4 | reproduction | `python -c ... SyncEngine().run(event='req.complete')` | 内存受控 REQ 初始 `trace_status='draft'`，执行 `req.complete` 后捕获派生状态为 `['draft']`。 | 直接证明当前同步逻辑不会把聚焦 REQ 从 `draft` 推进到 `pending_review`。 |
| E5 | code_path | `tests/unit/test_workflow_sync_engine.py:134-177` | 现有单测覆盖 `req.generate` 推进到 `draft`，未见 `req.complete` 同类测试。 | 证明缺少防回归覆盖，解释该状态传播缺口为何未被测试拦截。 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| 需求中心前端单独误判 | 用户报告的漂移源包含 registry 与 CHANGELOG，且受控运行证明后端 Workflow Sync 派生状态未推进；前端只是消费投影结果。 |
| REQ-0029 文档缺失导致同步失败 | 当前 REQ-0029 文件态已恢复一致，且受控样本无需依赖 REQ-0029 文档内容也能复现 `req.complete` 不推进状态。 |
| Sprint 范围缺失导致状态不更新 | 受控运行和真实命令均在 `--sprint auto` 未解析 Sprint 时仍会同步 Issue 级 trace、registry、CHANGELOG；Sprint 跳过不是 Issue 级状态传播的阻断条件。 |

## 已确认根因

Workflow Sync 缺少 `req.complete` 聚焦事件目标态推进规则。当前 `SyncEngine` 只对 `req.generate` / `bug.generate` 明确覆盖目标状态，导致 `req.complete` 事件会沿用现有 `trace_status` 派生状态；当父命令执行期间或同步前后存在 `draft` / `enriching` 中间态时，registry、CHANGELOG 与需求中心当前态看板可能继续保留旧状态，形成数据漂移。

同时，现有测试只覆盖了 `req.generate -> draft`，未覆盖 `req.complete -> pending_review`，没有在回归层面固定该状态传播契约。

## 修复方向

- 在 Workflow Sync 聚焦事件目标表中补充 `req.complete -> pending_review`。
- 对 `bug.complete -> pending_review` 进行同域评估；若存在同样语义，补齐一致行为与测试，避免 BUG 流程复发。
- 补充单测覆盖 `req.complete` 事件下 trace、registry、CHANGELOG 使用 `pending_review` 派生状态。
- 使用 REQ-0029 或等价受控样本验证重复执行同步幂等，不制造重复变更记录或状态回退。

## 验证闭环

当前已完成根因确认；修复验证留待后续 OpenSpec Change 实施阶段执行。验收至少包含：

- `req.complete` 从 `draft` 推进到 `pending_review`。
- `req.complete` 从 `enriching` 推进到 `pending_review`。
- registry 与 CHANGELOG 的当前态行同步为 `pending_review`。
- 重复执行 `req.complete` 不重复写入无意义记录、不回退状态。
