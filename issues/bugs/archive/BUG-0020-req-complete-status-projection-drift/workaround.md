---
bug_id: BUG-0020-req-complete-status-projection-drift
title: req.complete 后 REQ 状态投影残留 draft/enriching 导致数据漂移
status: available
created_at: 2026-09-14 11:42:05
updated_at: 2026-09-14 11:42:05
---

# 临时规避

## 可用规避

在正式修复前，执行 `/req-complete` 后若发现需求中心显示“存在数据漂移”，先不要直接进入 `/req-review`。按以下步骤人工收敛当前态：

1. 聚焦目标 REQ，检查 `trace.md`、`issues/requirements/_registry.yaml`、`issues/requirements/CHANGELOG.md` 的状态是否一致。
2. 确认六件套已经补齐，且按规则应进入 `pending_review`。
3. 重新运行聚焦同步：

```bash
python scripts/sync-workflow-status.py --event req.complete --req <REQ-full-id> --sprint auto --output detail
```

4. 若同步后仍停留旧值，暂缓评审，按缺陷链路推进本 BUG 修复；不要手工编辑 Workflow Sync marker 块。

## 限制

- 该规避不能从根上补齐 `req.complete -> pending_review` 的事件目标态。
- 如果父命令未正确写入 `trace.md` 状态，单纯重跑同步可能仍沿用旧状态。
- 不建议通过手工改 registry 或 CHANGELOG 作为长期方案；这会绕过事实源与派生链路。

## 回滚

规避动作不涉及代码变更。若手工检查发现同步结果不符合事实源，应停止推进评审，并保留命令摘要给后续修复验证使用。
