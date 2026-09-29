---
change_id: fix-req-complete-status-projection-drift
created_at: 2026-09-14 12:04:16
updated_at: 2026-09-14 12:04:16
source_bug: BUG-0020-req-complete-status-projection-drift
---

# Design

## 根因归纳

`scripts/workflow_sync/engine.py` 已为部分聚焦事件维护 `issue_event_targets`，例如 `req.generate` 固定派生到 `draft`。`req.complete` 不在该映射中，因此同步时会从 trace/registry 读取现存状态作为派生基础。若历史状态停留在 `draft` 或 `enriching`，完成事件不会把投影推进到 `pending_review`，随后 registry、CHANGELOG 与当前态看板继续消费旧状态并形成漂移。

## 设计原则

- 完成事件必须是状态推进事件，而不是简单刷新事件。
- 聚焦 REQ ID 是唯一作用边界，避免批量刷新误改其他 Issue。
- 派生态由 Workflow Sync 统一产出，后续投影只消费同一份当前态。
- 回归测试必须覆盖历史中间态，避免只验证理想路径。

## 技术方案

### 1. 聚焦事件目标状态

在 Workflow Sync 的聚焦事件目标表中新增：

- `req.complete` + REQ ID -> `pending_review`

状态推进需要允许旧态为 `draft` 或 `enriching` 的记录被刷新到目标态；若记录已经是 `pending_review`，重复同步保持幂等。

### 2. 生命周期字段

`req.complete` 成功传播时，trace lifecycle 应记录完成阶段结果，至少保证以下字段与既有结构一致：

- 当前状态为 `pending_review`
- 完成阶段时间或阶段标记可被后续 review/sprint 命令识别
- CHANGELOG 的 next action 指向 `/req-review <REQ-full-id>`

### 3. 投影刷新顺序

同步时保持单一派生态来源：

1. 解析聚焦 REQ。
2. 将事件目标状态派生为 `pending_review`。
3. 写回 trace。
4. 刷新 registry。
5. 刷新 CHANGELOG。
6. 刷新当前态看板。

### 4. 回归覆盖

新增或扩展 Workflow Sync 单元测试：

- `req.complete` 从 `draft` 推进到 `pending_review`
- `req.complete` 从 `enriching` 推进到 `pending_review`
- registry、CHANGELOG 与当前态看板消费同一派生态
- 重复执行 `req.complete` 保持幂等，不产生回退

## 风险与回滚

- 风险：若历史 REQ 文档缺少必要 trace 片段，状态推进可能无法定位目标文件。测试应覆盖最小 trace 结构，实际命令失败时保留可诊断错误。
- 回滚：移除 `req.complete` 聚焦事件目标状态映射和新增测试即可恢复旧行为；已生成文档投影可通过重新运行 Workflow Sync 修正。

