---
bug_id: BUG-0020-req-complete-status-projection-drift
title: req.complete 后 REQ 状态投影残留 draft/enriching 导致数据漂移
status: done
owner: 产品团队
discovered_at: '2026-09-14 11:33:24'
environment: local
related_requirement: REQ-0029-capture-multimodal-candidate-review
related_change: null
created_at: 2026-09-14 11:38:08
updated_at: 2026-09-14 13:11:57
severity: medium
---

# 现象

执行 `/req-complete` 后，REQ 状态投影可能残留 `draft` / `enriching` 等旧状态，导致需求中心当前态卡片提示“存在数据漂移”。

用户报告样本为 REQ-0029：`trace.md` 已进入后续状态，但 `issues/requirements/_registry.yaml` 与 `issues/requirements/CHANGELOG.md` 仍显示旧状态，需求中心据此判断当前态看板与事实源不一致。

# 复现步骤

1. 准备一个已执行 `/req-generate`、状态为 `draft` 的 REQ。
2. 执行 `/req-complete <REQ-full-id>`，并触发 `python scripts/sync-workflow-status.py --event req.complete --req <REQ-full-id> --sprint auto`。
3. 对比该 REQ 的 `trace.md`、`issues/requirements/_registry.yaml`、`issues/requirements/CHANGELOG.md` 与需求中心当前态卡片。
4. 观察是否出现 `trace.md` 与 registry / CHANGELOG / 当前态看板不一致，或状态仍残留 `draft` / `enriching`。

# 期望 vs 实际

| 项目 | 期望 | 实际 |
|---|---|---|
| `/req-complete` 状态传播 | `trace.md`、registry、CHANGELOG 和需求中心当前态看板一致推进到 `pending_review` | 用户报告 REQ-0029 出现状态投影残留旧值 |
| 需求中心漂移判断 | 完成同步后不误报数据漂移 | 卡片显示“存在数据漂移” |
| 回归覆盖 | 有 check / 单测覆盖 `req.complete -> pending_review` 状态传播 | 探索时仅发现 `req.generate -> draft` 的聚焦事件覆盖，未发现 `req.complete` 同类覆盖 |

# 影响范围

- 需求治理状态投影：`trace.md`、`issues/requirements/_registry.yaml`、`issues/requirements/CHANGELOG.md`。
- 需求中心当前态卡片：可能显示数据漂移或错误下一步。
- `/req-review` 前检查：可能因为状态不一致导致人工误判或额外返工。
- Workflow Sync 回归质量：`req.complete` 成功路径缺少明确回归用例时，后续类似事件可能复发。

# 严重等级说明

严重等级为 medium。

该问题影响需求治理事实源一致性、需求中心状态判断和评审前工作流体验；当前未发现生产数据丢失、权限越界、真实客户数据泄漏或核心业务不可用证据。

# 探索结论

当前工作区中 REQ-0029 已恢复为一致的 `pending_review` 状态，原始漂移无法直接从现有文件态复现。只读探索发现 Workflow Sync 代码中已有 `req.generate` / `bug.generate` 聚焦事件目标态推进到 `draft` 的逻辑，但尚未确认存在 `req.complete -> pending_review` 的同类推进和单测覆盖。

根因状态暂定为 `probable`：疑似 Workflow Sync 对 `req.complete` 缺少聚焦事件目标态推进与回归测试，导致状态传播依赖父命令写入 trace；一旦中间态或派生刷新顺序不一致，就可能留下 registry / CHANGELOG 漂移。正式根因需在 `/bug-complete` 中用受控测试失败或最小复现样本确认。

# 建议验收

- 补充 `req.complete -> pending_review` 的 Workflow Sync 单测，覆盖 trace、registry、CHANGELOG 派生刷新。
- 使用 REQ-0029 或等价受控样本验证 `draft -> enriching -> pending_review` 链路。
- 验证 `bug.generate` 与后续 BUG 流程不受影响。
- 验证重复执行 `req.complete` 同步保持幂等，不制造重复变更记录或状态回退。
