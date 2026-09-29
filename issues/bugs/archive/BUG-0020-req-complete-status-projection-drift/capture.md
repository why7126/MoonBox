---
bug_id: BUG-0020-req-complete-status-projection-drift
title: req.complete 后 REQ 状态投影残留 draft/enriching 导致数据漂移
status: done
created_at: '2026-09-14 11:33:24'
updated_at: 2026-09-14 13:12:02
related_requirement: REQ-0029-capture-multimodal-candidate-review
related_bug: null
environment: local
severity: medium
---

# 现象

执行 `/req-complete` 后，REQ 状态投影可能残留 `draft` / `enriching` 等旧状态，导致需求中心卡片提示“存在数据漂移”。

以 REQ-0029 为例：`trace.md` 已为 `enriching`，但 `issues/requirements/_registry.yaml` 与 `issues/requirements/CHANGELOG.md` 仍为 `draft`，需求中心当前态卡片据此显示数据漂移。

严重度初判 medium：该问题影响需求治理事实源一致性、需求中心当前态判断和后续评审前检查；当前未见生产数据丢失、权限越界或核心功能不可用证据。

# 复现步骤

1. 对一个已生成 `requirement.md` 的 REQ 执行 `/req-complete`。
2. 对比该 REQ 的 `trace.md`、`issues/requirements/_registry.yaml`、`issues/requirements/CHANGELOG.md` 与需求中心当前态卡片。
3. 观察是否出现 `trace.md` 已推进，但 registry、CHANGELOG 或当前态看板仍保留 `draft` / `enriching` 旧状态。
4. 用户报告样本：REQ-0029 的 `trace.md` 为 `enriching`，registry 和 CHANGELOG 仍为 `draft`，需求中心卡片显示“存在数据漂移”。

# 期望 vs 实际

| 项目 | 期望 | 实际 |
|---|---|---|
| `/req-complete` 状态传播 | `trace.md`、registry、CHANGELOG 和需求中心当前态看板状态一致 | REQ-0029 样本中状态投影残留旧值 |
| 漂移提示 | 完成状态同步后不误报数据漂移 | 当前态卡片显示“存在数据漂移” |
| 回归覆盖 | 有 check / 回归用例覆盖 `req.complete` 状态传播 | 用户反馈缺少覆盖或覆盖不足 |

# 建议验收

- 补充 check 或回归用例覆盖 `/req-complete` 后 `trace.md`、`issues/requirements/_registry.yaml`、`issues/requirements/CHANGELOG.md` 与需求中心当前态看板一致。
- 使用 REQ-0029 或等价受控样本验证 `draft -> enriching -> pending_review` 传播链路。
- 验证 `req.complete` 成功路径会刷新 CHANGELOG 当前态行，且需求中心不再误报数据漂移。
- 验证同步逻辑幂等：重复执行不会制造重复变更记录或错误回退状态。

# 附件

无新增截图或日志附件。证据来自用户对 REQ-0029 的状态差异描述；后续 `/bug-explore` 需要读取聚焦 REQ 文件和同步脚本输出补证。
