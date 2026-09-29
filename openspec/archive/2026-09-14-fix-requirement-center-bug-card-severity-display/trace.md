---
change_id: fix-requirement-center-bug-card-severity-display
type: fix
status: applied
source_bug: BUG-0021-requirement-center-bug-card-severity-display
sprint: sprint-006
owner: 产品团队
created_at: 2026-09-14 14:12:36
updated_at: 2026-09-14 14:41:04
product_data_collection_observability:
  status: applicable
  affected_layers:
    - request_logs
  reason: 涉及需求中心上下文 API 响应字段与 Web 卡片展示契约；不新增 DB、usage_events、Task Trace、对象存储或部署拓扑。
  validation: 已通过后端 board/API 测试、前端卡片与样式测试、TypeScript 检查和 OpenAPI/Orval 生成复核，确认 priority/severity 响应字段不混用，且未新增请求日志字段或 Task Trace 落地需求。
execution:
  schema_version: 1
  started_at: 2026-09-14 14:16:56
  completed_at: 2026-09-14 14:41:04
  last_event: opsx.modify
---

# fix-requirement-center-bug-card-severity-display Trace

## 追溯

| 字段 | 值 |
|---|---|
| Source BUG | BUG-0021-requirement-center-bug-card-severity-display |
| Sprint | sprint-006 |
| 类型 | fix |
| 状态 | applied |

## 证据入口

- `issues/bugs/review/BUG-0021-requirement-center-bug-card-severity-display/root-cause.md`
- `issues/bugs/review/BUG-0021-requirement-center-bug-card-severity-display/acceptance.md`
- `rules/document-governance.md#issue-分级元数据`
- `openspec/specs/web-catalog-requirement-center/spec.md`
- `openspec/specs/issue-classification-metadata/spec.md`
- `src/backend/app/schemas/requirement_center.py`：`RequirementCenterIssue` 增加 `severity`，移除 BUG 被默认表达为 `priority: P2` 的 schema 默认。
- `src/backend/app/services/requirement_center.py`：REQ/BUG 分级字段按类型分流，BUG 缺失或非法 `severity` 输出 drift warning。
- `src/web/src/pages/catalog/RequirementCenterPage.tsx`：卡片分级标签按 `issue.type` 展示 `priority` 或 `severity`，并携带等级值 class 供样式区分。
- `src/web/src/styles/globals.css`：REQ `priority` 与 BUG `severity` 标签按等级值设置可区分颜色。
- `src/web/openapi.json` 与 `src/web/src/api/generated/governance.ts`：已重新导出 OpenAPI 并通过本地 Orval 生成，`RequirementCenterIssue` 包含 `severity`。

## 验证记录

| 时间 | 命令 | 结果 |
|---|---|---|
| 2026-09-14 14:20 | `uv run pytest src/backend/tests/test_governance_board.py -q` | 首轮发现旧 BUG fixture 缺少 `severity`，已按新契约修正。 |
| 2026-09-14 14:21 | `uv run pytest src/backend/tests/test_governance_board.py -q` | pass，71 passed。 |
| 2026-09-14 14:21 | `./node_modules/.bin/vitest --run src/requirement-center.test.tsx` | pass，80 passed。 |
| 2026-09-14 14:22 | `cd src/backend && uv run python -c "import json; from app.main import app; print(json.dumps(app.openapi(), ensure_ascii=False, indent=2))" > ../web/openapi.json` | pass，OpenAPI 已导出。 |
| 2026-09-14 14:22 | `./node_modules/.bin/orval --config orval.config.ts` | pass，governance/chat client 已生成。 |
| 2026-09-14 14:22 | `uv run pytest src/backend/tests/test_governance_board.py tests/integration/api/test_requirement_center.py -q` | pass，87 passed。 |
| 2026-09-14 14:23 | `./node_modules/.bin/tsc --noEmit` | pass。 |
| 2026-09-14 14:23 | `./node_modules/.bin/vitest --run src/requirement-center.test.tsx` | pass，80 passed。 |
| 2026-09-14 14:40 | `./node_modules/.bin/vitest --run src/requirement-center.test.tsx` | pass，80 passed。 |
| 2026-09-14 14:40 | `./node_modules/.bin/tsc --noEmit` | pass。 |
| 2026-09-14 14:40 | `openspec validate fix-requirement-center-bug-card-severity-display --strict` | pass。 |
| 2026-09-14 14:40 | `python scripts/validate-openspec-language.py` | pass。 |
| 2026-09-14 14:40 | `python scripts/validate-root-cause-evidence.py --bug BUG-0021-requirement-center-bug-card-severity-display` | pass。 |
| 2026-09-14 14:40 | `python scripts/validate-sprint-scope.py sprint-006 --item BUG-0021-requirement-center-bug-card-severity-display` | pass。 |
| 2026-09-14 14:40 | `python scripts/validate-product-data-observability.py --change fix-requirement-center-bug-card-severity-display` | pass。 |
| 2026-09-14 14:40 | `git diff --check -- <本次返修相关文件>` | pass。 |
| 2026-09-14 14:40 | `python scripts/sync-workflow-status.py --event opsx.modify --change fix-requirement-center-bug-card-severity-display --sprint auto` | pass，Updated 2，Errors 0；BUG acceptance 仍为 pending。 |

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-14 14:38:53 | /opsx-modify BUG-0021-requirement-center-bug-card-severity-display | 为 BUG severity 和 REQ priority 标签增加按等级区分的颜色，并补充前端样式测试。 |
| 2026-09-14 14:24:00 | /opsx-apply BUG-0021-requirement-center-bug-card-severity-display | 完成 BUG severity 卡片展示修复、OpenAPI/Orval 生成与聚焦验证。 |
| 2026-09-14 14:12:36 | /bug-opsx BUG-0021-requirement-center-bug-card-severity-display | 创建 BUG 来源 OpenSpec fix Change。 |
