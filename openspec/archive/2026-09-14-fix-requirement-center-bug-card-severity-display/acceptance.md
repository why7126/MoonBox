---
change_id: fix-requirement-center-bug-card-severity-display
source_bug: BUG-0021-requirement-center-bug-card-severity-display
acceptance_status: passed
created_at: 2026-09-14 14:12:36
updated_at: 2026-09-14 14:38:53
---

# 验收标准

## AC-001 BUG 卡片显示严重性

BUG 事实源为 `severity: medium` 时，需求中心 BUG 卡片显示 `medium` 或产品确认的中文映射“中”，不得显示 `P2`。

## AC-002 REQ 卡片显示优先级

REQ 事实源为 `priority: P0|P1|P2|P3` 时，需求中心 REQ 卡片继续显示对应 P 值。

## AC-003 API 字段不混用

需求中心上下文 API 中，REQ 数据使用 `priority`，BUG 数据使用 `severity`；BUG 不得因缺少 `priority` 被默认投影为 `P2`。

## AC-004 缺失或非法分级可诊断

当 BUG 活动事实源缺失或包含非法 `severity` 时，同步或构卡链路提供可诊断提示，不静默猜测默认 P 值。

## AC-005 测试覆盖

后端 API / 构卡测试和前端卡片测试覆盖 REQ/BUG 分级差异。

## AC-006 分级标签按等级区分颜色

需求中心卡片中，REQ `priority` 的 `P0`、`P1`、`P2`、`P3` 标签应按等级呈现可区分颜色；BUG `severity` 的 `blocker`、`critical`、`high`、`medium`、`low` 标签应按严重性呈现可区分颜色。

## AC-007 非目标范围不回退

独立 Change 卡片、文档入口排序、负责人标签、Sprint 标签和任务进度展示不回退。

## 验收结果

| AC | 结果 | 证据 |
|---|---|---|
| AC-001 | pass | `src/web/src/requirement-center.test.tsx` 新增 BUG 同时带旧 `priority: P2` 与 `severity: medium` 时仅显示 `medium` 的回归测试；`./node_modules/.bin/vitest --run src/requirement-center.test.tsx` 80 passed。 |
| AC-002 | pass | 同一前端回归测试断言 REQ 卡片继续显示 `P0`；Vitest 80 passed。 |
| AC-003 | pass | `src/backend/app/schemas/requirement_center.py` 增加 `severity`；`src/backend/app/services/requirement_center.py` 按类型分流；`uv run pytest src/backend/tests/test_governance_board.py tests/integration/api/test_requirement_center.py -q` 87 passed。 |
| AC-004 | pass | `test_bug_card_classification_does_not_default_to_priority` 覆盖 BUG 缺失/非法 `severity` 时 `priority == ""` 且输出 drift warning。 |
| AC-005 | pass | 后端 board/API 聚焦测试 87 passed；前端 requirement-center 测试 80 passed；TypeScript `./node_modules/.bin/tsc --noEmit` 通过。 |
| AC-006 | pass | `/opsx-modify` 返修中补充 `.rc-priority-tag.p0/.p1/.p2/.p3` 与 `.rc-severity-tag.blocker/.critical/.high/.medium/.low` 样式，并由前端静态样式测试覆盖各等级 token 映射。 |
| AC-007 | pass | 前端既有 9 阶段、文档入口、独立 Change、action modal、任务/验收进度回归测试全部通过。 |

## 不适用与边界

- DB schema、对象存储、部署拓扑、权限、行为埋点、usage_events、Task Trace 不变。
- `request_logs` 仅受既有需求中心上下文 API 响应字段变化影响；未新增请求日志字段。
- 复用经验已纳入本 Change 证据，后续可在 Sprint 复盘中归纳，不新增单独 incident 文档。
